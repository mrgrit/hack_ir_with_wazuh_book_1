"""REV01 · 11장 사건 재구성과 대응 판단. 저자용이며 실습 명령을 실행하지 않는다.

2026-11-06 개정 기준
- 조사 질문: 어디까지 확인했고 무엇을 모르는가. 5장부터 쓴 공격 일지와 조사 기록을 대조하고(11.1), 앞 장의 공백을
  모아 보완 후보를 정한다(11.6). 세 사례(8·9·10장 기록)는 서로 다른 실습이므로 하나의 사건으로 합치지 않는다.
- 증거는 기존 발췌본 examples/chapter11/evidence(case-a·b·c.json, manifest.json의 sha256)을 바이트 그대로
  examples/rev01/chapter11/evidence로 복사해 쓴다. PowerShell 명령은 기존 검증 명령(C11-01~05, 2026-11-03 실행)을
  bash 구문 검사와 60자 제한에 맞춰 백틱 없이 다시 썼다. 경로가 바뀌었고 C11-06은 새 명령이다(README 미검증).
- 새 공격·UI 촬영·서버 변경은 없다. 검색식은 앞 장의 것을 REV01 예시값으로 다시 쓴 것이다.
"""
import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/REV01'
EX=ROOT/'examples/rev01/chapter11'
COMMIT='63d4180b1d6866de986ef263a3bd831d6082b5d5'
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
def box(kind,*text): return {'type':'box','kind':kind,'text':list(text)}
def code(t): return {'type':'code','text':t}
def link(text,url): return {'type':'link','text':text,'url':url}
PS='Windows · PowerShell · 예제 저장소 폴더'
def c(text,purpose,syntax,result,where=PS):
    b={'type':'command','id':f'C11-{len(commands)+1:02d}','where':where,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    commands.append(b);return b
def q(text,purpose,syntax,result,index='wazuh-alerts-*',qid=None,where=None):
    n=len([x for x in queries if x['id'].startswith('Q')])+1
    b={'type':'query','id':qid or f'Q11-{n:02d}','where':where or 'Windows · Discover · '+index,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    queries.append(b);return b
def page(title,*blocks,brk=True,level='page'):
    pg={'title':title,'kind':'body','blocks':list(blocks)}
    if not brk:pg['break']=False
    if level!='page':pg['level']=level
    pages.append(pg)
def section(title,*blocks):page(title,*blocks,brk=False,level='section')
FIG='assets/figures/chapter11/'
DEVTOOLS='''GET wazuh-alerts-*/_search
{
  "size": 0,
  "query": {"bool": {"filter": [
    {"term": {"data.srcip": "192.168.0.202"}},
    {"range": {"timestamp": {
      "gte": "2026-11-02T00:00:00+09:00",
      "lte": "2026-11-04T00:00:00+09:00"}}}
  ]}},
  "aggs": {"by_agent": {
    "terms": {"field": "agent.name"},
    "aggs": {"by_time": {"date_histogram": {
      "field": "timestamp", "fixed_interval": "10m",
      "min_doc_count": 1, "time_zone": "+09:00"}}}
  }}
}'''

# ── 장 도입 ───────────────────────────────────────────────────
page('11장  사건 재구성과 대응 판단',
    p('관리자가 묻는다. “그래서 무슨 일이 있었고, 무엇을 해야 하나?” 경보 목록을 그대로 넘기면 답이 되지 않는다. 확인한 사실, 그 사실에서 끌어낸 판단, 기록으로는 알 수 없는 것, 그리고 다음 행동이 나뉘어 있어야 한다. 앞 장들에서 경보마다 판정을 적었다. 이번에는 그 판정을 증거 번호가 붙은 시간표와 대응 계획, 한 쪽짜리 보고서로 바꾼다.'),
    p('11장에서는 공격을 다시 하지 않는다. 5장부터 쓴 사건 노트의 두 기록(공격 일지와 조사 기록)을 대조하고, 8·9·10장의 기록에서 뽑은 세 사례를 재구성한다. 마지막으로 모든 장에서 찾은 탐지 공백을 모아 보완 후보를 정한다.'),
    h('학습 목표'),
    ul('공격 일지와 조사 기록을 대조해 경보로 찾은 것과 찾지 못한 것을 구분하고, 탐지 공백을 보완 후보로 정리한다.',
       '원문 시각·경보 시각·표시 시간대와 식별값(출발지, 포트, 프로세스 번호, 지문)을 구분해 증거 번호가 붙은 시간표를 만든다.',
       '관찰 사실·근거 있는 판단·미확인·다음 행동을 나누어 대응 계획과 한 쪽 보고서를 쓴다.'),
    img(FIG+'rev01-roadmap.png','도식 11-1. 11장 학습 순서.',110),
    h('준비와 완료 기준'),
    tab(['항목','내용'],[
        ['실행 위치','Windows PowerShell(예제 저장소 폴더), Windows 브라우저'],
        ['선행 조건','5~10장의 사건 노트(공격 일지·조사 기록), 책 예제 저장소'],
        ['완료 기준','세 사례의 시간표, 대응 계획, 한 쪽 보고서, 탐지 공백 표를 쓴다.'],
        ['원상복구','Windows에 만든 분석 폴더만 정리한다. 서버는 바꾸지 않는다.']],[30,97],keep=True),
    box('field','세 사례는 서로 다른 날과 시각에 한 별개의 실습이다. 같은 출발지 주소와 ccc 계정이 나오지만 하나의 공격이 이어진 사건으로 합치지 않는다. 합치려면 시각·세션·인증 수단처럼 두 기록을 잇는 근거가 있어야 하고, 이 기록들에는 그런 근거가 없다.'))

# ── 11.1 ─────────────────────────────────────────────────────
section('11.1  공격 일지와 조사 기록',
    p('5장부터 공격을 보낼 때마다 공격 일지에 시각·출발지·대상·입력·응답을 적었고, Wazuh에서 확인한 사실은 조사 기록에 따로 적었다. 두 기록을 나란히 놓으면 세 가지가 드러난다. 일지에도 조사 기록에도 있는 행(탐지된 행동), 일지에만 있는 행(탐지 공백), 조사 기록에만 있는 행(내가 보내지 않았는데 보인 기록)이다.'),
    tab(['대조 결과','뜻','다음 행동'],[
        ['양쪽에 있음','경보·아카이브로 찾을 수 있는 행동','찾은 검색식을 조사 기록에 남긴다'],
        ['일지에만 있음','기록이 없거나 경보가 되지 않은 행동','어느 기록에 남았는지(아카이브·원문) 찾고, 없으면 공백으로 적는다'],
        ['조사 기록에만 있음','내가 만들지 않은 기록','다른 사용자·자동 작업·센서 동작인지 확인한다']],[28,48,51],keep=True),
    h('출발지 주소가 다른 행'),
    p('5장에서 Windows 브라우저로 보낸 요청은 웹 서버에 ipconfig의 PC 주소가 아니라 10.20.30.254로 기록될 수 있었다. 10.20.30.254는 kt66 VM이 ext망에서 쓰는 주소이다. 이 값이 출발지로 남았다는 것은 요청이 kt66 VM을 지나면서 출발지가 kt66 VM 주소로 바뀌었다는 뜻이다. 공격자 VM의 요청은 출발지가 그대로 남았다. 어느 단계에서 바뀌었는지는 kt66 VM의 주소 변환 규칙(sudo iptables -t nat -S)과 두 요청이 도착한 주소·포트를 비교해 확인하고 조사 기록에 적는다. 출발지가 바뀌는 경로에서는 data.srcip만으로 실제 PC를 특정할 수 없고, 주소를 바꾼 장비의 기록이 함께 필요하다.'),
    box('predict','자신의 일지에서 “일지에만 있음” 행은 몇 개인가? 그 행들이 어느 장에 몰려 있는가? 11.6의 표와 비교한다.'))

# ── 11.2 ─────────────────────────────────────────────────────
section('11.2  시각과 식별값',
    img(FIG+'rev01-cases.png','도식 11-2. 세 사례의 경계.'),
    p('시간표의 시각은 세 가지를 구분한다. 원문 시각은 프로그램이 로그 줄에 적은 값(predecoder.timestamp)이다. 경보 timestamp는 Manager가 기록을 받아 경보를 만든 시각이며 UTC로 저장된다. Discover는 이 값을 브라우저 시간대로 바꿔 보여 준다. 한국 표준시(KST)는 UTC보다 9시간 빠르다.'),
    tab(['예(사례 B)','값'],[
        ['원문 시각','Nov  3 07:50:25 (bastion의 auth.log, KST)'],
        ['경보 timestamp','2026-11-02T22:50:27.428+0000 (UTC)'],
        ['Discover 표시','Nov 3, 2026 @ 07:50:27.428 (KST)']],[30,97],keep=True),
    p('세 값은 한 사건이다. 2초 차이는 로그를 읽어 보내는 지연이다. 9.9에서 본 것처럼 서로 다른 기록의 순서는 경보 timestamp로 정하면 뒤바뀔 수 있으므로 원문 시각 열을 따로 둔다. 날짜도 UTC로 보면 하루 앞선다(11월 2일). 시간표에는 원문 시각, 경보 timestamp, 시간대를 별도 열로 둔다.'),
    tab(['식별값','잇는 범위','주의'],[
        ['출발지 주소','같은 출발지의 모든 기록','NAT·공유 주소에서는 사람이 여럿일 수 있다'],
        ['출발지 포트','한 TCP 연결','연결이 끝나면 다른 연결이 다시 쓴다'],
        ['sshd 프로세스 번호','한 연결의 sshd·PAM 줄','시간이 지나면 다시 쓰인다'],
        ['audit 세션·pid·ppid','한 로그인 세션의 명령과 부모 관계','같은 호스트에서만 의미가 있다'],
        ['키 지문','같은 공개 키','키 끝 설명(주석)은 누구나 바꿀 수 있다'],
        ['파일 경로·해시','같은 파일 내용','호스트가 다르면 같은 경로도 다른 파일이다']],[32,40,55],keep=True),
    p('bastion과 kt66-host 모두 ccc 계정과 /home/ccc/.ssh/authorized_keys가 있지만 다른 시스템의 다른 파일이다. 식별값 하나만 같으면 연결 후보로 적고, 둘 이상이 같은 시각 범위에서 맞을 때 연결 근거로 쓴다.'))

# ── 11.3 ─────────────────────────────────────────────────────
section('11.3  증거 사본과 해시',
    p('증거를 다룰 때는 원본을 그대로 두고 사본으로 분석한다. 원본의 위치, 뽑은 기준, 사본의 해시를 기록해 두면 나중에 누구든 같은 사본인지 확인할 수 있다. 책 예제 저장소의 examples/rev01/chapter11/evidence에 세 사례의 경보 발췌본이 있다. 8·9·10장 기록에서 사례마다 필요한 경보만 뽑고 증거 번호(evidence_id)와 출처 장(source_chapter)을 더한 것이다. manifest.json에 원본 경로·뽑은 기준·SHA-256이 있다. 원본 전체 로그나 디스크 이미지가 아니다.'),
    p('Windows에서 예제 저장소 폴더를 열고 주소창에 powershell을 입력해 그 위치에서 PowerShell을 연다. 아래 명령은 이 PowerShell 창에서 순서대로 실행한다. 변수($로 시작하는 이름)는 같은 창 안에서만 유지된다.'),
    c('Get-Location\nTest-Path .\\book11\nGet-ChildItem .\\examples\\rev01\\chapter11\\evidence',
      '현재 위치와 분석 폴더 이름을 확인하고 증거 파일 목록을 본다.',
      'Get-Location은 현재 폴더를 출력한다. Test-Path는 경로가 있으면 True, 없으면 False를 출력한다. Get-ChildItem은 폴더 안의 파일을 나열한다. .\\는 현재 폴더를 뜻한다.',
      '예제 저장소 폴더 경로, False, case-a.json·case-b.json·case-c.json·manifest.json 네 파일이 나온다. True이면 이미 있는 book11 폴더의 내용을 확인하고 다른 이름을 쓴다.'),
    c("New-Item -ItemType Directory .\\book11\n$src = '.\\examples\\rev01\\chapter11\\evidence'\nCopy-Item \"$src\\*.json\" .\\book11\nGet-ChildItem .\\book11",
      '분석 폴더를 만들고 증거 파일을 복사한다.',
      'New-Item -ItemType Directory는 폴더를 만든다. $src = …는 경로를 변수에 담는다. Copy-Item의 *.json은 확장자가 json인 모든 파일이다. 큰따옴표 안의 $src는 변수 값으로 바뀐다.',
      'book11에 네 파일이 보인다. 이후 분석은 이 사본으로 하고 원본 폴더의 파일은 열어 고치지 않는다.'),
    c('Get-FileHash .\\book11\\*.json -Algorithm SHA256\nGet-Content .\\book11\\manifest.json',
      '사본의 해시를 계산해 manifest의 값과 대조한다.',
      'Get-FileHash는 파일 내용의 해시를 계산하며 -Algorithm으로 방식을 정한다. Get-Content는 파일 내용을 출력한다.',
      'case-a.json의 Hash가 98C405B9…(manifest의 sha256 98c405b9…와 대소문자만 다름), case-b.json이 F804E4FD…, case-c.json이 63231335…로 시작한다. 다르면 파일이 바뀌었거나 줄바꿈이 변환된 것이므로 분석하지 않고 저장소를 다시 받는다.'),
    p('해시가 같다는 것은 사본이 manifest를 만들 때의 파일과 같은 바이트라는 뜻이다. 그 기록이 처음부터 정확했는지, 그 기간의 모든 기록을 담았는지는 해시가 말해 주지 않는다. 그래서 manifest에는 원본 위치와 뽑은 기준(selection)을 함께 적는다. 운영 사건에서는 이 표에 수집자, 수집 시각, 인계 기록을 더해 증거 대장(examples/rev01/chapter11/evidence-register.csv)으로 관리한다.'),
    c("$f = '.\\book11\\case-a.json'\n$caseA = Get-Content -Raw $f | ConvertFrom-Json\n$caseA | Select-Object -First 1 | Format-List *",
      '사례 A의 첫 기록을 필드 단위로 읽는다.',
      'Get-Content -Raw는 파일 전체를 문자열 하나로 읽고, ConvertFrom-Json은 JSON을 PowerShell 객체로 바꾼다. PowerShell의 파이프(|)도 앞 명령의 결과를 다음 명령으로 넘긴다. Select-Object -First 1은 첫 기록, Format-List *는 모든 속성을 한 줄씩 보인다.',
      'evidence_id A-001, timestamp 2026-11-02T11:37:05.325+0000, rule, agent, data, full_log 등이 나온다. 중첩된 값은 @{…}로 줄여 보인다.'),
    c('$caseA[0].agent | Format-List *\n$caseA[0].data | Format-List *\n$caseA[0].full_log',
      '중첩된 필드와 원문을 펼친다.',
      '[0]은 첫 번째 기록, 마침표(.)는 그 안의 속성이다.',
      'agent는 id 001, name bastion, data는 srcip 192.168.0.108, srcport 42688, dstuser ccc이고 full_log는 Nov  2 20:37:04 bastion sshd[2537]: Failed password for ccc from 192.168.0.108 port 42688 ssh2이다. data의 세 값이 원문 어디에서 왔는지 짚는다.'),
    c("$f = '.\\book11\\case-c.json'\n$caseC = Get-Content -Raw $f | ConvertFrom-Json\n$rule = @{n='rule';e={$_.rule.id}}\n$caseC | Sort-Object timestamp |\n  Format-Table evidence_id, timestamp, $rule",
      '사례 C의 기록을 시각순 표로 본다.',
      "@{n='rule';e={…}}는 표에 새 열을 만드는 계산 속성이다. n은 열 이름, e는 값을 만드는 식이며 $_는 지금 처리 중인 기록이다. 줄 끝의 파이프(|)는 다음 줄로 명령을 잇는다.",
      'C-001(24010)부터 C-009(533)까지 아홉 줄이 시각순으로 나온다. 이 표가 사례 C 시간표의 뼈대이다.'))

# ── 11.4 ─────────────────────────────────────────────────────
section('11.4  세 사례의 시간표',
    img(FIG+'rev01-levels.png','도식 11-3. 기록에서 결론까지의 층.',115),
    h('사례 A · SSH 인증(8장, bastion)'),
    tab(['증거','원문 시각(KST)','기록','읽은 값'],[
        ['A-001','11-02 20:37:04','5760 Failed password','sshd[2537] · 포트 42688 · ccc'],
        ['A-002','11-02 20:37:12','5715 Accepted password','sshd[2537] · 포트 42688 · ccc']],[16,30,40,41],keep=True),
    q('agent.name: "bastion" AND\ndata.srcip: "192.168.0.202" AND\n(rule.id: "5760" OR rule.id: "5715")',
      '자신의 8장 기록에서 같은 출발지의 실패와 성공을 고른다.',
      '기간을 8장 실습 시간으로 정하고 data.srcport 열을 추가한다. 출발지는 자신의 공격자 VM 주소이다.',
      '사례 A의 기록에서는 22건이었다. 같은 포트의 실패와 성공을 찾는다.'),
    tab(['층','사례 A'],[
        ['관찰 사실','20:37:12에 192.168.0.108에서 ccc의 암호 인증이 성공했다(A-002).'],
        ['근거 있는 판단','같은 연결(sshd[2537], 포트 42688)에서 실패(A-001) 뒤 성공했다. 두 기록의 프로세스 번호와 포트가 모두 같다.'],
        ['미확인','성공한 세션에서 무엇을 실행했는가. 계정 소유자의 접속이었는가.'],
        ['다음 행동','같은 시각 이후 ccc의 sudo·세션 기록, 계정 소유자 확인']],[28,99],keep=True),
    h('사례 B · 공개 키(9장, bastion)'),
    tab(['증거','시각(KST)','기록','읽은 값'],[
        ['B-001','11-03 07:50:21(경보)','550 authorized_keys','99→196바이트, diff에 키 한 줄 추가'],
        ['B-003','07:50:25(원문)','5715 Accepted publickey','ccc · 192.168.0.108 · ED25519 지문'],
        ['B-002','11-03 07:50:25(경보)','550 authorized_keys','196→99바이트, 키 줄 삭제']],[16,30,40,41],keep=True),
    q('agent.name: "bastion" AND\nsyscheck.path: "/home/ccc/.ssh/authorized_keys"',
      '자신의 9장 기록에서 키 파일 변경을 찾는다.',
      '기간을 9장 실습 시간으로 정한다. 9.3의 Q09-03과 같다.',
      '키 추가와 원상복구의 550 두 건이 나온다.'),
    tab(['층','사례 B'],[
        ['관찰 사실','키 한 줄이 더해졌다(B-001). 07:50:25에 공개 키로 ccc 로그인이 성공했다(B-003). 키 줄이 지워졌다(B-002).'],
        ['근거 있는 판단','로그인에 쓰인 키는 더해진 키이다. B-001 diff의 공개 키로 계산한 지문이 B-003 원문의 SHA256:FnGa4j0F…와 같다(9.3).'],
        ['미확인','키를 더한 세션이 어느 것인가(sudo 없이 ccc 파일 수정, 9.9). 로그인 뒤 무엇을 했는가.'],
        ['다음 행동','07:50:21 앞에 열려 있던 ccc 세션(5715·5501) 목록, 키 제거 뒤 남은 세션 확인']],[28,99],keep=True),
    p('B-002(07:50:25.985)가 B-003의 경보 시각(07:50:27.428)보다 앞서 있어도, B-003의 원문 시각이 07:50:25이고 지운 키로는 로그인할 수 없으므로 로그인이 먼저이다. 시간표에 원문 시각 열을 따로 두는 이유이다.'),
    h('사례 C · 포트와 키 상태(10장, kt66-host)'),
    tab(['증거','시각(KST)','기록','읽은 값'],[
        ['C-001','08:37:01','24010 added','31337 · nc'],
        ['C-002','08:37:47','4151','192.168.0.108 → .107 반복 차단'],
        ['C-003·004','08:38:22 · 08:39:01','24010 added','공개 키(book10-key@attacker) · 31338'],
        ['C-005','08:42:21','533','현재 출력에 31337·31338'],
        ['C-006~008','08:45:00~08','24010 removed','31337 · 31338 · 공개 키'],
        ['C-009','08:48:21','533','이전 출력에만 31337·31338']],[18,32,32,45],keep=True),
    q('agent.name: "kt66-host" AND rule.groups: "osquery"',
      '자신의 10장 기록에서 osquery 결과를 시각순으로 본다.',
      'data.osquery.name, action, columns.port, columns.comment 열을 추가한다.',
      '포트 두 개와 공개 키 한 개의 added와 removed가 나온다.'),
    tab(['층','사례 C'],[
        ['관찰 사실','31337·31338 수신 대기와 공개 키 한 줄이 생겼다가 사라졌다. 같은 시간대에 192.168.0.108이 반복 차단되었다.'],
        ['근거 있는 판단','31337은 08:37:01 이전부터 08:45:00 직전까지 열려 있었다(osquery added·removed와 533의 현재·이전 출력이 일치).'],
        ['미확인','그 포트로 들어온 연결이 있었는가. 추가된 키로 로그인했는가(사례 C에는 그 기록이 없다).'],
        ['다음 행동','같은 기간의 경계 방화벽 기록에서 DPT=31337, kt66-host의 Accepted publickey 검색']],[28,99],keep=True),
    p('사례 C의 공개 키 행은 사례 B와 주석·대상이 다르다. 사례 B의 로그인 기록을 가져와 사례 C의 키가 쓰였다고 쓰지 않는다. 4151의 출발지(192.168.0.108)가 사례 A·B의 출발지와 같아도 별개의 실습이다.'),
    h('출발지 하나의 날짜별 분포'),
    p('사례를 나누는 근거를 숫자로 확인한다. 6.6의 Dev Tools에서 한 출발지의 경보를 에이전트별, 10분 단위로 센다. 복사용 파일은 examples/rev01/chapter11/D11-01.json이다.'),
    q(DEVTOOLS,
      '한 출발지의 경보가 어느 에이전트에서 언제 몰려 있는지 센다.',
      'date_histogram은 시간 구간별로 문서 수를 센다. fixed_interval 10m은 10분 단위, min_doc_count 1은 빈 구간을 빼고, time_zone은 구간을 KST로 나눈다. 주소와 기간은 자신의 값으로 바꾼다.',
      'by_agent 아래 에이전트마다 시간 구간과 doc_count가 나온다. 경보가 몰린 구간이 에이전트·날짜별로 떨어져 있으면 그 구간이 사례의 경계 후보이다. 사례 기록이라면 bastion은 11월 2일 20시대와 11월 3일 07시대, kt66-host는 11월 3일 08시대에 나뉘어 나온다.',qid='D11-01',where='Windows · Indexer management · Dev Tools'))

# ── 11.5 ─────────────────────────────────────────────────────
section('11.5  대응 판단',
    p('침해 대응은 봉쇄(진행 중인 피해를 멈춤), 제거(원인과 지속 수단을 없앰), 복구(안전한 정상 운영으로 돌아감)로 나뉜다. 실제로는 새 증거가 나올 때마다 이 단계를 다시 오간다. 대응 계획은 증거 번호에서 출발하고, 조치마다 대상·근거·실행 권한·기대 결과·확인 방법·되돌릴 조건을 적는다. [1]'),
    tab(['사례','확인된 상태','조치 후보','조치 뒤 확인'],[
        ['A','ccc 암호가 알려졌다','ccc 암호 교체, ccc의 열린 세션 확인·종료, 출발지 접근 제한','새 암호로만 로그인되는지, 옛 암호 실패(5760)'],
        ['B','ccc에 모르는 키가 등록·사용되었다','키 줄 제거(내용 보존 뒤), 열린 세션 종료, 다른 키 목록 점검','그 키로 새 연결 거부, FIM 550 원상복구'],
        ['C','모르는 수신 대기 프로세스와 키 줄','프로세스 정보 보존 뒤 종료, 키 줄 제거, 시작 경로(9장의 지속성 위치) 점검','osquery removed, ss·533 사라짐']],[13,33,46,35],keep=True),
    p('“IP 차단”처럼 범위가 없는 조치는 쓰지 않는다. 어느 장비의 어느 방향, 어떤 포트에, 언제까지 적용하는지 쓴다. 암호만 바꾸면 사례 B처럼 등록된 키는 남고, 키만 지우면 이미 열린 세션은 계속된다. 조치 하나가 다른 접근 경로를 막지 못하는 경우를 표의 “조치 뒤 확인”으로 메운다. 대응 계획 양식은 examples/rev01/chapter11/response-template.txt이다.'),
    box('field','11장의 대응 연습은 계획을 쓰는 데까지이다. 실제 계정 정지·방화벽 변경·서버 격리는 그 환경의 승인과 복구 경로를 갖춘 뒤 실행한다. 조치 전에 보존할 것(프로세스 정보, 키 파일 내용, 경보 원문)을 먼저 적는다.'),
    h('종결 기준'),
    tab(['항목','확인'],[
        ['원인과 지속 수단','확인된 원인을 조치했고, 9장의 지속성 위치를 점검했다.'],
        ['자격 증명과 세션','영향받은 암호·키를 교체·제거했고 남은 세션을 확인했다.'],
        ['수집','에이전트·센서가 정상이고 조치 후 기간의 기록이 들어온다.'],
        ['재발 관찰','같은 출발지·계정·경로를 정한 기간 동안 검색으로 관찰한다.']],[32,95],keep=True),
    p('경보가 멈췄다고 종결하지 않는다. 에이전트가 끊겨 조용한 것인지 먼저 확인한다. 수집이 끊긴 기간은 “행위 없음”이 아니라 “기록 없음”으로 적는다.'))

# ── 11.6 ─────────────────────────────────────────────────────
section('11.6  탐지 공백과 보완 후보',
    p('각 장의 공격 일지 대조에서 “경보에 없음”이었던 행을 모은다. 기록 자체가 없는 것과, 기록은 있는데 경보가 되지 않은 것을 나눈다. 앞의 것은 수집을 늘려야 하고, 뒤의 것은 규칙을 더하거나 검색으로 메운다.'),
    tab(['장','경보에 없던 행동','기록이 있던 곳','보완 후보'],[
        ['5','200으로 처리된 인코딩 경로 조작','아카이브','디코딩한 URL에 일치하는 사용자 규칙'],
        ['5·7','POST 본문의 입력, 기록되지 않는 헤더','WAF 감사 기록','감사 기록 수집과 규칙'],
        ['6','탐색 도구가 찾아낸 200 경로','아카이브(NOT 404)','같은 출발지의 404 다수 뒤 200을 묶는 규칙'],
        ['6','로그인 시도와 성공','아카이브','POST /login.php 반복을 묶는 규칙'],
        ['7·9','docker exec 셸의 명령과 파일 변경','없음(호스트 감사에 docker 실행만)','docker exec 사용 감사와 승인 절차'],
        ['9','ccc가 sudo 없이 바꾼 자기 파일의 주체','열린 세션 후보','감사 연동 FIM(whodata)을 쓸 수 있는 환경'],
        ['9','/var/log 로그 비우기','인덱서와 로컬 비교','로그 전송이 끊긴 구간 감시'],
        ['10','스캔한 포트 범위 전체','공격자 쪽 기록','LOG 상한 조정 또는 흐름 기록'],
        ['10','6분보다 짧게 열린 수신 대기','auditd 실행 기록','osquery 주기 단축, 실행 기록과의 상관']],[10,40,33,44],keep=True),
    p('보완 후보는 비용이 따른다. 아카이브를 오래 보관하거나 주기를 줄이면 저장 공간과 처리량이 는다. 규칙을 더하면 정상 업무도 경보가 된다. 4장의 사용자 규칙 작성 절차로 후보 하나를 골라 실험 환경에서 시험한 뒤, 정상 기록에서 몇 건이 붙는지부터 확인한다.'),
    box('predict','표의 후보 중 하나를 고른다면 무엇인가? 그 규칙이 붙을 정상 업무는 무엇이 있을까?'))

# ── 11.7 ─────────────────────────────────────────────────────
section('11.7  한 쪽 보고서',
    p('보고서 첫 문장에 대상과 확인 결과를 쓴다. 이어서 근거(증거 번호), 범위, 영향, 조치, 미확인과 후속을 적는다. 규칙 이름과 필드 값을 길게 늘어놓기보다 판단에 쓴 증거 번호로 연결한다. 사례 B의 예이다.'),
    tab(['항목','내용'],[
        ['요약','bastion의 ccc 계정에 공개 키 한 줄이 등록되었고 그 키로 로그인이 한 번 성공했다(실습).'],
        ['근거','B-001(키 줄 추가, 550 diff), B-003(Accepted publickey, 지문 일치), B-002(키 줄 삭제)'],
        ['범위','2026-11-03 07:45~08:05 KST · bastion · ccc'],
        ['영향','등록된 키로 ccc 권한 접속이 가능했다. 접속 뒤 활동은 이 기록에서 확인하지 않았다.'],
        ['조치','키 파일을 실습 전 내용으로 되돌렸고 그 키의 새 연결이 거부되었다(9.3).'],
        ['미확인·후속','키를 등록한 세션, 로그인 뒤 명령 기록. 운영 사건이면 ccc의 다른 키와 열린 세션 점검'],
        ['시간대','KST(원문), 경보 timestamp는 UTC로 저장']],[22,105],keep=True),
    p('자신의 사례로 같은 표를 쓴다. 증거 없이 칸을 채우지 않고, 모르는 칸에는 모르는 이유와 다음 수집 대상을 쓴다. 조사 기록 양식은 examples/rev01/chapter11/investigation-template.txt, 시간표 양식은 timeline.csv이다.'),
    h('정리'),
    c('Get-FileHash .\\book11\\case-*.json -Algorithm SHA256\nRemove-Item -Recurse .\\book11',
      '분석 사본의 해시를 다시 확인한 뒤 분석 폴더를 지운다.',
      'Remove-Item -Recurse는 폴더와 안의 파일을 함께 지운다. 작성한 시간표·보고서를 다른 곳에 보관했는지 먼저 확인한다.',
      '해시가 C11-03과 같고 폴더가 지워진다. 예제 저장소의 원본 증거 파일은 그대로 남는다.'))

# ── 장 끝 ─────────────────────────────────────────────────────
page('11장 정리',
    h('핵심 정리'),
    ul('공격 일지와 조사 기록의 대조에서 “일지에만 있음”이 탐지 공백이다. 기록이 없는 공백은 수집으로, 경보가 되지 않은 공백은 규칙·검색으로 메운다.',
       '시간표에는 원문 시각, 경보 timestamp, 시간대를 따로 둔다. 서로 다른 기록의 순서는 원문 시각으로 정한다.',
       '식별값 하나가 같으면 후보, 둘 이상이 같은 시각 범위에서 맞으면 근거이다. 같은 주소·계정이라도 별개의 실습을 하나의 사건으로 합치지 않는다.',
       '결론은 관찰 사실·근거 있는 판단·미확인·다음 행동으로 나눈다. 대응은 다른 접근 경로가 남는지까지 확인해야 끝난다.'),
    h('확인 문제'),
    ol('같은 출발지와 ccc 계정이 사례 A와 사례 C에 나온다. 한 공격자가 bastion에서 kt66 VM으로 옮겨 갔다고 쓸 수 있는가?',
       '사례 B의 B-002가 B-003보다 경보 timestamp가 이르다. 키를 지운 뒤 로그인했다고 쓸 수 있는가?',
       '사본의 해시가 manifest와 같다. 원본 기록이 완전하다는 증거인가?',
       'ccc의 암호를 바꿨다. 사례 B의 상황이라면 대응이 끝났는가?',
       '조치 뒤 경보가 멈췄는데 에이전트가 disconnected이다. 무엇을 먼저 하는가?'),
    h('확인 문제 해설'),
    ol('쓸 수 없다. 두 사례는 날짜·대상 시스템·관찰 대상이 다르고, 세션·인증 수단처럼 둘을 잇는 기록이 없다. 같은 주소는 연결 후보일 뿐이다.',
       '쓸 수 없다. B-003의 원문 시각은 07:50:25로 삭제와 같은 초이며, 지운 키로는 로그인할 수 없다. 경보 timestamp는 로그를 읽어 보내는 지연을 포함한다.',
       '아니다. 해시는 사본이 manifest를 만든 때의 파일과 같다는 것만 보인다. 완전성은 뽑은 기준과 원본 위치로 따로 확인한다.',
       '아니다. 등록된 키는 암호와 상관없이 남고, 열린 세션도 계속된다. 키 목록 점검과 세션 종료가 필요하다.',
       '수집을 복구하고 끊긴 기간을 기록한다. 그 기간의 원본 로그를 확인하기 전에는 “행위 없음”으로 적지 않는다.'),
    h('더 읽을거리'),
    p('NIST의 침해 대응 지침이다. 탐지·대응·복구를 조직의 위험 관리와 어떻게 잇는지 11.5의 표와 대조한다.'),
    link('NIST SP 800-61 Rev. 3','https://csrc.nist.gov/pubs/sp/800/61/r3/final'))

section('11장 참고 자료',
    p('세 사례의 기록은 8장(2026-11-02), 9장·10장(2026-11-03) 실행 기록의 발췌본이다. 새 공격과 화면 촬영은 하지 않았다.'),
    h('[1] 침해 대응'),
    link('NIST SP 800-61 Rev. 3','https://csrc.nist.gov/pubs/sp/800/61/r3/final'),
    h('[2] Wazuh 이벤트 기록'),
    link('Wazuh · Event logging','https://documentation.wazuh.com/current/user-manual/manager/event-logging.html'),
    h('[3] PowerShell'),
    link('Microsoft Learn · Get-FileHash','https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/get-filehash'),
    link('Microsoft Learn · ConvertFrom-Json','https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/convertfrom-json'),
    h('[4] 책 예제 저장소'),
    link('hack_ir_with_wazuh_book_1','https://github.com/mrgrit/hack_ir_with_wazuh_book_1'))

README='''11장 REV01 복사용 입력

C11-01~ : PowerShell 명령(예제 저장소 폴더에서 한 창으로 순서대로). manifest.json에 실행 위치가 있다.
Q11-01~ : Discover 검색식. queries.json에 인덱스 패턴과 설명이 있다.
D11-01.json : Dev Tools 집계 요청(11.4)
evidence/ : 세 사례의 경보 발췌본과 manifest.json(원본 위치·뽑은 기준·SHA-256). 줄바꿈 변환을 막는 .gitattributes 포함
investigation-template.txt · response-template.txt · timeline.csv · evidence-register.csv : 양식

주소 예시는 kt66 VM 192.168.0.189, 공격자 VM 192.168.0.202이다. 발췌본의 주소는 기록 환경 값(.107·.108)이다.
'''

if __name__=='__main__':
    data={'title':'사건 재구성과 대응 판단','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','baseline':COMMIT,'revision':'REV01',
          'comments':'REV01 원고. 8~10장 기록 발췌본으로 재구성. 새 공격·촬영 없음.','pages':pages}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'volume01-chapter11.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    EX.mkdir(parents=True,exist_ok=True)
    for old in list(EX.glob('C11-*.txt'))+list(EX.glob('Q11-*.txt'))+list(EX.glob('D11-*.json')):old.unlink()
    for b in commands:(EX/(b['id']+'.txt')).write_text(b['text']+'\n')
    for b in queries:(EX/(b['id']+('.json' if b['id'].startswith('D') else '.txt'))).write_text(b['text']+'\n')
    (EX/'manifest.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
    (EX/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2)+'\n')
    src=ROOT/'examples/chapter11'
    (EX/'evidence').mkdir(exist_ok=True)
    for f in ['case-a.json','case-b.json','case-c.json','manifest.json','.gitattributes']:shutil.copyfile(src/'evidence'/f,EX/'evidence'/f)
    for f in ['investigation-template.txt','response-template.txt','timeline.csv','evidence-register.csv']:shutil.copyfile(src/f,EX/f)
    (EX/'README.txt').write_text(README)
    print(len(pages),'pages',len(commands),'commands',len(queries),'queries')
