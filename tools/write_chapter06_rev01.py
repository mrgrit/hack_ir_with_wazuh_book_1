"""REV01 · 6장 웹 탐색과 인증 공격. 저자용이며 실습 명령을 실행하지 않는다.

2026-11-05 개정 기준
- 조사 질문: 무엇을 찾고 어떻게 들어오려 했는가.
- 앞부분(6.1~6.5)은 공격을 보내며 공격 일지를 쓰고, 뒷부분(6.6~6.7)은 일지를 덮고 경보만으로 다시 찾는다.
  분포 읽기·값 필터·집계(Dev Tools)·출발지 피벗·타임라인·아카이브의 성공 요청 찾기를 다룬다(사용자 지적 반영).
- 공격·화면·검색 결과는 2026-11-01 기존 kt66 실측(editorial/chapter06-review.json)을 따른다.
- 6.6~6.7의 건수는 같은 시간 범위의 저장 기록(editorial/evidence/chapter06/wazuh-alerts-records.json 30건,
  wazuh-archives-records.json 63건)을 센 값이다. 필드 상세·Dev Tools 화면은 새로 촬영하지 못해 촬영 자리로 둔다.
"""
import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/REV01'
EX=ROOT/'examples/rev01/chapter06'
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
def screen(name,caption,width=127): return img(f'assets/screens/chapter06/{name}.png',caption,width)
def slot(title,text): return {'type':'capture_slot','title':title,'text':text}
def box(kind,*text,items=None):
    b={'type':'box','kind':kind,'text':list(text)}
    if items:b['items']=items
    return b
