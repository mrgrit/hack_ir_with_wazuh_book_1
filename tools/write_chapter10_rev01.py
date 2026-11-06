"""REV01 · 10장 네트워크 흔적과 현재 상태 조사. 저자용이며 실습 명령을 실행하지 않는다.

2026-11-06 개정 기준
- 조사 질문: 이 서버에서 무엇이 연결을 기다리고 있고, 누가 두드렸는가. 실습 29·30·62를 같은 변화가 기록마다
  다른 시각(auditd·osquery·netstat)과 다른 수(Nmap·LOG·archives·alerts)로 남는다는 관점으로 묶는다.
- 결과 값·화면은 2026-11-03 실제 kt66 실행 기록(editorial/evidence/chapter10/2026-11-03, kt66 .107 · 공격자 .108)이다.
- 기록 환경은 host-sensors 구성이 일부 빠져 있어 저자가 수동으로 보완했다. 본문은 kt66.sh up이 매번 실행하는
  deployment/host-sensors.sh가 만든 상태(osquery 모듈, kern.log 수집, kt66-perimeter)를 전제로 확인만 하고,
  빠졌을 때 그 스크립트를 다시 실행하게 했다. 수동 보완·제거 절차는 옮기지 않았다.
- 공개 키는 기록과 달리 kt66 VM에서 만든다(scp 생략). 기록 값은 주석(book10-key@attacker)을 그대로 인용한다.
- LOG 상한 계산(200 + 100×4.9초)은 perimeter.sh의 limit 값과 Nmap 실행 시간으로 계산한 상한이다.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/REV01'
EX=ROOT/'examples/rev01/chapter10'
COMMIT='63d4180b1d6866de986ef263a3bd831d6082b5d5'
KT66='https://github.com/mrgrit/kt66/blob/'+COMMIT
WZ='https://github.com/wazuh/wazuh/blob/v4.10.0/ruleset'
pages=[];commands=[];queries=[]

def p(t): return {'type':'p','text':t}
def h(t): return {'type':'h','text':t}
def ul(*items): return {'type':'list','items':list(items)}
def ol(*items): return {'type':'list','style':'number','items':list(items)}
def tab(head,rows,widths=None,keep=False):
    b={'type':'table','head':head,'rows':rows,'widths':widths}
    if keep:b['keep']=True
    return b
def img(path,caption,width=127): return {'type':'image','path':path,'caption':caption,'width_mm':width}
def screen(name,caption,width=90): return img(f'assets/screens/chapter10/{name}.png',caption,width)
def box(kind,*text): return {'type':'box','kind':kind,'text':list(text)}
def code(t): return {'type':'code','text':t}
def link(text,url): return {'type':'link','text':text,'url':url}
HOST='kt66 VM · 터미널';HOSTA='kt66 VM · 터미널 A';HOSTC='kt66 VM · 터미널 C';ATT='공격자 VM · 터미널'
SIEM='kt66-siem 컨테이너 · 셸';OSQ='kt66 VM · osquery> 프롬프트'
def c(text,purpose,syntax,result,where):
    b={'type':'command','id':f'C10-{len(commands)+1:02d}','where':where,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    commands.append(b);return b
def q(text,purpose,syntax,result,index='wazuh-alerts-*',qid=None,where=None):
    n=len([x for x in queries if x['id'].startswith('Q')])+1
    b={'type':'query','id':qid or f'Q10-{n:02d}','where':where or 'Windows · Discover · '+index,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    queries.append(b);return b
def page(title,*blocks,brk=True,level='page'):
    pg={'title':title,'kind':'body','blocks':list(blocks)}
    if not brk:pg['break']=False
    if level!='page':pg['level']=level
    pages.append(pg)
def section(title,*blocks):page(title,*blocks,brk=False,level='section')
FIG='assets/figures/chapter10/'
KT='192.168.0.189';AT='192.168.0.202'
SQL1='SELECT p.pid, p.name, p.path, l.address, l.port\nFROM listening_ports l\nJOIN processes p USING (pid)\nWHERE l.port IN (31337, 31338);'
DEVTOOLS='''GET wazuh-archives-*/_search
{
  "size": 0,
  "query": {"bool": {"filter": [
    {"term": {"agent.name": "kt66-host"}},
    {"term": {"data.srcip": "192.168.0.202"}},
    {"term": {"data.action": "DROP"}},
    {"range": {"timestamp": {"gte": "now-1h"}}}
  ]}},
  "aggs": {
    "ports": {"cardinality": {"field": "data.dstport"}},
    "first": {"min": {"field": "timestamp"}},
    "last": {"max": {"field": "timestamp"}}
  }
}'''

# ── 장 도입 ───────────────────────────────────────────────────
page('10장  네트워크 흔적과 현재 상태 조사',
    p('9장까지는 무엇이 실행되고 무엇이 바뀌었는지를 조사했다. 이번에는 서버의 바깥쪽 상태를 본다. 지금 이 서버에서 어떤 프로그램이 연결을 기다리고 있는가. 그리고 누가 밖에서 이 서버의 포트를 두드렸는가. 공격자가 남긴 수신 대기 프로그램은 다시 들어올 입구가 되고, 포트 스캔은 공격 전에 입구를 찾는 단계이다.'),
    p('세 가지 기록을 쓴다. 호스트 안에서 소켓과 프로세스를 보는 기록(auditd, osquery, netstat 명령 모니터링), 방화벽이 버린 패킷의 기록(kern.log), 그리고 이들을 모은 Wazuh 경보·아카이브이다. 같은 변화가 기록마다 다른 시각에, 다른 수로 남는다는 점이 이 장의 분석 대상이다. Module 01 실습 29·30·62에 해당한다.'),
    h('학습 목표'),
    ul('새 수신 대기 포트를 만들고 auditd(80792)·osquery(24010)·netstat 명령 모니터링(533)이 각각 언제 그 변화를 보고하는지 비교한다.',
       '포트 스캔이 방화벽 LOG·아카이브·경보(4151)에 남는 수를 비교하고, 각 수가 무엇을 세는지 구분한다.',
       'osquery로 현재 상태를 SQL로 조회하고, 예약 조회의 added·removed로 상태 변화의 시각을 찾는다.'),
    img(FIG+'rev01-roadmap.png','도식 10-1. 10장 학습 순서.',110),
    h('준비와 완료 기준'),
    tab(['항목','내용'],[
        ['실행 위치','kt66 VM 터미널 세 개(A·B·C), 공격자 VM 터미널, Windows 브라우저'],
        ['선행 조건','1.9의 Nmap 설치, 9장의 kt66-host 에이전트, 4.4의 wazuh-archives-* 검색'],
        ['완료 기준','10.6의 두 표(기록별 시각, 기록별 수)를 자신의 결과로 채운다.'],
        ['결과가 다를 때','10.7 끝의 증상별 확인 순서를 따른다.'],
        ['원상복구','10.5에서 리스너 두 개와 공개 키를 되돌린다.']],[30,97],keep=True),
    box('field','본문의 결과 값과 화면은 2026년 11월 3일의 실행 기록이다. 그 환경의 kt66 VM은 192.168.0.107, 공격자 VM은 192.168.0.108이었다. 본문 예시값으로는 각각 192.168.0.189와 192.168.0.202이다. 화면의 hostIdentifier ccc는 그 환경의 kt66 VM 호스트 이름이다.'))

# ── 10.1 ─────────────────────────────────────────────────────
section('10.1  세 가지 기록',
    p('수신 대기(listening)는 프로그램이 주소와 포트를 열어 두고 새 연결을 기다리는 상태이다. ss와 netstat는 이 소켓 목록을 출력한다. kt66은 호스트(kt66 VM)에 다음 수집을 둔다. 모두 kt66.sh up이 매번 실행하는 deployment/host-sensors.sh가 설정한다. [1]'),
    tab(['기록','무엇을 보나','주기 · Wazuh 규칙'],[
        ['auditd','로그인 계정이 실행한 프로그램과 인자','실행 즉시 · 80792(9장)'],
        ['osquery 예약 조회','수신 대기 포트·공개 키 등의 현재 목록과 그 차이','60초 · 24010'],
        ['netstat 명령 모니터링','netstat 출력 전체와 이전 출력의 차이','360초 · 533'],
        ['kern.log','경계 방화벽이 버린 SYN 패킷','즉시 · 4101(저장 안 함) → 4151']],[34,58,35],keep=True),
    p('osquery는 운영체제 정보를 SQL로 조회할 수 있는 표로 보여 주는 도구이다. osqueryi는 사람이 직접 질문하는 프로그램이고, osqueryd는 설정에 적은 예약 조회를 반복 실행해 이전 결과와 달라진 행을 added·removed로 파일에 쓰는 서비스이다. netstat 명령 모니터링은 Wazuh 에이전트가 정해진 주기마다 명령을 실행하고 그 출력을 통째로 보내는 기능이다. [2][3]'),
    c('systemctl is-active wazuh-agent osqueryd auditd\nsudo iptables -S INPUT | grep KT66',
      '호스트 수집 서비스와 경계 방화벽이 동작 중인지 확인한다.',
      'systemctl is-active는 서비스가 지금 실행 중인지 출력한다. iptables -S INPUT은 들어오는 패킷 규칙을 출력하고, grep KT66으로 kt66의 경계 방화벽 체인으로 넘기는 줄만 고른다.',
      'active가 세 번 나오고 -A INPUT -i ens33 -j KT66-PERIMETER 형식의 줄이 나온다(ens33은 VM의 네트워크 장치 이름). 하나라도 빠지면 C10-03을 실행한다.',HOST),
    c("sudo grep -n -B2 -A1 'netstat listening' \\\n  /var/ossec/etc/ossec.conf\nsudo tail -n 1 /var/log/osquery/osqueryd.results.log",
      'netstat 명령 모니터링 설정과 osquery 예약 조회 결과 파일을 확인한다.',
      'grep의 -B2는 일치한 줄 앞 2줄, -A1은 뒤 1줄을 함께 출력한다. tail -n 1은 결과 파일의 마지막 줄이다.',
      'netstat -tulpn으로 시작하는 command, alias netstat listening ports, frequency 360이 나온다. 결과 파일 마지막 줄은 "name":"kt66_…"이 든 JSON 한 줄이다.',HOST),
    c('cd ~/kt66\nsudo ./deployment/host-sensors.sh',
      '(빠진 것이 있을 때만) kt66의 호스트 센서 설정을 다시 적용한다.',
      'kt66.sh up이 매번 실행하는 스크립트이며 여러 번 실행해도 같은 상태가 된다. 패키지 설치를 위해 인터넷 연결이 필요하다.',
      '[host-sensors] 완료: Wazuh 에이전트 kt66-host + auditd + Sysmon for Linux + osquery + 경계 방화벽 로그가 나온다. C10-01·C10-02를 다시 확인한다.',HOST))

# ── 10.2 ─────────────────────────────────────────────────────
section('10.2  새 수신 대기 포트',
    p('실습 29. 침입한 공격자는 나중에 접속할 입구로 수신 대기 프로그램을 남길 수 있다. 호스트에서 nc로 31337 포트를 열어 두고, 세 기록이 이 변화를 언제 보고하는지 본다. nc는 연결 대기만 하며 받은 내용을 실행하지 않는다. kt66 VM 터미널을 세 개 연다. A와 C는 nc를 실행한 채 두고, 나머지 명령은 B에서 실행한다.'),
    c("sudo ss -lntp 'sport = :31337'",
      '31337 포트가 비어 있는지 확인한다.',
      'ss는 소켓 목록을 출력한다. -l은 수신 대기, -n은 숫자 주소, -t는 TCP, -p는 소켓을 연 프로세스이다. 작은따옴표 안의 sport = :31337은 로컬 포트 조건이다.',
      '머리글 한 줄만 나온다. 다른 프로세스가 나오면 그 포트를 쓰지 말고 다른 빈 포트를 정한다.',HOST),
    c(f'nc -lk {KT} 31337',
      '31337 포트에서 연결을 기다린다.',
      '-l은 연결 대기, -k는 연결 하나가 끝나도 계속 기다린다. 앞의 주소는 받을 로컬 주소이다.',
      '프롬프트가 돌아오지 않으면 정상이다. 시각을 공격 일지에 적는다. 이 터미널은 10.5까지 그대로 둔다.',HOSTA),
    c("sudo ss -lntp 'sport = :31337'\nps -C nc -o pid,ppid,user,lstart,args",
      '수신 대기 상태와 그 프로세스를 확인한다.',
      'ps -C nc는 이름이 nc인 프로세스만 고르고, -o로 출력 열을 정한다. lstart는 시작 시각, args는 명령줄이다.',
      'LISTEN … 192.168.0.189:31337 … users:(("nc",pid=…))와 ccc가 실행한 nc -lk 192.168.0.189 31337이 나온다. PID를 사건 노트에 적는다.',HOST),
    q('agent.name: "kt66-host" AND\nrule.groups: "audit_command" AND\ndata.audit.execve.a0: "nc"',
      'nc 실행 기록을 찾는다.',
      '9.5와 같은 검색식이다.',
      '실행 시각에 80792가 나온다. 기록에서는 08:36:55, a1 -lk, a2 주소, a3 31337, pid 181571이었다.'),
    q('agent.name: "kt66-host" AND\ndata.osquery.name: "kt66_listening_ports"',
      'osquery 예약 조회의 수신 대기 포트 결과를 찾는다.',
      'data.osquery.name은 예약 조회의 이름이다. data.osquery.action, data.osquery.columns.port, data.osquery.columns.name 열을 추가한다.',
      '1분 안에 action added, port 31337, name nc, path /usr/bin/nc.openbsd 행이 나온다. 기록에서는 08:37:01이었다.'),
    q('agent.name: "kt66-host" AND rule.id: "533"',
      'netstat 출력 변경 경보를 찾는다.',
      '경보를 펼쳐 full_log와 previous_output을 비교한다. 6분 주기이므로 nc를 연 뒤 최대 6분을 기다린다.',
      'full_log(현재 출력)에 tcp 192.168.0.189:31337 0.0.0.0:* …/nc 줄이 있고 previous_output(이전 출력)에는 없다. 기록에서는 08:42:21이었다.'),
    screen('ports','화면 10-1. 533 경보 full_log의 마지막 줄들.',85),
    p('533은 netstat 출력이 이전과 조금이라도 다르면 붙는다. 출력에는 수신 대기 포트 전체가 들어 있으므로 경보 한 건이 새 포트 한 개를 뜻하지 않는다. 두 출력에서 같은 줄을 지워 가며 차이를 직접 찾는다. 포트가 그대로여도 프로세스 번호만 바뀌면 경보가 붙는다. 6분 점검 사이에 열렸다 닫힌 포트는 533에 남지 않는다. [4]'),
    box('predict','밖에서 31337에 접속하면 연결될까? 10.3에서 경계 방화벽 규칙을 읽고 답한다.'))

# ── 10.3 ─────────────────────────────────────────────────────
section('10.3  포트 스캔과 방화벽 기록',
    p('실습 30. 포트 스캔은 대상의 포트마다 연결을 시도해 응답으로 열림 여부를 판단하는 정찰이다. 공격자 VM의 Nmap으로 kt66 VM의 TCP 1~1000번을 한 번 조사한다. Nmap은 포트를 open(연결을 받음), closed(응답했지만 대기 프로그램 없음), filtered(응답이 없거나 필터에 막혀 판단할 수 없음)로 표시한다. [5]'),
    c('sudo iptables -S KT66-PERIMETER',
      '경계 방화벽 체인의 규칙을 읽는다.',
      'KT66-PERIMETER는 kt66이 만든 사용자 체인이다. INPUT에서 이 체인으로 넘어와 위에서부터 차례로 적용된다.',
      'ESTABLISHED,RELATED … -j RETURN, 포트마다 -p tcp --dport 번호 -j RETURN, -p tcp --syn -m limit --limit 100/s --limit-burst 200 -j LOG --log-prefix "DROP ", -p tcp --syn -j DROP 순서로 나온다.',HOST),
    p('RETURN은 이 체인을 빠져나가 원래 체인으로 돌아간다는 뜻이며, 이후 기본 정책에 따라 받아들여진다. 예외 포트 목록은 kt66-perimeter 서비스가 적용될 때의 수신 대기 포트로 만들어진다. 그 뒤에 연 31337은 목록에 없으므로 밖에서 온 SYN은 LOG 뒤 DROP된다. ss의 LISTEN은 서버 안의 상태이고, 밖에서 닿는지는 방화벽이 정한다. LOG 줄의 limit는 기록 수의 상한이다. 처음 200줄까지 바로 남기고 그 뒤로는 초당 100줄까지만 남긴다. 상한을 넘은 패킷도 다음 줄의 DROP으로 버려진다. [1][6]'),
    c('nmap --version',
      '공격자 VM의 Nmap을 확인한다.',
      '1.9의 C01-24로 설치했다.',
      'Nmap version 7.80이 나온다.',ATT),
    c(f'date\nnmap -sT -Pn -n -p 1-1000 --max-retries 1 {KT}',
      'kt66 VM의 TCP 1~1000번을 한 번 조사한다.',
      '-sT는 TCP 연결을 끝까지 맺어 보는 방식, -Pn은 사전 생존 확인을 생략, -n은 이름 조회 생략, -p는 포트 범위, --max-retries 1은 응답이 없을 때 다시 보내는 횟수의 상한이다. 대상은 자신의 kt66 VM 하나로 한정한다.',
      '기록에서는 4.91초가 걸렸고 Not shown: 993 filtered ports와 open 7개(22, 25, 53, 80, 443, 587, 993)가 나왔다. SERVICE 열은 포트 번호로 붙인 이름이며 실제 서비스를 확인한 결과가 아니다. 시각과 결과를 공격 일지에 적는다.',ATT),
    c("sudo grep -F 'SRC=192.168.0.202 ' /var/log/kern.log \\\n  | tail -n 3",
      '방화벽이 남긴 커널 기록을 읽는다.',
      'grep -F는 글자 그대로 찾는다. 주소 뒤 공백까지 넣어 .2020 같은 다른 주소와 구분한다. 주소는 자신의 공격자 VM 주소로 바꾼다.',
      'DROP IN=ens33 … SRC=192.168.0.202 DST=192.168.0.189 … PROTO=TCP SPT=… DPT=… SYN 줄이 나온다. DPT가 목적지 포트이다.',HOST),
    q('agent.name: "kt66-host" AND rule.id: "4151"',
      '같은 출발지의 반복 차단 경보를 찾는다.',
      '4151은 같은 출발지의 차단(4101)이 45초 안에 18건 쌓이면 붙고, 붙은 뒤 240초 동안은 다시 붙지 않는다.',
      '스캔 시각에 수준 10의 4151 한 건이 나온다. 기록에서는 08:37:47, data.dstport 565였다.'),
    screen('firewall','화면 10-2. 반복 차단 경보의 주소·포트 필드.',75),
    p('data.dstport 565는 이 경보를 만든 마지막 패킷 하나의 목적지 포트이다. 스캔한 포트 범위가 아니다. 4101은 no_log 옵션 때문에 경보 인덱스에 저장되지 않고 4151의 집계에만 쓰인다. 개별 차단 기록은 아카이브에서 찾는다. agent.ip 10.20.32.254는 에이전트가 Manager에 등록된 주소이며 패킷의 목적지(data.dstip)와 다르다. [7]'),
    q('agent.name: "kt66-host" AND\nlocation: "/var/log/kern.log" AND\ndata.action: "DROP" AND\ndata.srcip: "192.168.0.202"',
      '개별 차단 기록을 아카이브에서 찾는다.',
      '인덱스 패턴을 wazuh-archives-*로 바꾼다(4.4). data.dstport 열을 추가한다.',
      '기록에서는 592건이었고 data.dstport는 817, 267, 48처럼 순서 없이 섞여 있었다.',index='wazuh-archives-*'),
    screen('archives','화면 10-3. 아카이브의 개별 차단 기록.',70),
    p('필드 분포(6.6)로는 표본의 상위 값만 보인다. 서로 다른 목적지 포트의 수와 스캔 시작·끝 시각은 Dev Tools로 센다. 복사용 파일은 examples/rev01/chapter10/D10-01.json이다.'),
    q(DEVTOOLS,
      '한 출발지의 차단 기록에서 서로 다른 목적지 포트 수와 처음·마지막 시각을 센다.',
      'cardinality는 서로 다른 값의 수를 센다(근사값). min·max는 가장 이른·늦은 timestamp이다. now-1h는 지금부터 1시간 전까지이며 스캔 시각을 포함하도록 바꾼다.',
      'hits.total.value에 차단 기록 수, aggregations.ports.value에 목적지 포트 수, first·last에 시각이 나온다. 포트 수를 Nmap의 filtered 993과 비교한다.',qid='D10-01',where='Windows · Indexer management · Dev Tools'),
    box('blind','아카이브의 차단 기록으로는 스캔한 포트 전체를 셀 수 없다. 기록의 스캔은 4.91초 동안 filtered 포트 993개에 SYN을 보냈다. LOG 상한으로 그 시간에 남을 수 있는 줄은 약 690줄(처음 200 + 초당 100 × 4.9)이므로 적어도 300개 가까운 포트는 커널 로그부터 빠진다. 실제로 남은 것은 592건이었다. 스캔 범위는 공격자 쪽 기록이나 네트워크 장비의 기록과 함께 판단한다.'))

# ── 10.4 ─────────────────────────────────────────────────────
section('10.4  osquery로 현재 상태 조회',
    p('실습 62. 경보는 바뀐 순간의 기록이다. 지금 무엇이 열려 있고 어떤 키가 등록되어 있는지는 현재 상태를 직접 조회해야 안다. osquery의 listening_ports 표는 소켓, processes 표는 프로세스 정보를 담는다. 두 표를 pid로 이어 어느 프로그램이 포트를 열었는지 본다. SQL은 osqueryi의 osquery> 프롬프트에 입력하며 Discover의 DQL과 다르다. [2]'),
    c('sudo osqueryi',
      'osquery 조회 셸을 연다.',
      'sudo로 실행해야 다른 계정의 프로세스와 키 파일까지 읽는다.',
      'osquery> 프롬프트가 나온다.',HOST),
    q(SQL1+'\n.quit',
      '수신 대기 포트와 그 프로세스를 함께 조회하고 나온다.',
      'SELECT는 출력할 열, FROM은 표, l과 p는 표의 짧은 이름이다. JOIN … USING (pid)는 pid가 같은 두 표의 행을 잇는다. WHERE는 조건이고 IN은 괄호 안 값 중 하나이다. 세미콜론(;)이 SQL 문장의 끝이다. .quit는 osqueryi를 닫는 명령이다.',
      '31337 행에 nc, /usr/bin/nc.openbsd, 192.168.0.189와 C10-06의 PID가 나온다. 예약 조회(kt66_listening_ports)는 PID를 고르지 않으므로 PID는 이렇게 직접 조회해 얻는다.',qid='S10-01',where=OSQ),
    p('예약 조회 kt66_listening_ports는 127.0.0.1·::1·127.0.0.53 주소와 docker-proxy라는 이름을 빼고 TCP만 고른다. kt66_authorized_keys는 UID 1000 이상과 0인 계정의 공개 키에서 사용자·파일·알고리즘·주석만 고른다. 키 본문과 옵션은 고르지 않으므로, 주석은 그대로 두고 키 본문만 바꾸면 결과에 차이가 생기지 않는다. [1]'),
    h('두 번째 포트와 공개 키 등록'),
    c('ls -l ~/.ssh/authorized_keys ~/book10-ak.before\nmkdir -m 700 ~/book10\nssh-keygen -t ed25519 -N \'\' -C book10-lab -f ~/book10/key\ncp -p ~/.ssh/authorized_keys ~/book10-ak.before',
      'kt66 VM의 ccc 공개 키 목록을 백업하고 실습용 키를 만든다.',
      '9.3과 같은 ssh-keygen 옵션이다. 백업 이름이 비어 있는지 먼저 본다.',
      'authorized_keys는 -rw------- 1 ccc ccc …, 백업 이름은 No such file or directory이다. authorized_keys가 처음부터 없으면 백업은 실패하므로 “없음”을 적고, 원상복구 때 이번에 생긴 파일을 지운다.',HOST),
    c(f'nc -lk {KT} 31338',
      '두 번째 포트에서 연결을 기다린다.',
      'C10-05와 같다.',
      '프롬프트가 돌아오지 않는다. 시각을 공격 일지에 적는다.',HOSTC),
    c('echo >> ~/.ssh/authorized_keys\ncat ~/book10/key.pub >> ~/.ssh/authorized_keys\nssh-keygen -lf ~/.ssh/authorized_keys',
      '공개 키 한 줄을 ccc의 authorized_keys에 더한다.',
      'echo >>는 빈 줄 하나를 더해, 기존 마지막 줄 끝에 줄바꿈이 없더라도 새 키가 같은 줄에 붙지 않게 한다. ssh-keygen -lf에 키 목록 파일을 주면 키마다 지문과 주석을 출력한다.',
      '마지막 줄에 256 SHA256:… book10-lab (ED25519)가 나온다.',HOST),
    q('agent.name: "kt66-host" AND\nrule.groups: "osquery" AND\ndata.osquery.action: "added"',
      '두 예약 조회의 추가 행을 함께 본다.',
      'data.osquery.name, columns.port, columns.comment 열을 추가한다.',
      '포트 31338 행과 kt66_authorized_keys의 공개 키 행이 더해진다. 기록에서는 공개 키 08:38:22(주석 book10-key@attacker), 31338은 08:39:01이었다.'),
    screen('osquery-port','화면 10-4. osquery가 보고한 새 수신 대기 포트.',90),
    screen('osquery-key','화면 10-5. osquery가 보고한 새 공개 키.',95),
    p('calendarTime은 osquery가 조회한 시각(UTC)이고 경보 timestamp는 Wazuh가 처리한 시각이다. counter는 그 예약 조회가 차이를 보고한 순번이다. 순번이 가장 작은 보고는 osquery가 그 조회를 처음 실행한 결과일 수 있다. 처음 실행에서는 이미 있던 행도 모두 added로 나오므로, 그 행이 새로 생긴 것인지는 첫 결과의 시각과 비교한다. key_file과 username은 키가 든 파일과 그 주인이다. 키를 더한 사람이 아니다. [3]'))

# ── 10.5 ─────────────────────────────────────────────────────
section('10.5  원상복구와 removed',
    p('터미널 A와 C에서 각각 Ctrl+C를 눌러 nc를 끝낸다. Ctrl+C는 그 터미널의 전경 프로그램에 중단 신호를 보낸다. 터미널을 닫아 버렸다면 C10-06의 PID를 확인해 그 PID만 kill로 끝낸다.'),
    c("sudo ss -lntp '( sport = :31337 or sport = :31338 )'\ncp -p ~/book10-ak.before ~/.ssh/authorized_keys\ncmp ~/book10-ak.before ~/.ssh/authorized_keys\nrm ~/book10/key ~/book10/key.pub ~/book10-ak.before\nrmdir ~/book10",
      '두 포트가 닫혔는지 확인하고 공개 키 목록을 되돌린 뒤 실습 파일을 지운다.',
      'ss 조건의 or는 두 포트 중 하나이다. cp -p로 백업을 되돌리고 cmp로 같은지 확인한다. rmdir는 빈 디렉터리만 지운다.',
      'ss는 머리글만, cmp는 출력 없음, rmdir는 오류 없음이다. 공격 일지에 원상복구 시각을 적는다.',HOST),
    q('agent.name: "kt66-host" AND\nrule.groups: "osquery" AND\ndata.osquery.action: "removed"',
      '사라진 행을 확인한다.',
      '1분 남짓 기다린 뒤 검색한다.',
      '31337, 31338, 공개 키 세 행의 removed가 나온다. 기록에서는 08:45:00(포트 두 개)과 08:45:08(키)이었다.'),
    screen('removed','화면 10-6. 예약 조회에서 사라진 공개 키 행.',95),
    p('6분 뒤 Q10-03을 다시 검색하면 533이 한 건 더 있다. 이번에는 31337·31338 줄이 previous_output에만 있다(기록 08:48:21). removed는 조회 결과에서 행이 사라졌다는 뜻이다. 프로세스가 끝났는지, 키 파일이 바뀌었는지, osquery가 그 파일을 읽지 못하게 되었는지는 ss와 cmp 같은 현재 상태로 확인한다.'))

# ── 10.6 ─────────────────────────────────────────────────────
section('10.6  교차 분석',
    p('같은 변화가 세 기록에 언제 나타났는지 놓는다. 공격 일지를 덮고 경보 시각만으로 표를 채운다.'),
    img(FIG+'rev01-latency.png','도식 10-2. 같은 리스너를 세 기록이 본 시각.'),
    tab(['기록','31337 생김','31337 사라짐','늦어지는 이유'],[
        ['auditd 80792','08:36:55','없음','실행만 기록, 종료는 남지 않음'],
        ['osquery 24010','08:37:01','08:45:00','60초 주기와 시간 분산(splay)'],
        ['netstat 533','08:42:21','08:48:21','360초 주기']],[26,22,24,55],keep=True),
    p('nc를 끝낸 시각(08:44)은 어느 경보에도 없다. 사라짐은 osquery의 다음 조회와 netstat의 다음 점검으로만 알 수 있으므로, 실제 종료 시각은 그 직전 점검과 사라짐 보고 사이의 어느 때이다. 수신 대기 프로그램이 짧게 열렸다 닫히면 533에는 남지 않고, osquery에도 1분보다 짧으면 남지 않을 수 있다. 실행 기록(auditd)은 시작을 빠짐없이 남기지만 그 프로그램이 포트를 열었는지는 말해 주지 않는다. 세 기록을 함께 써야 “언제 실행되어 언제부터 언제까지 열려 있었나”에 답한다.'),
    h('같은 스캔, 다른 수'),
    img(FIG+'rev01-funnel.png','도식 10-3. 스캔 한 번이 기록마다 남은 수.',110),
    p('Nmap의 993, LOG 상한 약 690, 아카이브 592, 경보 1은 모두 같은 스캔에서 나왔다. 경보 1건은 공격이 한 번이었다는 뜻이 아니라 240초 동안 다시 붙지 않는 4151이 한 번 붙었다는 뜻이다. 아카이브 592건은 LOG 상한 안에서 남은 줄이다. 보고서에는 수마다 무엇을 셌는지 함께 쓴다.'),
    h('출발지로 다른 에이전트까지'),
    q('data.srcip: "192.168.0.202"',
      '같은 출발지가 다른 에이전트의 기록에도 있는지 본다.',
      '에이전트 조건 없이 출발지만 쓴다. 기간을 실습한 날 전체로 넓히고 agent.name과 rule.groups의 필드 분포를 연다.',
      'kt66-host의 firewall 외에 같은 날 bastion에서 SSH 실습을 했다면 sshd·authentication 그룹이 함께 나온다. 같은 주소라도 같은 사람이라고 단정하지 않고 시각과 대상 계정을 함께 본다.'),
    p('포트 스캔(정찰) 뒤에 같은 출발지의 인증 시도나 웹 요청이 이어지면 공격 단계가 이어진 것으로 본다. 자동 차단(8장)과 경계 방화벽 기록은 같은 출발지를 기준으로 묶인다.'))

# ── 10.7 ─────────────────────────────────────────────────────
section('10.7  정의 확인과 결과가 다를 때',
    c('docker exec -it kt66-siem /bin/bash',
      'Manager 컨테이너로 들어간다.',
      'kt66 VM 터미널에서 실행한다.',
      '프롬프트가 kt66-siem 안으로 바뀐다.',HOST),
    c("R=/var/ossec/ruleset/rules\ngrep -n -A4 'id=\"533\"' $R/0015-ossec_rules.xml\ngrep -n -A5 'id=\"4101\"' $R/0900-firewall_rules.xml\ngrep -n -A3 'id=\"4151\"' $R/0900-firewall_rules.xml\ngrep -n -A4 'id=\"24010\"' $R/0545-osquery_rules.xml\nexit",
      '네 규칙의 조건을 읽고 나온다.',
      'R=…은 긴 경로를 셸 변수 R에 담고 $R로 다시 쓰는 표기이다. -A는 일치한 줄 뒤 몇 줄을 함께 출력한다.',
      "533: if_sid 530, match ossec: output: 'netstat listening ports, check_diff. 4101: action DROP, options no_log. 4151: frequency 18 timeframe 45 ignore 240, if_matched_sid 4101, same_source_ip. 24010: if_sid 24000, decoded_as json, options no_full_log.",SIEM),
    p('check_diff는 같은 명령의 이전 출력과 비교해 다를 때만 경보를 만드는 옵션이다. no_full_log는 경보에 원문(full_log)을 넣지 않는 옵션이므로 osquery 경보는 data.osquery 필드로 읽는다. [4][7][8]'),
    tab(['증상','확인 순서'],[
        ['533이 없다','6분이 지났는지, C10-02의 netstat 설정, 그 사이에 포트가 닫혔는지'],
        ['osquery 결과가 없다','systemctl is-active osqueryd, 결과 파일 마지막 줄 시각, C10-03'],
        ['스캔이 closed를 많이 보인다','C10-01의 INPUT 줄과 C10-07의 DROP 줄, 스캔한 주소'],
        ['4151이 없다','C10-10의 kern.log 줄, 앞선 4151 뒤 240초 안인지, 아카이브(Q10-05)'],
        ['아카이브 검색이 비었다','인덱스 패턴 wazuh-archives-*와 시간 범위(4.4)']],[38,89],keep=True),
    h('공격 일지와 조사 기록'),
    p('공격 일지에는 리스너 두 개의 시작·종료, 스캔 시각과 결과, 공개 키 등록·복원 시각이 있어야 한다. 조사 기록은 examples/rev01/chapter10/investigation.txt 양식으로 10.6의 두 표를 옮긴다.'))

# ── 장 끝 ─────────────────────────────────────────────────────
page('10장 정리',
    h('핵심 정리'),
    ul('수신 대기 포트의 변화는 auditd(실행 즉시), osquery(60초), netstat 533(360초)이 다른 시각에 보고한다. 종료 시각은 어느 경보에도 없고 다음 점검의 사라짐으로 범위를 좁힌다.',
       'ss의 LISTEN은 서버 안의 상태이다. 밖에서 닿는지는 방화벽이 정하며, kt66 경계 방화벽은 적용 시점에 열려 있던 포트만 예외로 둔다.',
       '스캔 한 번이 Nmap·LOG·아카이브·경보에 서로 다른 수로 남는다. 4151 한 건, data.dstport 한 값은 스캔 범위가 아니다.',
       'osquery 직접 조회로 현재 상태를 보고, 예약 조회의 added·removed와 counter로 그 상태가 언제 생기고 사라졌는지 찾는다.'),
    h('확인 문제'),
    ol('533 경보의 full_log에 수신 대기 포트가 30줄 있다. 새로 생긴 포트를 어떻게 찾는가?',
       '4151의 data.dstport가 565이다. 공격자가 565번만 조사했다고 쓸 수 있는가?',
       '아카이브의 차단 기록이 592건인데 Nmap은 993개를 filtered로 보고했다. 차이는 어디서 오는가?',
       'osqueryd를 시작한 직후의 첫 added에 낯선 포트가 있다. 그 포트가 그 시각에 새로 열렸다고 쓸 수 있는가?',
       'nc를 언제 끝냈는지 경보로 알 수 있는가?'),
    h('확인 문제 해설'),
    ol('previous_output과 줄 단위로 비교해 full_log에만 있는 줄을 찾는다. 프로세스 번호만 바뀐 줄도 차이로 잡히므로 주소·포트를 기준으로 본다.',
       '쓸 수 없다. 그 값은 경보를 만든 마지막 패킷의 포트이다. 범위는 아카이브의 개별 기록과 D10-01 집계로 본다.',
       '방화벽 LOG 규칙의 기록 상한(처음 200, 이후 초당 100)이다. 4.9초 동안 남을 수 있는 줄은 약 690줄이라 993개를 다 남길 수 없다.',
       '쓸 수 없다. osquery가 그 조회를 처음 실행하면 이미 있던 행도 added로 나온다. osqueryd의 시작 시각, auditd의 실행 기록, 프로세스 시작 시각(lstart)과 비교한다.',
       '알 수 없다. auditd는 실행만 남기고, osquery·533은 다음 점검에서 사라짐을 보고한다. 종료 시각은 직전 점검과 사라짐 보고 사이로 범위를 적는다.'),
    h('더 읽을거리'),
    p('Nmap의 포트 상태 설명이다. open·closed·filtered 외에 unfiltered, open|filtered가 어떤 응답에서 나오는지 읽는다.'),
    link('Nmap · Port Scanning Basics','https://nmap.org/book/man-port-scanning-basics.html'),
    p('osquery의 결과 로그 문서이다. added·removed 차이 기록과 counter·epoch의 뜻을 10.4와 대조한다.'),
    link('osquery · Logging','https://osquery.readthedocs.io/en/stable/deployment/logging/'))

section('10장 참고 자료',
    p('결과 값과 화면은 2026년 11월 3일 kt66(기준 커밋 63d4180)의 실행 기록이다. 규칙은 Wazuh 4.10.0과 대조했다.'),
    h('[1] kt66 호스트 센서'),
    link('kt66 · deployment/host-sensors.sh',KT66+'/deployment/host-sensors.sh'),
    link('kt66 · deployment/perimeter.sh',KT66+'/deployment/perimeter.sh'),
    link('kt66 · deployment/osquery-linux.conf',KT66+'/deployment/osquery-linux.conf'),
    h('[2] osquery'),
    link('osquery · Configuration','https://osquery.readthedocs.io/en/stable/deployment/configuration/'),
    h('[3] osquery 결과 로그'),
    link('osquery · Logging','https://osquery.readthedocs.io/en/stable/deployment/logging/'),
    h('[4] Wazuh 명령 모니터링 규칙'),
    link('0015-ossec_rules.xml',WZ+'/rules/0015-ossec_rules.xml'),
    h('[5] Nmap'),
    link('Nmap · Port Scanning Basics','https://nmap.org/book/man-port-scanning-basics.html'),
    link('Nmap · Port Scanning Techniques','https://nmap.org/book/man-port-scanning-techniques.html'),
    h('[6] iptables'),
    link('iptables(8)','https://man7.org/linux/man-pages/man8/iptables.8.html'),
    link('iptables-extensions(8)','https://man7.org/linux/man-pages/man8/iptables-extensions.8.html'),
    h('[7] Wazuh 방화벽 규칙'),
    link('0900-firewall_rules.xml',WZ+'/rules/0900-firewall_rules.xml'),
    h('[8] Wazuh osquery 규칙'),
    link('0545-osquery_rules.xml',WZ+'/rules/0545-osquery_rules.xml'),
    h('[9] 강의 자료'),
    link('Module 01 Wazuh 위협탐지 DQL · 실습 29·30·62','https://docs.google.com/presentation/d/1o0H_2DDHBp8p2HvlSnEPbx6-jdURYzew/edit'))

INVESTIGATION='''네트워크 흔적·현재 상태 조사 기록

조사 범위(시각 KST · 에이전트 · 인덱스):
수신 대기 포트: 주소·포트 · 프로세스(이름·PID·사용자·시작 시각) · 직접 조회 시각
같은 포트의 기록별 시각: auditd 실행 · osquery added/removed · 533 현재/이전 출력
열려 있던 범위(언제부터 언제까지, 근거):
밖에서 닿는가(경계 방화벽 예외 · 스캔 결과):
스캔: 출발지 · 시각 · Nmap 결과 · LOG 줄 · 아카이브 건수 · 4151 건수 · 목적지 포트 수
공개 키: 사용자 · 파일 · 주석 · 지문 · added/removed 시각
같은 출발지의 다른 기록(에이전트 · 그룹 · 시각):
판정과 근거:
원상복구 확인(포트 · 키 파일 cmp · 실습 파일):
'''
README='''10장 REV01 복사용 입력

C10-01~ : 명령 블록 번호와 같은 파일. 실행 위치는 manifest.json의 where를 따른다.
Q10-01~ : Discover 검색식. queries.json에 인덱스 패턴과 설명이 있다.
S10-01.txt : osqueryi에 입력하는 SQL
D10-01.json : Dev Tools 집계 요청(10.3)
investigation.txt : 조사 기록 양식

주소 예시는 kt66 VM 192.168.0.189, 공격자 VM 192.168.0.202이다. 자신의 값으로 바꾼다.
결과 값과 화면은 2026-11-03 실행 기록(kt66 .107, 공격자 .108)이다.
'''

if __name__=='__main__':
    data={'title':'네트워크 흔적과 현재 상태 조사','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','baseline':COMMIT,'revision':'REV01',
          'comments':'REV01 원고. 결과 값·화면은 2026-11-03 실제 실행 기록. 새로 넣은 확인 절차는 README의 미검증 목록 참조.','pages':pages}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'volume01-chapter10.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    EX.mkdir(parents=True,exist_ok=True)
    for old in list(EX.glob('C10-*.txt'))+list(EX.glob('Q10-*.txt'))+list(EX.glob('S10-*.txt'))+list(EX.glob('D10-*.json')):old.unlink()
    for b in commands:(EX/(b['id']+'.txt')).write_text(b['text']+'\n')
    for b in queries:(EX/(b['id']+('.json' if b['id'].startswith('D') else '.txt'))).write_text(b['text']+'\n')
    (EX/'manifest.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
    (EX/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2)+'\n')
    (EX/'investigation.txt').write_text(INVESTIGATION)
    (EX/'README.txt').write_text(README)
    print(len(pages),'pages',len(commands),'commands',len(queries),'queries')