def code(t): return {'type':'code','text':t}
def link(text,url): return {'type':'link','text':text,'url':url}
HOST='kt66 VM · 터미널';WEB='kt66-web 컨테이너 · 셸';SIEM='kt66-siem 컨테이너 · 셸';DVWA='kt66-dvwa 컨테이너 · 셸';ATT='공격자 VM · 터미널'
def c(text,purpose,syntax,result,where):
    b={'type':'command','id':f'C06-{len(commands)+1:02d}','where':where,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    commands.append(b);return b
def q(text,purpose,syntax,result,index='wazuh-alerts-*',qid=None,where=None):
    b={'type':'query','id':qid or f'Q06-{len([x for x in queries if x["id"].startswith("Q")])+1:02d}','where':where or 'Windows · Discover · '+index,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    queries.append(b);return b
def page(title,*blocks,brk=True,level='page'):
    pg={'title':title,'kind':'body','blocks':list(blocks)}
    if not brk:pg['break']=False
    if level!='page':pg['level']=level
    pages.append(pg)
def section(title,*blocks):page(title,*blocks,brk=False,level='section')
FIG='assets/figures/chapter06/'
PATHS='login.php\nrobots.txt\nadmin/\n'+'\n'.join(f'book06-scan-{i:02d}' for i in range(1,21))
DEVTOOLS='''GET wazuh-alerts-*/_search
{
  "size": 0,
  "query": {"bool": {"filter": [
    {"term": {"agent.name": "web"}},
    {"range": {"timestamp": {
      "gte": "2026-11-01T21:31:58+09:00",
      "lte": "2026-11-01T21:32:32+09:00"}}}
  ]}},
  "aggs": {"by_src": {
    "terms": {"field": "data.srcip"},
    "aggs": {"by_rule": {"terms": {"field": "rule.id"}}}
  }}
}'''

# ── 장 도입 ───────────────────────────────────────────────────
page('6장  웹 탐색과 인증 공격',
    p('Wazuh 경보 목록에 Web server 400 error code(31101)가 30초 사이에 수십 건 쌓였다. 한 건씩 열면 모두 “없는 페이지를 요청했다”는 기록이다. 한 건만 보면 오타와 구별되지 않는다. 출발지와 시각으로 묶어 보면 누가 무엇을 찾았는지, 그리고 경보에는 없는 무엇을 찾아냈는지가 드러난다.'),
    p('6장의 앞부분에서는 경로 탐색, 헤더·메서드 변경, 긴 URL, 암호 추측 요청을 보내고 공격 일지에 적는다. 뒷부분에서는 공격 일지를 덮고 경보만으로 다시 시작한다. 분포를 읽고, 값으로 거르고, 출발지로 묶고, 시간순으로 늘어놓아 공격자의 행동을 재구성한 뒤 공격 일지와 맞춰 본다. Module 01 실습 04~06, 13~15에 해당한다.'),
    h('학습 목표'),
    ul('경로 탐색·User-Agent 변경·HTTP 메서드·긴 URL·암호 추측 요청을 보내고, 각 요청의 응답과 Wazuh·WAF의 분류를 대조한다.',
       '표식 없이 경보를 출발지·규칙·응답 코드별로 세고, 한 출발지로 피벗해 시간순 행동을 재구성한다.',
       '경보 인덱스에 없는 성공 요청과 인증 요청을 아카이브에서 찾아, 공격자가 무엇을 얻었는지 판단한다.'),
    img(FIG+'rev01-roadmap.png','도식 6-1. 6장 학습 순서.',120),
    h('준비와 완료 기준'),
    tab(['항목','내용'],[
        ['실행 위치','Windows 브라우저, 공격자 VM(경로 탐색·선택 curl), kt66 VM 터미널'],
        ['선행 조건','5장의 DVWA 접속·학습용 DB, hosts 등록, 사건 노트'],
        ['완료 기준','공격 일지와, 경보만으로 재구성한 타임라인(6.7)을 대조해 일치·불일치를 적는다.'],
        ['결과가 다를 때','6.9의 증상별 확인 순서를 따른다.'],
        ['원상복구','6.9에서 User-Agent·학습 단계를 되돌리고 경로 목록 파일을 지운다.']],[32,95],keep=True))

# ── 6.1 ──────────────────────────────────────────────────────
section('6.1  준비',
    ol('Windows 브라우저로 http://dvwa.kt66.lab/login.php에 접속해 로그인한다(5.2). **DVWA Security**의 현재 값을 사건 노트에 적고 **Low**로 바꾼다.',
       '개발자 도구의 **Network**를 열고 **Preserve log**를 켠다(5.3).',
       '다른 탭에서 https://192.168.0.189:5601(자신의 kt66 주소)로 Wazuh에 로그인하고 Discover를 연다.'),
    screen('security','화면 6-1. DVWA의 Low 단계.',100),
    p('이 장의 요청은 어느 인덱스에 남는지가 요청마다 다르다. 404·403처럼 경보 규칙에 일치한 요청은 두 인덱스에 모두 있고, 정상 응답(200·302)은 아카이브에만 있다.'),
    tab(['찾을 기록','인덱스 패턴'],[
        ['404·403·긴 URL 등 경보로 분류된 요청','wazuh-alerts-*'],
        ['200·302 응답, 로그인 요청, WAF 감사 기록','wazuh-archives-*']],[70,57]),
    h('공격자 VM의 Gobuster'),
    p('Gobuster는 단어 목록의 각 줄을 URL 경로에 붙여 차례로 요청하고 응답 코드를 출력하는 경로 탐색 도구이다. 1.9의 공격자 VM에서 쓴다. [2]'),
    c('gobuster -h',
      'Gobuster가 설치되어 있는지와 사용할 수 있는 옵션을 확인한다.',
      '-h는 사용법을 출력한다. Ubuntu 22.04의 패키지는 Gobuster 2.0.1이다.',
      '-m, -u, -w, -t, -a 옵션이 보인다. command not found이면 다음 명령으로 설치한다. 3 계열이면 dir 하위 명령을 쓰므로 C06-07의 구문을 그 버전의 도움말로 고친다.',ATT),
    c('sudo apt update\nsudo apt install gobuster',
      '(설치되어 있지 않을 때만) Gobuster를 설치한다.',
      'apt는 Ubuntu의 패키지 관리자이다. update는 설치 가능한 패키지 목록을 갱신하고, install은 지정한 패키지를 설치한다. 설치를 계속할지 물으면 Y를 입력한다.',
      '오류 없이 끝나면 gobuster -h를 다시 실행해 사용법을 확인한다.',ATT),
    c('getent hosts dvwa.kt66.lab',
      '공격자 VM에서 DVWA 이름이 kt66 IP로 해석되는지 확인한다.',
      '5.12와 같은 명령이다. 도메인은 자신의 값으로 바꾼다.',
      'kt66의 WEB_HOST_IP가 나온다. 없으면 5.12의 hosts 등록을 먼저 한다.',ATT))

# ── 6.2 ──────────────────────────────────────────────────────
section('6.2  경로 탐색',
    p('웹 경로 탐색은 파일·디렉터리 이름을 바꿔 가며 요청하고 응답 코드의 차이로 무엇이 있는지 알아내는 작업이다. 공격자는 관리 화면, 설정 파일, 백업 파일처럼 링크로 드러나지 않은 경로를 찾는다. [1]'),
    img(FIG+'path-scan.png','도식 6-2. 경로 탐색과 반복 요청의 기록.'),
    h('브라우저로 하나씩'),
    ol('주소창에 http://dvwa.kt66.lab/login.php?book06=known을 입력한다. 로그인 화면과 Network의 200을 확인한다.',
       '주소를 http://dvwa.kt66.lab/book06-missing으로 바꾼다. 응답 코드와 본문을 읽는다.',
       '관리 화면에 흔히 쓰이는 경로 네 개를 하나씩 입력하고 응답 코드를 적는다: /admin/, /phpmyadmin/, /wp-admin/, /manager/html. 보낸 요청을 공격 일지에 적는다.'),
    screen('path-missing','화면 6-2. 없는 경로의 404 응답.',100),
    q('agent.name: "web"\nAND data.url: ("/admin/" OR "/phpmyadmin/"\nOR "/wp-admin/" OR "/manager/html")',
      '관리 경로 후보 네 개의 경보를 찾는다.',
      '값 자리의 괄호와 OR는 data.url이 넷 중 하나와 일치하는 기록을 고른다. 세 줄을 함께 입력한다.',
      '검증 환경에서는 네 요청 모두 404, 규칙 31101(Web server 400 error code.)이었다.'),
    screen('admin-data','화면 6-3. 관리 경로 후보의 접속 기록.'),
    p('31101은 응답 코드가 4로 시작하면 붙는다. 잘못 입력한 주소나 끊어진 링크도 같은 경보를 만든다. 경로 탐색인지는 한 건이 아니라 같은 출발지의 앞뒤 기록을 함께 보고 판단한다(6.7).'),
    h('Gobuster로 목록 탐색'),
    p('공격자 VM 홈 디렉터리에 탐색할 경로 목록을 만든다. 처음 세 줄은 실제로 있을 수 있는 경로이고, 나머지 20줄은 없는 경로이다. 복사용 목록은 examples/rev01/chapter06/paths.txt이다.'),
    c('ls -l ~/book06-paths.txt',
      '(사전 확인) 같은 이름의 파일이 이미 있는지 확인한다.',
      '물결표(~)는 현재 사용자의 홈 디렉터리이다.',
      'No such file or directory가 나오면 새로 만든다. 파일이 있으면 내용을 확인하고 다른 이름을 정해 이후 명령에서 모두 바꾼다.',ATT),
    c('nano ~/book06-paths.txt',
      '경로 목록 파일을 만든다.',
      'nano는 터미널 편집기이다. 아래 목록을 한 줄에 하나씩 23줄 입력한다. … 자리에는 book06-scan-02부터 19까지가 차례로 들어간다. **Ctrl+O**, **Enter**로 저장하고 **Ctrl+X**로 닫는다.',
      '편집기가 닫히고 프롬프트로 돌아온다.',ATT),
    code('login.php\nrobots.txt\nadmin/\nbook06-scan-01\n…\nbook06-scan-20'),
    c('cat ~/book06-paths.txt',
      '(사후 확인) 저장된 목록을 확인한다.',
      'cat은 파일 내용을 출력한다.',
      '23줄이 나온다. URL 전체가 아니라 경로만 들어 있어야 한다.',ATT),
    tab(['옵션','뜻'],[
        ['-m dir','디렉터리·파일 경로 탐색 모드'],
        ['-u URL','탐색할 사이트의 기본 주소'],
        ['-w 파일','후보 경로를 읽을 단어 목록'],
        ['-t 1','동시에 요청하는 작업 수를 1로 제한'],
        ['-a 문자열','요청의 User-Agent 헤더 값']],[30,97],keep=True),
    c('gobuster -m dir \\\n  -u http://dvwa.kt66.lab/ \\\n  -w ~/book06-paths.txt -t 1 -a book06-scan',
      '목록의 경로를 차례로 요청한다.',
      '옵션은 위 표와 같다. -a로 User-Agent를 book06-scan으로 바꿔 Gobuster의 요청을 원본 로그에서 구분할 수 있게 한다. 줄 끝의 역슬래시(\\)는 명령을 다음 줄로 잇는다.',
      '검증 환경에서는 /login.php (Status: 200)와 /robots.txt (Status: 200) 두 줄이 출력되었다. 실행 시각을 공격 일지에 적는다.',ATT),
    box('blind','Gobuster는 기본적으로 200·204·301·302·307·403 응답만 화면에 출력한다. 404인 경로는 화면에 나오지 않지만 웹 서버 로그에는 모두 남는다. 반대로 Wazuh 경보에는 404만 남고, 공격자가 찾아낸 200 경로는 경보에 나오지 않는다(6.7).'),
    q('agent.name: "web" AND rule.id: "31151"',
      '같은 출발지의 반복된 4xx 경보를 찾는다.',
      '31151은 같은 출발지에서 31101이 짧은 시간에 반복되면 붙는 규칙이다. 기간은 Gobuster 실행 시각의 앞뒤 1분으로 지정한다.',
      '검증 환경에서 한 건이 나왔다. data.srcip가 공격자 VM의 주소이다.'),
    screen('scan-rule','화면 6-4. 반복된 4xx 응답 경보.'),
    p('31151의 조건은 frequency 14, timeframe 90초, same_source_ip이다. 직전 90초의 다른 4xx 요청도 함께 세므로 목록의 몇 번째 요청에서 붙는지는 앞선 요청에 따라 달라진다. 31151은 별도 경보가 추가되는 것이 아니라 조건을 채운 그 404 요청 한 건에 31101 대신 붙는다. 정의는 6.8에서 확인한다. [3]'))

# ── 6.3 ──────────────────────────────────────────────────────
section('6.3  헤더와 메서드 바꾸기',
    h('User-Agent'),
    p('User-Agent는 클라이언트가 자신의 프로그램 종류를 알리는 HTTP 헤더이다. 접속 로그 맨 끝에 기록되며, 요청자가 마음대로 바꿀 수 있다. Chrome의 값을 SQL 인젝션 도구 sqlmap의 이름으로 바꿔 요청을 보낸다. 여기서 sqlmap은 실행하지 않고 이름만 헤더 값으로 쓴다.'),
    img(FIG+'user-agent.png','도식 6-3. User-Agent 검사와 로그 검색.'),
    ol('개발자 도구에서 **⋮** → **More tools** → **Network conditions**를 연다.',
       '**User agent**의 **Use browser default**를 끄고 Custom 칸에 sqlmap/1.0 book06-ua를 넣는다.',
       '주소창에 http://dvwa.kt66.lab/book06-ua를 입력한다. Network에서 Request Headers의 User-Agent와 Status Code를 확인하고 공격 일지에 적는다.',
       '**Use browser default**를 다시 켠다.'),
    screen('ua-settings','화면 6-5. 사용자 지정 User-Agent.',100),
    q('agent.name: "web" AND data.url: "/book06-ua"\nAND full_log: "sqlmap"',
      'User-Agent에 sqlmap이 들어간 요청을 찾는다.',
      'User-Agent는 별도 필드로 추출되지 않으므로 원문 full_log에서 찾는다.',
      'data.id가 403이고 full_log 끝에 sqlmap/1.0 book06-ua가 있다.'),
    q('agent.name: "web"\nAND location: "/var/log/apache2/modsec_audit.log"\nAND data.request.request_line: *book06-ua*',
      '같은 요청의 WAF 감사 기록을 찾는다.',
      '5.6과 같은 형식이다.',
      'intercepted: true, 응답 403이다. messages에 913100과 949110이 있다.',index='wazuh-archives-*'),
    screen('ua-waf-action','화면 6-6. User-Agent 요청에 대한 WAF의 차단 결정.'),
    p('CRS 규칙 913100은 User-Agent에서 알려진 스캐너 이름을 찾고, 949110은 누적 점수로 차단한다. 이 기록으로 확인한 사실은 “sqlmap이라는 문자열을 보냈다”이다. 실제로 어떤 도구가 요청했는지는 요청 간격·순서 같은 행동 패턴으로 판단한다. [5]'),
    h('HTTP 메서드'),
    p('HTTP 메서드는 요청의 동작을 나타낸다. GET은 조회, POST는 제출이고, PROPFIND는 WebDAV(HTTP로 원격 파일을 관리하는 확장 규약)에서 자원의 속성을 조회하는 메서드이다. DVWA에는 PROPFIND를 보내는 버튼이 없으므로 개발자 도구의 **Console**에서 JavaScript로 한 건을 보낸다. [8][9]'),
    img(FIG+'method.png','도식 6-4. 메서드와 허용 정책 비교.'),
    code("fetch('/book06-method', {method: 'PROPFIND'})\n  .then(r => console.log(r.status));"),
    tab(['구문','뜻'],[
        ['fetch(주소, 설정)','HTTP 요청을 보낸다. /로 시작하는 주소는 현재 사이트의 경로이다.'],
        ["{method: 'PROPFIND'}",'요청 설정. method 값으로 메서드를 정한다.'],
        ['.then(r => console.log(r.status))','응답 r이 도착하면 상태 코드를 Console에 출력한다.']],[52,75],keep=True),
    p('login.php 탭에서 **Console**을 열고 위 식을 입력한 뒤 Enter를 누른다(B06-06-method.txt). 줄을 바꿀 때는 **Shift+Enter**를 쓴다.'),
    screen('method-console','화면 6-7. PROPFIND 요청과 403 응답.',100),
    q('agent.name: "web" AND data.protocol: "PROPFIND"\nAND data.url: "/book06-method"',
      'PROPFIND 요청의 경보를 찾는다.',
      'data.protocol은 웹 접속 로그에서 HTTP 메서드이다.',
      'data.protocol PROPFIND, data.id 403이다. 같은 경로로 감사 기록을 찾으면(Q06-04의 마지막 조건을 *book06-method*로 바꾼다) messages에 911100과 949110이 있다.'),
    p('CRS 911100은 허용 메서드 목록에 없는 메서드를 탐지한다. WebDAV를 쓰는 서비스에서 PROPFIND는 정상 요청이므로, 서비스가 제공하는 기능과 허용 메서드를 기준으로 판단한다. [5]'))

# ── 6.4 ──────────────────────────────────────────────────────
section('6.4  긴 URL',
    p('매우 긴 URL은 버퍼 처리 오류나 요청 크기 제한을 노리는 요청에서 나타난다. 문자 A 8,000개를 쿼리 값으로 한 번 보낸다. Apache의 LimitRequestLine은 요청 줄의 크기를 제한하며 기본값은 8,190바이트이다. [10]'),
    code("location.href = '/?book06-long=' + 'A'.repeat(8000);"),
    p('login.php 탭의 Console에 입력한다(B06-11-long.txt). location.href는 현재 탭이 이동할 주소이고, \'A\'.repeat(8000)은 A를 8,000번 반복한 문자열, +는 두 문자열을 잇는다.'),
    q('agent.name: "web" AND rule.id: "31115"\nAND data.url: *book06-long*',
      '긴 URL 경보를 찾는다.',
      '31115는 로그 이벤트의 크기 조건(maxsize)으로 일치하는 규칙이다.',
      '검증 환경에서 data.id 200, rule.id 31115(URL too long…)였다.'),
    screen('long-rule','화면 6-8. 긴 로그 이벤트의 경보.'),
    img(FIG+'length.png','도식 6-5. HTTP 요청 줄과 접속 로그의 길이.'),
    p('검증 기록에서 요청 줄은 8,027바이트, 접속 로그 원문은 8,228바이트였다. 31115의 maxsize="7900"은 URL 길이가 아니라 로그 이벤트 전체의 크기를 비교한다. 이 요청은 200으로 처리되었으므로 WAF에서 멈추지 않았고, 응답 본문은 일반 로그인 화면이다. 경보 수준이 13으로 높아도 도달 지점(5.9)과 결과는 따로 판단한다.'))

# ── 6.5 ──────────────────────────────────────────────────────
section('6.5  인증 시도',
    p('암호 추측 공격은 후보 암호를 반복해 제출해 인증을 통과하는 값을 찾는 공격이다. DVWA의 일반 로그인과 Brute Force 실습 메뉴에 후보 세 개를 한 번씩 넣는다. 세 번째가 실제 암호이다. [6]'),
    img(FIG+'login-flow.png','도식 6-6. DVWA 로그인 응답의 분기.'),
    tab(['순서','Username','Password'],[['1','admin','book06-wrong1'],['2','admin','book06-wrong2'],['3','admin','password']],[20,40,67]),
    h('일반 로그인'),
    ol('**Logout**을 누르고 Network를 비운다.',
       '세 후보를 차례로 입력하고 **Login**을 누른다. 각 시각을 공격 일지에 적는다.',
       'Network에서 POST login.php 행마다 Status Code와 Response Headers의 Location을 읽는다.'),
    screen('login-failed-headers','화면 6-9. 실패한 로그인 요청의 302 응답.'),
    tab(['구분','실패','성공'],[['POST 응답','302','302'],['Location','login.php','index.php'],['도착 화면','Login failed','Home']],[30,48,49],keep=True),
    p('실패와 성공 모두 302이다. 결과는 Location과 도착 화면이 알려 준다.'),
    h('Brute Force 메뉴'),
    p('로그인한 상태에서 **Brute Force**를 누르고 같은 세 후보를 넣는다. 이 Low 단계 실습은 사용자명과 암호를 GET 쿼리로 보낸다. 틀리면 Username and/or password incorrect., 맞으면 Welcome to the password protected area admin이 나온다.'),
    screen('brute-success','화면 6-10. 올바른 암호의 결과.',100),
    p('세 요청 모두 200이다. 결과는 응답 본문의 문구로만 구분된다.'),
    box('predict','여섯 번의 인증 시도 중 Wazuh 경보가 된 것은 몇 건일까? 6.6으로 넘어가기 전에 예측을 적는다.'),
    q('agent.name: "web" AND data.protocol: "POST"\nAND data.url: "/login.php"',
      '일반 로그인 제출 요청을 찾는다.',
      '인덱스 패턴을 wazuh-archives-*로 바꾼다. 경보 인덱스에서는 0건이다.',
      '세 POST 요청이 나오고 모두 302이다.',index='wazuh-archives-*'),
    q('agent.name: "web"\nAND data.url: *vulnerabilities/brute/*\nAND data.url: *username=admin*',
      'Brute Force 메뉴의 인증 시도를 찾는다.',
      '경로와 admin 입력을 함께 찾는다.',
      '세 요청이 나오고 모두 200이다. URL에 password=… 값이 그대로 남아 있다.',index='wazuh-archives-*'),
    screen('brute-data','화면 6-11. Brute Force 요청의 쿼리 값.'),
    box('blind','여섯 번의 인증 시도는 어느 것도 경보가 되지 않았다. 302와 200은 4xx가 아니고, 접속 로그에는 POST 본문의 사용자명·암호도, 응답의 Location도, 성공·실패 문구도 없다. 웹 애플리케이션의 인증 시도는 애플리케이션이 계정·결과를 따로 기록해야 조사할 수 있다. GET으로 보낸 암호는 반대로 접속 로그와 아카이브에 그대로 남는다.'))

# ── 6.6 ──────────────────────────────────────────────────────
section('6.6  분포와 필터: 경보만으로 다시 보기',
    p('이제 공격 일지를 덮는다. 실제 조사에서는 공격자가 무엇을 했는지 모른 채 경보 목록에서 출발한다. 표식(book06-…)도 쓰지 않는다. 6.1~6.5를 실행한 시간 전체를 Absolute로 지정하고 경보부터 본다.'),
    box('predict','이 시간 범위의 경보에는 출발지가 몇 개 있을까? 가장 많은 경보를 만든 출발지는 어디일까?'),
    q('agent.name: "web"',
      '실습 시간대의 web 경보 전체를 본다.',
      '조건을 에이전트 하나로만 두고 나머지는 시간 범위로 제한한다.',
      '검증 환경(21:31:58~21:32:32)에서는 30건이었다.'),
    h('필드 분포 읽기'),
    p('Discover 왼쪽 필드 목록에서 필드 이름 옆의 세부 정보 버튼을 누르면 현재 결과에서 그 필드의 상위 값(Top 5 values)과 비율이 나온다. data.srcip, rule.id, data.id 순서로 연다.'),
    slot('촬영 자리 · 화면 6-12','Discover 왼쪽 필드 목록에서 data.srcip의 세부 정보를 연 화면. 상위 값 두 개(공격자 VM, 브라우저 경로)와 비율이 보이게 촬영한다.'),
    tab(['필드','상위 값과 건수 (검증 환경 30건)'],[
        ['data.srcip','192.168.0.202 22 · 10.20.30.254 8'],
        ['rule.id','31101 28 · 31151 1 · 31115 1'],
        ['data.id','404 27 · 403 2 · 200 1'],
        ['data.protocol','GET 29 · PROPFIND 1']],[30,97],keep=True),
    p('분포만으로 첫 판단이 선다. 30건 중 22건이 한 출발지에서 왔고, 대부분이 404이다. 403 두 건과 PROPFIND 한 건은 다른 출발지의 소수 요청이다.'),
    h('값으로 거르기'),
    p('결과 한 행을 펼치고 data.srcip 줄에 마우스를 올리면 돋보기 모양의 **Filter for value**(+)와 **Filter out value**(−) 버튼이 나온다. +를 누르면 검색창 아래에 data.srcip: 192.168.0.202 필터가 붙고 그 출발지의 경보만 남는다. −를 누르면 그 값을 제외한다. 필터는 검색식을 고치지 않고 조건을 더하거나 뺄 때 쓴다. 필터 이름을 눌러 **Exclude results**로 반전하거나 **Temporarily disable**로 잠시 끌 수 있다.'),
    slot('촬영 자리 · 화면 6-13','상세 기록의 data.srcip 줄에서 Filter for value(+)를 누른 직후. 검색창 아래 필터와 22건으로 줄어든 결과 수가 함께 보이게 촬영한다.'),
    p('필터를 붙인 상태에서 다시 rule.id 분포를 보면 31101 21, 31151 1이다. 이 출발지는 404만 받았다.'),
    h('집계로 세기(선택)'),
    p('필드 분포는 현재 결과의 표본에서 계산된다. 기록이 많거나 출발지별·규칙별로 함께 세려면 Indexer에 직접 집계를 요청한다. Wazuh 메뉴 **Indexer management** → **Dev Tools**에서 다음 요청을 보낸다. 복사용 파일은 examples/rev01/chapter06/D06-01.json이다.'),
    q(DEVTOOLS,
      '시간 범위 안의 web 경보를 출발지별로, 그 안에서 규칙별로 센다.',
      'GET 인덱스/_search는 검색 요청이다. size 0은 문서를 돌려받지 않고 집계만 받는다. bool.filter는 에이전트 이름과 시간 범위 조건이다. aggs의 terms는 필드 값별 건수를 세고, 안쪽 aggs가 출발지마다 rule.id를 다시 센다. 요청 줄 오른쪽의 실행 버튼(▶)을 누른다.',
      'aggregations.by_src.buckets에 출발지별 doc_count가, 각 버킷의 by_rule에 규칙별 건수가 나온다. 저장된 검증 기록으로 세면 192.168.0.202는 22건(31101 21, 31151 1), 10.20.30.254는 8건(31101 7, 31115 1)이다.',qid='D06-01',where='Windows · Indexer management · Dev Tools'))

# ── 6.7 ──────────────────────────────────────────────────────
section('6.7  피벗과 타임라인',
    p('피벗은 한 단서에서 같은 값을 가진 다른 기록으로 옮겨 가며 범위를 넓히는 조사 방법이다. 가장 많은 경보를 만든 출발지 192.168.0.202를 단서로 삼는다.'),
    q('agent.name: "web" AND data.srcip: "192.168.0.202"',
      '한 출발지의 경보를 시간순으로 읽는다.',
      'Time 열 머리글을 눌러 오래된 순으로 정렬하고 data.url, data.id, rule.id 열을 추가한다(3.5).',
      '22건이 21:32:02.191부터 .243 사이, 0.05초 안에 몰려 있다. 첫 요청은 무작위 문자열 경로이고, 이어서 /admin/, /book06-scan-01~20이 순서대로 나온다.'),
    box('field','0.05초에 22건은 사람이 주소창에 입력하는 속도가 아니다. 간격이 일정하고 경로가 목록 순서대로이면 자동 도구의 탐색이다. 첫 요청의 무작위 경로는 Gobuster가 시작할 때 “없는 경로에 서버가 어떻게 응답하는지” 확인하는 요청이다. full_log 끝의 User-Agent(검증 환경 book06-scan)도 단서가 되지만 바꿀 수 있는 값이다.'),
    box('predict','경보에는 404만 있다. 이 출발지는 아무것도 찾지 못했을까?'),
    q('agent.name: "web" AND data.srcip: "192.168.0.202"\nAND NOT data.id: "404"',
      '같은 출발지의 요청 중 404가 아닌 것을 아카이브에서 찾는다.',
      '인덱스 패턴을 wazuh-archives-*로 바꾼다. NOT은 뒤의 조건을 만족하지 않는 기록을 고른다.',
      '검증 환경에서 세 건이 나왔다: / (302), /login.php (200), /robots.txt (200). 공격자가 찾아낸 경로이다.',index='wazuh-archives-*'),
    box('blind','공격자가 찾아낸 경로(200)는 경보 인덱스에 없고 아카이브에만 있다. 경로 탐색을 조사할 때 경보만 보면 “무엇을 찾으려 했는지”는 알 수 있어도 “무엇을 찾아냈는지”는 놓친다. 같은 출발지의 200 응답을 아카이브에서 따로 확인한다.'),
    h('두 번째 출발지'),
    p('10.20.30.254의 경보 8건은 없는 경로·관리 경로 404 다섯 건, User-Agent·메서드 403 두 건, 긴 URL 한 건이다. 아카이브에서 같은 출발지의 인증 요청을 찾는다.'),
    q('agent.name: "web" AND data.srcip: "10.20.30.254" AND\n((data.protocol: "POST" AND data.url: "/login.php")\nOR data.url: *username=*)',
      '같은 출발지의 로그인 제출과 GET 인증 시도를 함께 찾는다.',
      '안쪽 괄호는 “POST이면서 /login.php”를 한 조건으로 묶고, OR로 username=이 든 URL을 더한다. 10.20.30.254는 자신의 data.srcip로 바꾼다.',
      '검증 환경에서 여섯 건이다. 세 번째 POST와 같은 시각에 같은 출발지의 GET /index.php가 있다(검색 조건을 빼고 그 시각 앞뒤를 보면 나온다). 그 POST가 로그인 성공이다. Brute Force의 세 번째 요청 URL에는 password=password가 보인다.',index='wazuh-archives-*'),
    img(FIG+'rev01-timeline.png','도식 6-7. 검증 환경의 출발지별 타임라인.'),
    h('공격 일지와 대조'),
    tab(['공격 일지','경보만으로 찾았는가','찾은 곳'],[
        ['Gobuster 목록 탐색','예 · 31101·31151','경보'],
        ['Gobuster가 찾은 200 경로','아니요','아카이브(NOT 404)'],
        ['없는·관리 경로 5건','예 · 31101','경보'],
        ['User-Agent·PROPFIND','예 · 31101(403)','경보 + WAF 감사'],
        ['긴 URL','예 · 31115','경보'],
        ['로그인 3회·Brute Force 3회','아니요','아카이브'],
        ['로그인 성공 여부','아니요','브라우저 화면·애플리케이션']],[48,40,39],keep=True),
    p('공격 일지에만 있고 경보에는 없는 행이 탐지 공백이다. 11장에서 모든 장의 공백을 모아 규칙 보완 후보를 정한다. 4장에서처럼 사용자 규칙을 만들면, 예를 들어 같은 출발지의 POST /login.php 302가 짧은 시간에 반복될 때 경보를 붙일 수 있다.'))

# ── 6.8 ──────────────────────────────────────────────────────
section('6.8  원본 로그와 정의 확인',
    p('Discover에서 찾은 요청과 규칙을 서버의 원본 파일과 정의로 확인한다.'),
    c('docker exec -it kt66-web /bin/bash',
      'kt66-web 컨테이너의 셸로 들어간다.',
      '5.4와 같은 명령이다.',
      '프롬프트가 kt66-web 안으로 바뀐다.',HOST),
    c("grep -F 'book06-scan' /var/log/apache2/dvwa_access.log",
      'Gobuster 요청의 원본 접속 로그를 읽는다.',
      'grep -F로 User-Agent 표식을 글자 그대로 찾는다.',
      '각 줄의 출발지·시각·경로·응답 코드와 끝의 "book06-scan"을 읽는다. 404 줄 사이에 /login.php와 /robots.txt의 200 줄도 있다.',WEB),
    code('192.168.0.202 - - [01/Nov/2026:21:32:00 +0900]\n"GET /book06-scan-01 HTTP/1.1"\n404 451 "-" "book06-scan"'),
    c('exit',
      'kt66-web 셸에서 나온다.',
      'exit는 현재 셸을 끝낸다.',
      'kt66 VM의 프롬프트로 돌아온다.',WEB),
    c('docker exec -it kt66-siem /bin/bash',
      'kt66-siem 컨테이너의 셸로 들어간다.',
      '4.5와 같은 명령이다.',
      '프롬프트가 kt66-siem 안으로 바뀐다.',HOST),
    c("sed -n '/<rule id=\"31151\"/,/<\\/rule>/p' \\\n  /var/ossec/ruleset/rules/0245-web_rules.xml",
      '반복 4xx 규칙 31151의 정의 전체를 읽는다.',
      'sed는 텍스트의 줄을 골라 출력하거나 바꾸는 도구이다. -n은 자동 출력을 끄고, 끝의 p는 선택한 줄을 출력한다. /시작/,/끝/은 시작 패턴이 있는 줄부터 끝 패턴이 있는 줄까지를 고른다. 끝 패턴의 \\/는 슬래시(/) 문자 자체를 뜻한다. 작은따옴표는 식 전체를 셸이 해석하지 않고 sed에 넘긴다.',
      'rule id="31151" level="10" frequency="14" timeframe="90", if_matched_sid 31101, same_source_ip, 설명, 그룹 web_scan·recon이 나온다.',SIEM),
    p('31151의 그룹에는 web_scan과 recon(정찰)이 있다. rule.groups: "web_scan"으로 검색하면 규칙 번호를 몰라도 경로 탐색 계열 경보를 모을 수 있다.'),
    c('exit',
      'kt66-siem 셸에서 나온다.',
      'C06-10과 같다.',
      'kt66 VM의 프롬프트로 돌아온다.',SIEM),
    c('docker exec -it kt66-dvwa /bin/bash',
      'DVWA 애플리케이션 컨테이너의 셸로 들어간다.',
      '컨테이너 이름만 다르다.',
      '프롬프트가 kt66-dvwa 안으로 바뀐다.',HOST),
    c("grep -nE 'checkToken|generateSessionToken|dvwaRedirect' \\\n  /var/www/html/login.php\ngrep -nE 'GET|Welcome|incorrect' \\\n  /var/www/html/vulnerabilities/brute/source/low.php",
      '두 로그인 기능이 입력을 받고 결과를 나누는 코드를 찾는다.',
      '-n은 줄 번호, -E는 확장 정규표현식이다. 이 정규표현식에서 파이프(|)는 또는(OR)을 뜻한다. 파일은 읽기만 한다.',
      'login.php에서 토큰 확인(checkToken)과 login.php·index.php로의 이동(dvwaRedirect)이, low.php에서 $_GET으로 username·password를 읽고 Welcome·incorrect 문구로 나누는 줄이 나온다.',DVWA),
    p('$_GET은 URL 쿼리, $_POST는 폼 본문의 값을 읽는 PHP 변수이다. 일반 로그인 폼의 user_token은 세션 값과 폼 값을 대조하는 CSRF(사이트 간 요청 위조) 방지 토큰으로, 폼을 다시 열 때마다 바뀐다. [7]'),
    c('exit',
      'kt66-dvwa 셸에서 나온다.',
      'C06-10과 같다.',
      'kt66 VM의 프롬프트로 돌아온다.',DVWA))

# ── 6.9 ──────────────────────────────────────────────────────
section('6.9  결과가 다를 때와 원상복구',
    tab(['증상','확인 순서'],[
        ['Gobuster가 시작하지 못한다','-h로 버전·옵션 → 목록 파일 경로 → 이름 해석(C06-03)'],
        ['31151이 없다','개별 404 기록 → 같은 출발지인지 → 90초 안의 4xx 건수'],
        ['필드 분포에 값이 없다','시간 범위 → 인덱스 패턴 → 그 필드가 있는 기록인지(3.4)'],
        ['Dev Tools 집계가 0이다','시간대 표기(+09:00) → 인덱스 이름 → agent.name 값'],
        ['인증 요청이 안 보인다','인덱스 패턴을 wazuh-archives-*로 바꿨는지'],
        ['긴 요청이 414 또는 403','Network의 실제 URL 길이 → 요청 줄 제한 → WAF 감사 기록']],[45,82],keep=True),
    h('원상복구'),
    ol('Network conditions의 **Use browser default**가 켜져 있는지 확인한다.',
       '**DVWA Security**를 6.1에서 적은 값으로 되돌리고 **Logout**을 누른다.',
       'Discover의 필터와 검색식을 비우고 wazuh-alerts-*, Last 24 hours로 되돌린다.'),
    c('cat ~/book06-paths.txt\nrm -i ~/book06-paths.txt\nls -l ~/book06-paths.txt',
      '공격자 VM에서 이번에 만든 경로 목록을 확인하고 지운다.',
      'cat으로 지울 파일이 이번 목록인지 확인한다. rm -i는 지우기 전에 확인을 묻는다. 표시된 경로가 맞으면 y를 입력한다.',
      '마지막 ls -l이 No such file or directory를 출력한다.',ATT),
    {'type':'image','path':'assets/illustrations/chapter06/log-review.png','caption':'삽화. 요청 기록 검토.','width_mm':45,'align':'right'},
    p('조사 기록 양식은 examples/rev01/chapter06/investigation.txt이다. 6.7의 대조 표를 사건 노트에 옮긴다.'))

# ── 6.10 ─────────────────────────────────────────────────────
section('6.10  선택 실습: curl로 헤더와 메서드 지정',
    p('브라우저에서 한 헤더·메서드 시험을 공격자 VM의 curl로 보낸다. -A는 User-Agent를, -X는 메서드를 지정한다. 나머지 옵션은 5.12와 같다. [11]'),
    c('curl -i --max-time 15 \\\n  -A "sqlmap/1.0 book06-curl-ua" \\\n  http://dvwa.kt66.lab/book06-curl-ua',
      'User-Agent를 바꾼 요청을 보낸다.',
      '큰따옴표는 공백이 든 헤더 값을 하나의 인자로 묶는다.',
      '검증 환경에서는 HTTP/1.1 403 Forbidden이었다. Discover에서 data.url: *book06-curl-ua*로 찾고 WAF 메시지 913100을 확인한다.',ATT),
    c('curl -i --max-time 15 -X PROPFIND \\\n  http://dvwa.kt66.lab/book06-curl-method',
      'PROPFIND 메서드로 요청한다.',
      '-X 뒤의 값이 요청 메서드가 된다.',
      '검증 환경에서는 403이었다. data.url: *book06-curl-method*로 찾고 data.protocol PROPFIND와 WAF 메시지 911100을 확인한다.',ATT),
    p('두 요청을 공격 일지에 적는다. 브라우저 요청과 출발지가 다르므로 6.7의 피벗을 공격자 VM 주소로 다시 해 본다. 브라우저의 fetch는 TRACE 같은 일부 메서드를 보낼 수 없지만 curl은 보낼 수 있다.'))

# ── 장 끝 ─────────────────────────────────────────────────────
page('6장 정리',
    h('핵심 정리'),
    ul('경로 탐색의 404는 경보(31101·31151)가 되지만, 공격자가 찾아낸 200 경로는 아카이브에만 있다. 같은 출발지의 NOT 404를 아카이브에서 확인한다.',
       '웹 로그인 시도는 302·200 응답이라 경보가 되지 않는다. 접속 로그에는 POST 본문과 결과가 없으므로 인증 결과는 Location·화면·애플리케이션 기록으로 판단한다.',
       '경보 분석은 분포 읽기 → 값 필터 → 집계 → 피벗 → 타임라인 순서로 한다. 요청 간격과 순서는 자동 도구를 구분하는 단서이다.',
       '공격 일지와 경보로 재구성한 타임라인의 차이가 탐지 공백이다.'),
    h('확인 문제'),
    ol('31101 경보만 보고 경로 탐색과 오타를 어떻게 구분하는가?',
       '경로 탐색 경보에는 404만 있다. 공격자가 찾아낸 경로는 어떻게 찾는가?',
       '로그인 POST 요청이 모두 302이다. 어느 것이 성공인지 접속 로그만으로 알 수 있는가?',
       'data.srcip로 필터를 건 뒤 다른 인덱스 패턴에서 같은 출발지를 찾으려면 무엇을 확인하는가?',
       'User-Agent에 sqlmap이 있다. sqlmap이 실행되었다고 쓸 수 있는가?'),
    h('확인 문제 해설'),
    ol('같은 출발지·짧은 시간 범위로 피벗해 요청 수, 간격, 경로 순서를 본다. 0.05초에 수십 건이 목록 순서대로이면 자동 탐색이다.',
       '아카이브에서 같은 출발지의 NOT data.id: "404"를 검색한다(Q06-11).',
       '알 수 없다. 응답의 Location(index.php)과 그 뒤 요청(index.php 등)의 순서로 추정하고, 화면·애플리케이션 기록으로 확인한다.',
       '필터는 인덱스 패턴을 바꾸면 다시 확인해야 한다. 검색창에 data.srcip 조건을 직접 적는 편이 확실하다.',
       '쓸 수 없다. User-Agent는 요청자가 바꿀 수 있는 값이다. 이 장의 실습처럼 브라우저로도 넣을 수 있다. 요청 패턴과 단말의 실행 기록을 함께 본다.'),
    h('더 읽을거리'),
    p('OpenSearch의 terms 집계 문서이다. 6.6의 Dev Tools 요청에서 size·order로 상위 몇 개를 어떤 순서로 받을지 정하는 법을 읽는다.'),
    link('OpenSearch 2.16 · Terms aggregation','https://docs.opensearch.org/2.16/aggregations/bucket/terms/'),
    p('OWASP 테스트 가이드의 웹 서버 메타파일·경로 탐색 항목이다. 6.2에서 robots.txt가 왜 탐색 목록에 들어가는지 읽는다.'),
    link('OWASP WSTG · Review Webserver Metafiles','https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/03-Review_Webserver_Metafiles_for_Information_Leakage'))

section('6장 참고 자료',
    p('화면과 결과는 Wazuh 4.10.0의 기존 kt66과 DVWA v1.10에서 2026년 11월 1일 21:31~21:33(KST)에 기록했다.'),
    h('[1] 경로 탐색'),
    link('OWASP · Forced browsing','https://owasp.org/www-community/attacks/Forced_browsing'),
    h('[2] Gobuster 2.0.1'),
    link('Gobuster · 2.0.1 README','https://github.com/OJ/gobuster/tree/v2.0.1'),
    h('[3] Wazuh 웹 규칙'),
    link('Wazuh 4.10.0 · 0245-web_rules.xml','https://github.com/wazuh/wazuh/blob/v4.10.0/ruleset/rules/0245-web_rules.xml'),
    h('[4] User-Agent 변경'),
    link('Chrome DevTools · Override the user agent','https://developer.chrome.com/docs/devtools/device-mode/override-user-agent'),
    h('[5] OWASP CRS 3.3.2'),
    link('CRS · 허용 메서드 정책','https://github.com/coreruleset/coreruleset/blob/v3.3.2/rules/REQUEST-911-METHOD-ENFORCEMENT.conf'),
    link('CRS · 스캐너 탐지','https://github.com/coreruleset/coreruleset/blob/v3.3.2/rules/REQUEST-913-SCANNER-DETECTION.conf'),
    h('[6] 암호 추측 공격'),
    link('OWASP · Brute Force Attack','https://owasp.org/www-community/attacks/Brute_force_attack'),
    h('[7] DVWA'),
    link('DVWA · 공식 저장소','https://github.com/digininja/DVWA'),
    h('[8] HTTP 메서드'),
    link('MDN · HTTP request methods','https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods'),
    link('RFC 4918 · WebDAV PROPFIND','https://www.rfc-editor.org/rfc/rfc4918#section-9.1'),
    h('[9] Console과 fetch'),
    link('MDN · Using Fetch','https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch'),
    h('[10] 요청 줄 제한'),
    link('Apache 2.4 · LimitRequestLine','https://httpd.apache.org/docs/2.4/mod/core.html#limitrequestline'),
    h('[11] curl'),
    link('curl · Manual','https://curl.se/docs/manpage.html'))

INVESTIGATION='''웹 탐색·인증 조사 기록

조사 시간 범위(KST):
경보 분포(data.srcip · rule.id · data.id 상위 값):
피벗한 출발지:
그 출발지의 첫·마지막 요청 시각, 건수, 간격:
경보에 없던 성공 요청(아카이브, NOT 404):
인증 요청(경로 · 메서드 · 응답 · Location):
WAF 기록(transaction_id · CRS 규칙 · intercepted):
공격 일지와의 대조(일치 · 경보 없음):
탐지 공백과 규칙 보완 후보:
원상복구(User-Agent · 학습 단계 · 목록 파일):
'''
README='''6장 REV01 복사용 입력

C06-01~ : 명령 블록 번호와 같은 파일. 실행 위치는 manifest.json의 where를 따른다.
Q06-01~ : Discover 검색식. D06-01.json은 Dev Tools 집계 요청이다. queries.json에 설명이 있다.
B06-01~11 : 브라우저 주소창·Console·User-Agent 칸에 넣는 값. 도메인은 자신의 값으로 바꾼다.
paths.txt : Gobuster 경로 목록(23줄)
records/  : 검증 환경에서 기록된 요청별 원문과 경보(읽기 자료)
investigation.txt : 조사 기록 양식
'''

if __name__=='__main__':
    data={'title':'웹 탐색과 인증 공격','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','baseline':COMMIT,'revision':'REV01',
          'comments':'REV01 원고. 공격·화면은 2026-11-01 기존 kt66 실측, 6.6~6.7 건수는 같은 시간 범위의 저장 기록을 센 값. 필드 상세·필터·Dev Tools 화면은 촬영 자리.','pages':pages}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'volume01-chapter06.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    EX.mkdir(parents=True,exist_ok=True)
    for old in list(EX.glob('C06-*.txt'))+list(EX.glob('Q06-*.txt'))+list(EX.glob('D06-*')):old.unlink()
    for b in commands+[x for x in queries if x['id'].startswith('Q')]:(EX/(b['id']+'.txt')).write_text(b['text']+'\n')
    for b in queries:
        if b['id'].startswith('D'):(EX/(b['id']+'.json')).write_text(b['text']+'\n')
    (EX/'manifest.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
    (EX/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2)+'\n')
    for f in (ROOT/'examples/chapter06').glob('B06-*.txt'):shutil.copyfile(f,EX/f.name)
    (EX/'paths.txt').write_text(PATHS+'\n')
    (EX/'records').mkdir(exist_ok=True)
    for f in (ROOT/'examples/chapter06/records').iterdir():shutil.copyfile(f,EX/'records'/f.name)
    (EX/'investigation.txt').write_text(INVESTIGATION)
    (EX/'README.txt').write_text(README)
    print(len(pages),'pages',len(commands),'commands',len(queries),'queries')
