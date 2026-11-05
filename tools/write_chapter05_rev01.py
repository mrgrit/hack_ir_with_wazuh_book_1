"""REV01 · 5장 웹 공격의 시작과 입력값 검증. 저자용이며 실습 명령을 실행하지 않는다.

2026-11-05 개정 기준
- 조사 질문: 입력은 어디까지 전달되었는가. 브라우저 송신 → 웹 서버 도착 → WAF 판정 → 애플리케이션 처리 → 결과의
  다섯 지점과 각 지점의 기록(도식 5-2)을 장 전체의 판정 틀로 쓴다.
- 5장부터 사건 노트의 공격 일지를 쓴다(머리말·1.8). Windows 출발지 IP를 ipconfig로 적고 data.srcip와 대조한다.
- 브라우저·Wazuh 화면과 결과는 2026-11-01 기존 kt66 실측(editorial/chapter05-review.json)을 따른다.
  curl 선택 실습은 이전 검증 기록(editorial/chapter05-curl-review.json)의 명령 문자열을 유지하고 블록만 묶었다.
- 31101·31104·31106의 해석은 Wazuh v4.10.0 0245-web_rules.xml과 대조했다.
"""
import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/REV01'
EX=ROOT/'examples/rev01/chapter05'
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
def screen(name,caption,width=127): return img(f'assets/screens/chapter05/browser/{name}.png',caption,width)
def box(kind,*text,items=None):
    b={'type':'box','kind':kind,'text':list(text)}
    if items:b['items']=items
    return b
def code(t): return {'type':'code','text':t}
def link(text,url): return {'type':'link','text':text,'url':url}
HOST='kt66 VM · 터미널';WEB='kt66-web 컨테이너 · 셸';SIEM='kt66-siem 컨테이너 · 셸';ATT='공격자 VM · 터미널'
def c(text,purpose,syntax,result,where):
    b={'type':'command','id':f'C05-{len(commands)+1:02d}','where':where,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    commands.append(b);return b
def q(text,purpose,syntax,result,index='wazuh-alerts-*'):
    b={'type':'query','id':f'Q05-{len(queries)+1:02d}','where':'Windows · Discover · '+index,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    queries.append(b);return b
def page(title,*blocks,brk=True,level='page'):
    pg={'title':title,'kind':'body','blocks':list(blocks)}
    if not brk:pg['break']=False
    if level!='page':pg['level']=level
    pages.append(pg)
def section(title,*blocks):page(title,*blocks,brk=False,level='section')
FIG='assets/figures/chapter05/'
PAYLOAD="1' UNION SELECT user,password FROM users-- "
CURL='curl -sS -i --max-time 15 --get \\\n'

# ── 장 도입 ───────────────────────────────────────────────────
page('5장  웹 공격의 시작과 입력값 검증',
    p('DVWA의 사용자 조회 칸에 SQL 구문을 넣고 Submit을 눌렀다. Wazuh에는 SQL injection attempt 경보가 생겼다. 데이터베이스의 계정 정보가 빠져나갔을까? 이 경보가 알려 주는 것은 웹 서버 접속 로그의 URL에 SQL 공격 문자열이 있었다는 사실이다. 입력이 웹 방화벽에서 멈췄는지, 애플리케이션까지 갔는지, 데이터베이스가 실제로 실행했는지는 각 지점의 기록을 따로 확인해야 알 수 있다.'),
    p('5장부터는 독자가 공격자이다. SQL 인젝션, XSS, 경로 조작 세 가지 입력을 브라우저로 보내고, 입력이 어디까지 전달되었는지를 응답·접속 로그·WAF 기록으로 판정한다. 보낸 공격은 사건 노트의 공격 일지에 적는다. Module 01 실습 01~03에 해당한다.'),
    h('학습 목표'),
    ul('HTTP 요청의 URL·매개변수·응답 코드를 브라우저 개발자 도구와 Apache 접속 로그에서 읽고 Wazuh 필드와 대응시킨다.',
       'SQL 인젝션·XSS·경로 조작 입력의 동작 원리를 설명하고, 각 요청이 어느 지점까지 도달했는지 근거와 함께 판정한다.',
       'HTTP 응답 코드, WAF의 차단 결정, Wazuh 규칙 번호가 각각 무엇을 알려 주는지 구분한다.'),
    img(FIG+'rev01-roadmap.png','도식 5-1. 5장 학습 순서.',120),
    h('준비와 완료 기준'),
    tab(['항목','내용'],[
        ['실행 위치','Windows 브라우저, kt66 VM 터미널, 공격자 VM(5.12 선택)'],
        ['선행 조건','kt66 기동, Discover 검색(3장), 아카이브 확인(4장), 사건 노트(1.8)'],
        ['대상','자신의 kt66에서 실행되는 DVWA'],
        ['완료 기준','네 공격 요청마다 공격 일지 한 줄과 도달 지점 판정(5.9)을 쓴다.'],
        ['결과가 다를 때','5.10의 증상별 확인 순서를 따른다.'],
        ['원상복구','5.11에서 DVWA 학습 단계와 hosts 변경을 되돌리고 로그아웃한다.']],[32,95],keep=True))

# ── 5.1 ──────────────────────────────────────────────────────
section('5.1  웹 요청이 지나가는 길',
    p('DVWA(Damn Vulnerable Web Application)는 웹 취약점을 학습하도록 일부러 취약하게 만든 웹 애플리케이션이다. kt66은 DVWA를 kt66-dvwa 컨테이너로 실행하고, 그 앞에 웹 서버 컨테이너 kt66-web을 둔다. [1]'),
    p('kt66-web의 Apache는 HTTP 요청을 받아 DVWA로 전달하는 웹 서버이다. Apache에는 WAF(Web Application Firewall)인 ModSecurity가 설치되어 있다. WAF는 웹 요청을 검사해 공격으로 판단한 요청을 차단하는 방화벽이며, kt66은 공개 규칙 모음 OWASP CRS를 차단 모드로 적용한다. [2]'),
    img(FIG+'request-log-path.png','도식 5-2. 웹 요청과 로그 수집 경로.'),
    p('kt66-web은 세 종류의 로그를 남긴다. dvwa_access.log는 요청과 응답 코드, error.log는 처리 오류와 ModSecurity 메시지, modsec_audit.log는 WAF가 검사한 요청의 상세 기록이다. kt66-web의 Wazuh 에이전트(이름 web)가 access 로그와 감사 로그를 Manager로 보낸다.'),
    p('요청이 지나가는 지점마다 남는 기록이 다르다. 입력의 도달 범위는 다음 다섯 지점으로 나누어 판정한다.'),
    img(FIG+'rev01-reach.png','도식 5-3. 입력의 도달 지점과 확인할 기록.'),
    box('blind','Apache 접속 로그는 요청 줄과 응답 코드, 응답 크기를 기록하고 응답 본문은 기록하지 않는다. 데이터베이스가 어떤 SQL을 실행했는지, 브라우저가 스크립트를 실행했는지도 접속 로그에는 없다. 4·5 지점은 응답 본문과 애플리케이션·브라우저의 동작으로 확인한다.'))

# ── 5.2 ──────────────────────────────────────────────────────
section('5.2  DVWA 접속 준비',
    p('같은 kt66 IP에서 여러 웹 사이트가 실행되므로 DVWA는 IP가 아니라 이름(dvwa.<LAB_DOMAIN>)으로 접속한다. 브라우저는 이름을 IP로 바꿔 접속하고, HTTP 요청의 Host 헤더에 이름을 넣어 보낸다. Apache는 Host 값으로 DVWA 사이트를 고른다.'),
    img(FIG+'name-and-host.png','도식 5-4. 웹 이름과 접속 주소.'),
    c("grep -E '^(WEB_HOST_IP|LAB_DOMAIN)=' .env",
      'kt66의 웹 진입 IP와 실습 도메인을 확인한다.',
      'kt66 저장소 디렉터리(~/kt66)에서 실행한다. grep -E는 확장 정규표현식으로 찾는다. 이 정규표현식에서 ^는 줄의 시작, 괄호 안의 파이프(|)는 또는(OR)을 뜻하므로 WEB_HOST_IP= 또는 LAB_DOMAIN=으로 시작하는 줄을 찾는다.',
      '두 줄이 나온다. 값을 사건 노트의 기준 상태와 대조한다. 본문의 예시는 192.168.0.189와 kt66.lab이다.',HOST),
    h('Windows에 이름 등록'),
    p('hosts는 이름과 IP를 직접 연결하는 파일이다. Windows의 hosts에 DVWA 이름과 kt66 IP를 적는다. [11]'),
    ol('시작 메뉴에서 **메모장**을 검색하고, 마우스 오른쪽 버튼으로 **관리자 권한으로 실행**을 누른다.',
       '**파일** → **열기**에서 C:\\Windows\\System32\\drivers\\etc 폴더를 연다. 파일 형식을 **모든 파일**로 바꾸고 hosts를 연다.',
       'dvwa가 들어간 줄이 있는지 찾는다. 있으면 그 줄을 사건 노트에 옮겨 적고, IP와 이름이 맞으면 그대로 둔다. 없으면 맨 끝에 192.168.0.189 dvwa.kt66.lab 형식으로 한 줄을 추가한다.',
       '**Ctrl+S**로 저장하고 파일을 다시 열어 그 줄이 남아 있는지 확인한다.'),
    box('caution','DVWA는 일부러 취약하게 만든 애플리케이션이다. 외부와 분리된 실습망에서만 접속한다. hosts는 Windows 전체의 이름 해석에 쓰이므로 추가한 줄만 바꾸고 다른 줄은 건드리지 않는다.'),
    h('로그인과 학습용 DB'),
    ol('브라우저 주소창에 http://dvwa.kt66.lab/login.php를 입력한다(도메인은 자신의 값). DVWA 로고와 Username·Password 칸이 나오면 이름 연결이 된 것이다.',
       'Username에 admin, Password에 password를 입력하고 **Login**을 누른다. DVWA 계정은 Wazuh 계정과 다르다.'),
    screen('login-filled','화면 5-1. DVWA 계정 입력.',100),
    p('로그인 뒤 **Database Setup** 화면이 열리면 학습용 DB가 아직 없는 것이다. 페이지 아래의 **Create / Reset Database**를 누르고 Setup successful!과 users·guestbook 테이블 생성 메시지를 확인한다. 약 5초 뒤 로그인 화면으로 돌아가면 다시 로그인한다.'),
    screen('setup-success','화면 5-2. 학습용 DB 생성 결과.',100),
    box('caution','Create / Reset Database는 기존 DB를 초기 상태로 바꾼다. 이미 DVWA를 쓰던 환경이면 누르지 않고 기존 계정으로 로그인한다.'),
    h('학습 단계 선택'),
    p('DVWA Security는 애플리케이션의 입력 처리 수준을 고르는 메뉴이다. Low는 입력 검사를 거의 하지 않는 코드를 실행한다. 이 설정은 DVWA 코드에만 적용되고, 앞단 WAF의 검사는 별도로 동작한다.'),
    ol('왼쪽 **DVWA Security**를 누르고 Security level is currently 옆의 현재 값을 사건 노트에 적는다.',
       '선택 상자에서 **Low**를 고르고 **Submit**을 누른다. 현재 값이 low로 바뀌었는지 확인한다.'),
    screen('security-select','화면 5-3. Low 선택과 적용.',100),
    screen('menu','화면 5-4. DVWA 실습 메뉴.',52),
    p('실습에는 왼쪽 메뉴의 **SQL Injection**(사용자 번호 조회), **XSS (Reflected)**(이름 출력), **File Inclusion**(파일 선택)을 쓴다.'))

# ── 5.3 ──────────────────────────────────────────────────────
section('5.3  요청과 응답 읽기',
    p('HTTP는 클라이언트의 요청에 서버가 응답하는 통신 규약이다. Submit을 누르면 브라우저가 다음과 같은 요청을 보낸다. GET은 지정한 자원을 요청하는 메서드이다.'),
    code('GET /vulnerabilities/sqli/?id=1&Submit=Submit HTTP/1.1\nHost: dvwa.kt66.lab'),
    p('URL의 물음표(?) 뒤는 이름=값 형식의 쿼리 매개변수이고 앰퍼샌드(&)가 여러 매개변수를 구분한다. 이 요청에서 id=1은 조회할 사용자 번호, Submit=Submit은 버튼 값이다.'),
    p('브라우저 개발자 도구의 **Network**는 브라우저가 보낸 요청과 받은 응답을 보여 준다(도식 5-3의 1 지점). Wazuh의 Dev Tools와는 다른 도구이다. [10]'),
    ol('DVWA 탭에서 **Ctrl+Shift+I**를 눌러 개발자 도구를 열고 **Network**를 고른다.',
       '**Preserve log**(로그 보존)를 켠다. 페이지가 바뀌어도 요청 목록이 남는다. 녹화 표시가 회색이면 눌러 빨간색으로 바꾼다.'),
    screen('network-list','화면 5-5. Network의 요청 목록.'),
    tab(['항목','읽는 내용'],[
        ['Type: document','페이지 문서 요청. CSS·이미지 요청과 구분해 이 행을 연다.'],
        ['Headers','Request URL·Request Method·Status Code'],
        ['Payload','전송한 쿼리 매개변수의 이름과 값'],
        ['Response','서버가 돌려준 본문']],[30,97]),
    p('브라우저는 특수문자를 URL에 넣을 수 있도록 %와 16진수 두 자리로 바꿔 보낸다(URL 인코딩). 이 장에서 읽을 표기는 다음과 같다.'),
    tab(['표기','원래 문자'],[
        ['%27','작은따옴표(\')'],['+ 또는 %20','공백'],['%2C · %2F','쉼표(,) · 슬래시(/)'],
        ['%3C · %3E','여는 꺾쇠(<) · 닫는 꺾쇠(>)'],['%28 · %29','여는 · 닫는 소괄호']],[30,97],keep=True),
    c('ipconfig',
      'Windows PC의 IP 주소를 확인한다. 공격 일지의 출발지 IP 칸에 적는다.',
      'ipconfig는 Windows의 네트워크 설정을 출력한다. 시작 메뉴에서 **명령 프롬프트**를 열고 입력한다.',
      'kt66과 같은 네트워크에 연결된 어댑터의 IPv4 주소를 적는다.','Windows · 명령 프롬프트'),
    p('Windows의 시각도 확인한다. 공격 일지의 시각과 Wazuh의 timestamp를 대조하려면 PC 시계가 맞아야 한다. **설정** → **시간 및 언어** → **날짜 및 시간**에서 시간 자동 설정이 켜져 있는지 확인한다.'))

# ── 5.4 ──────────────────────────────────────────────────────
section('5.4  정상 요청과 기준 기록',
    p('공격 요청을 읽기 전에 정상 요청이 어떤 기록을 남기는지 본다. 이 기록이 비교 기준이 된다.'),
    ol('**SQL Injection**을 누르고 User ID에 1을 입력한다.',
       'Network의 **Clear** 버튼으로 목록을 비우고 **Submit**을 누른다.'),
    screen('normal-result','화면 5-6. 사용자 1의 조회 결과.',100),
    p('ID: 1, First name: admin, Surname: admin이 나온다. Network에서 sqli/?id=1&Submit=Submit 행을 눌러 Headers의 GET·200 OK와 Payload의 id=1을 확인하고, 요청 시각을 적는다.'),
    screen('normal-headers','화면 5-7. 정상 요청의 URL·메서드·응답 코드.'),
    box('predict','이 정상 요청은 wazuh-alerts-*에 있을까, wazuh-archives-*에만 있을까? 4장에서 본 저장 기준으로 예측한다.'),
    q('agent.name: "web"\nAND data.url: "/vulnerabilities/sqli/?id=1&Submit=Submit"',
      '정상 조회 요청의 수집 기록을 찾는다.',
      'Discover에서 wazuh-archives-*를 고르고 기간을 요청 시각 앞뒤 5분으로 정한다. data.url은 디코더가 접속 로그에서 꺼낸 요청 경로와 쿼리이다.',
      '요청 시각의 행이 나온다. 정상 요청에 일치하는 경보 규칙이 없어 wazuh-alerts-*에서는 같은 검색이 0건이다.',index='wazuh-archives-*'),
    screen('normal-data','화면 5-8. 정상 요청의 수집 기록.'),
    tab(['필드','이 기록의 값과 뜻'],[
        ['data.url','/vulnerabilities/sqli/?id=1&Submit=Submit · 요청 경로와 입력값'],
        ['data.id','200 · HTTP 응답 코드. 규칙 번호 rule.id와 다르다.'],
        ['data.protocol','GET · 이 웹 로그에서는 HTTP 메서드'],
        ['data.srcip','웹 서버가 기록한 요청 출발지'],
        ['location','/var/log/apache2/dvwa_access.log']],[30,97]),
    p('data.srcip를 ipconfig로 적은 PC 주소와 비교한다. 두 값이 다르면 요청이 웹 서버에 도착하기 전에 네트워크 장비에서 출발지 주소가 바뀐 것이다. 화면의 10.20.30.254는 검증 환경의 브라우저 경로에서 기록된 값이다. 이후 검색에는 자신의 기록에서 읽은 data.srcip를 쓴다.'),
    h('Apache 원본 로그'),
    p('Discover의 기록이 원본과 같은지 kt66-web에서 직접 확인한다(도식 5-3의 2 지점).'),
    c('docker exec -it kt66-web /bin/bash',
      '웹 서버 컨테이너 kt66-web의 셸로 들어간다.',
      '-i는 키보드 입력을 연결하고 -t는 터미널을 할당한다. /bin/bash는 실행할 셸이다.',
      '프롬프트가 kt66-web 안으로 바뀐다.',HOST),
    c("grep -F '/vulnerabilities/sqli/?id=1&Submit=Submit' \\\n  /var/log/apache2/dvwa_access.log",
      '정상 요청의 접속 로그 원문을 찾는다.',
      'grep -F는 작은따옴표 안의 URL을 정규표현식이 아니라 글자 그대로 찾는다. 물음표·앰퍼샌드도 일반 문자로 다룬다. 줄 끝의 역슬래시(\\)는 명령을 다음 줄로 잇는다.',
      '요청 시각의 줄에서 출발지 IP, GET 요청, 200 응답을 읽는다.',WEB),
    c('exit',
      'kt66-web 셸에서 나온다.',
      'exit는 현재 셸을 끝낸다. 컨테이너는 계속 실행된다.',
      'kt66 VM의 프롬프트로 돌아온다.',WEB),
    code('10.20.30.254 - - [01/Nov/2026:21:12:21 +0900]\n"GET /vulnerabilities/sqli/?id=1&Submit=Submit\nHTTP/1.1" 200 1792'),
    tab(['원문의 부분','뜻 · Wazuh 필드'],[
        ['첫 IP','요청 출발지 · data.srcip'],
        ['- -','원격 사용자 식별값과 인증 사용자명. 기록되지 않았다.'],
        ['[날짜:시각 시간대]','Apache가 기록한 시각'],
        ['"GET … HTTP/1.1"','요청 줄 · 메서드는 data.protocol, 경로는 data.url'],
        ['200','응답 코드 · data.id'],
        ['1792','응답으로 보낸 바이트 수'],
        ['뒤의 따옴표 두 개','Referer(이전 페이지 주소)와 User-Agent(브라우저 정보)']],[38,89],keep=True),
    p('원문 전체는 full_log에 저장된다. 원문의 나머지는 examples/rev01/chapter05/browser/normal.log에 있다. [4]'))

# ── 5.5 ──────────────────────────────────────────────────────
section('5.5  SQL 인젝션',
    p('SQL은 데이터베이스에서 자료를 조회·변경하는 언어이다. DVWA의 사용자 조회는 입력한 id를 다음 SQL 문장의 따옴표 안에 그대로 붙여 실행한다. 이 코드는 kt66-dvwa 컨테이너의 /var/www/html/vulnerabilities/sqli/source/low.php에 있다. [1]'),
    code("SELECT first_name, last_name\nFROM users\nWHERE user_id = '1';"),
    p('SQL 인젝션은 입력값이 SQL 문법의 일부로 해석되어 원래 조회의 의미가 바뀌는 취약점이다. 입력을 SQL 문자열에 그대로 결합하면 생긴다. Discover의 DQL은 저장된 기록을 검색하는 식이고, 여기의 SQL은 애플리케이션이 데이터베이스에 보내는 문장이다. [5]'),
    img(FIG+'sql-context.png','도식 5-5. 입력값을 SQL 문자열에 결합하는 처리.'),
    p('User ID에 다음 값을 넣는다. 공격 동작을 유도하려고 보내는 이런 입력을 페이로드(payload)라고 한다. 복사용 파일은 examples/rev01/chapter05/B05-03-sqli.txt이다. -- 뒤에 공백이 한 칸 있다.'),
    code(PAYLOAD),
    tab(['부분','의도'],[
        ["1'","작은따옴표로 원래 문자열 값을 닫는다."],
        ['UNION SELECT user,password','원래 조회 결과에 계정명과 저장된 암호값 두 열을 덧붙인다.'],
        ['FROM users','그 값을 users 테이블에서 읽는다.'],
        ['-- 와 공백','MySQL에서 뒤에 남은 원래 SQL을 주석으로 만든다.']],[42,85],keep=True),
    box('field','공격 일지 기록을 여기서 시작한다. 공격을 보낼 때마다 시각(KST) | 실행 위치 | 출발지 IP | 대상 | 입력 | 응답을 한 줄로 적는다. 입력에는 복사용 파일 이름(B05-03 등)을 쓰면 된다.'),
    box('predict','DVWA는 Low 단계라 입력을 검사하지 않는다. 그 앞의 WAF는 어떻게 할까? 응답 코드를 예측한다.'),
    ol('User ID에 위 값을 붙여 넣는다.',
       'Network를 비우고 **Submit**을 누른다. 공격 일지에 시각을 적는다.'),
    screen('sqli-input','화면 5-9. User ID에 SQL 구문 입력.',100),
    screen('sqli-blocked','화면 5-10. SQL 요청의 거부 응답.',100),
    p('Forbidden 화면이 나온다. Network의 문서 요청에서 Status Code 403과 Payload의 id 값을 확인한다. 403은 서버가 요청 수행을 거부했다는 응답 코드이다. 누가 거부했는지는 5.6에서 확인한다.'),
    screen('sqli-headers','화면 5-11. SQL 요청의 URL과 응답 코드.'),
    q('agent.name: "web" AND data.url: *vulnerabilities/sqli/*\nAND data.url: *UNION*',
      'SQL 실습 경로에 UNION을 보낸 요청의 경보를 찾는다.',
      '별표(*)는 임의의 문자열과 일치한다. 두 data.url 조건을 AND로 묶어 경로와 문자열을 모두 포함한 URL을 고른다.',
      '요청 시각의 행이 나온다. rule.id·data.id·data.url을 조사 기록에 적는다.'),
    screen('sqli-data','화면 5-12. SQL 입력과 응답 코드.'),
    screen('sqli-rule','화면 5-13. SQL 인젝션 탐지 설명.'),
    tab(['필드','이 사례의 값과 해석'],[
        ['data.url','%27은 작은따옴표, +는 공백, %2C는 쉼표이다. UNION SELECT 구문이 들어 있다.'],
        ['data.id','403 · 웹 서버가 거부 응답을 보냈다.'],
        ['rule.id · 설명','31103 · SQL injection attempt.']],[30,97]),
    p('규칙 31103은 접속 로그의 URL에 union+, select+, %20from%20 같은 문자열이 있으면 일치한다. 판정 근거는 URL 문자열이므로, 도식 5-3에서 이 경보가 보여 주는 것은 2 지점(웹 서버 도착)까지이다. 화면의 &amp;는 매개변수 구분 기호 &를 HTML로 표기한 것이다. [6]'))

# ── 5.6 ──────────────────────────────────────────────────────
section('5.6  WAF 차단 근거 찾기',
    p('403은 웹 서버, 접근 제어, WAF 중 어디에서든 나올 수 있다. 같은 요청의 ModSecurity 감사 기록에서 WAF가 차단했는지 확인한다(도식 5-3의 3 지점).'),
    q('agent.name: "web"\nAND location: "/var/log/apache2/modsec_audit.log"\nAND data.request.request_line: *UNION*',
      'SQL 요청에 대한 WAF 감사 기록을 찾는다.',
      '감사 기록은 경보 규칙과 관계없이 아카이브에 있으므로 인덱스 패턴을 wazuh-archives-*로 바꾼다. location으로 감사 로그를, request_line으로 SQL 요청을 고른다.',
      '한 행을 펼쳐 request_line의 SQL 입력, 시각, 출발지를 5.5의 접속 로그와 대조한다.',index='wazuh-archives-*'),
    screen('waf-action','화면 5-14. ModSecurity의 차단 결정.'),
    tab(['필드','뜻'],[
        ['action.intercepted: true','WAF가 요청 처리를 가로막았다.'],
        ['action.phase: 2','요청 본문 검사 단계. URL 매개변수도 이 단계의 규칙이 검사한다.'],
        ['action.message','차단 판단의 비교 조건. 누적 점수(anomaly_score)가 기준 이상인지 검사했다.']],[42,85]),
    p('화면의 필드 이름은 모두 data.audit_data.action으로 시작한다.'),
    screen('waf-response','화면 5-15. 감사 기록의 응답과 접속 정보.'),
    tab(['필드','확인할 내용'],[
        ['response.status','403'],
        ['transaction.remote_address','요청 출발지. 접속 로그의 data.srcip와 같은지 본다.'],
        ['transaction.local_address · local_port','요청을 받은 kt66-web의 주소 10.20.32.80과 포트 80'],
        ['transaction.time','WAF가 처리한 시각'],
        ['transaction.transaction_id','WAF가 요청마다 붙인 식별자']],[48,79],keep=True),
    p('JSON 탭의 data.audit_data.messages에는 일치한 CRS 규칙과 차단 이유가 있다. 다음 두 번호를 찾는다.'),
    code('942100 · SQL Injection Attack Detected\n949110 · Access denied with code 403'),
    p('CRS는 공격 패턴 규칙마다 점수를 더하고, 합계가 기준(기본 5) 이상이면 차단 규칙 949110이 요청을 거부한다. 942100이 SQL 인젝션 점수를 더했고, 949110이 403으로 차단했다. [2]'),
    box('field','942100은 WAF(CRS)의 규칙 번호이고 31103은 Wazuh의 규칙 번호이다. 두 번호는 서로 다른 장비가 같은 요청을 각자 판단한 결과이다. 보고서에는 어느 장비의 번호인지 함께 적는다.'),
    p('시각·출발지·요청 URL이 접속 로그와 같으면 조사 기록에 “SQL 인젝션 입력이 웹 서버에 도착했고 WAF가 403으로 차단했다”라고 적는다. DVWA와 데이터베이스는 이 요청을 받지 않았다.'))

# ── 5.7 ──────────────────────────────────────────────────────
section('5.7  XSS',
    p('DVWA의 XSS (Reflected) 실습은 이름 칸에 받은 값을 응답 HTML에 그대로 넣는다. XSS(Cross-Site Scripting)는 입력한 스크립트가 웹 페이지의 코드로 해석되어 사용자의 브라우저에서 실행되는 취약점이다. 반사형(Reflected)은 요청의 입력값이 곧바로 그 응답에 들어가는 방식이다. [7]'),
    code('<script>alert(1)</script>'),
    p('<script>와 </script>는 HTML에서 스크립트의 시작과 끝이고, alert(1)은 JavaScript로 숫자 1을 띄우는 알림 창을 연다. SQL 인젝션은 데이터베이스의 SQL 해석을, XSS는 브라우저의 HTML·스크립트 해석을 노린다.'),
    img(FIG+'xss-context.png','도식 5-6. 반사형 XSS의 실행 과정.'),
    ol('거부 화면에서는 브라우저의 뒤로 가기로 DVWA에 돌아온다. **XSS (Reflected)**를 누른다.',
       'What’s your name?에 위 값을 넣는다(B05-04-xss.txt). Network를 비우고 **Submit**을 누른 뒤 공격 일지에 적는다.'),
    screen('xss-blocked','화면 5-16. XSS 요청의 거부 응답.',100),
    p('403 응답이 나오고 알림 창은 열리지 않는다. Network의 Payload에서 name 값을 확인한다.'),
    q('agent.name: "web" AND data.url: *vulnerabilities/xss_r/*\nAND rule.id: "31105"',
      'XSS 실습 경로의 XSS 경보를 찾는다.',
      '5.5와 같은 형식이다. 31105는 Wazuh의 XSS 시도 규칙이다.',
      '요청 시각의 행에서 data.url의 %3Cscript%3E(<script>)와 data.id 403을 읽는다.'),
    screen('xss-data','화면 5-17. 스크립트 입력의 수집 기록.'),
    p('31105(XSS (Cross Site Scripting) attempt.)는 URL에 %3Cscript, script> 같은 문자열이 있으면 일치한다. 5.6의 Q05-03에서 마지막 조건을 data.request.request_line: *xss_r*로 바꾸면 같은 요청의 intercepted: true와 403을 확인할 수 있다. [6]'),
    tab(['관찰','도달 지점 판정'],[
        ['URL에 스크립트가 있다','1·2 · 입력을 보냈고 웹 서버에 도착했다.'],
        ['403과 intercepted: true','3 · WAF가 차단했다.'],
        ['응답이 200이다','4 · 응답 HTML에 입력이 어떻게 들어갔는지 Response에서 확인한다.'],
        ['브라우저에서 알림 창이 열린다','5 · 그 페이지에서 스크립트가 실행되었다.']],[45,82],keep=True),
    p('애플리케이션에서는 입력을 출력할 위치에 맞게 바꿔야 한다. 예를 들어 HTML 본문에 출력할 때 <를 &lt;로 바꾸면 브라우저는 태그가 아니라 문자로 표시한다. HTML 속성·JavaScript·URL 안에서는 각각 다른 처리가 필요하다. [8]'))

# ── 5.8 ──────────────────────────────────────────────────────
section('5.8  경로 조작',
    p('DVWA의 File Inclusion 실습은 page 값으로 서버가 읽어 포함할 파일을 고른다. LFI(Local File Inclusion)는 입력값에 따라 서버 내부 파일을 포함하는 취약점이고, 디렉터리 트래버설은 ../ 같은 경로 표현으로 허용된 디렉터리 밖의 파일에 접근하려는 공격이다. [9]'),
    code('../../../../../etc/passwd'),
    p('../는 상위 디렉터리로 이동한다. 다섯 번이면 DVWA의 실습 디렉터리에서 루트(/)까지 올라간다. /etc/passwd는 Linux의 계정 이름·UID·홈 디렉터리·로그인 셸이 적힌 파일이다.'),
    img(FIG+'path-context.png','도식 5-7. 입력 경로를 그대로 사용한 파일 접근.'),
    ol('**File Inclusion**을 누르고 **file1.php** 링크를 누른다. 주소창의 ?page=file1.php와 본문의 파일 내용을 확인한다.',
       '주소창에서 물음표 뒤를 page=../../../../../etc/passwd&bookcase=book05-browser-path-raw로 바꾸고 Enter를 누른다. 앞부분 주소는 그대로 둔다. 전체 주소는 B05-06-path-raw-url.txt에 있다. bookcase는 로그에서 이 요청을 찾기 위해 붙인 표식이다.'),
    screen('file-normal','화면 5-18. file1.php를 선택한 결과.',100),
    screen('path-blocked','화면 5-19. 파일 경로 요청의 거부 응답.',100),
    box('predict','다음에는 슬래시(/)를 %2F로 인코딩해 같은 경로를 보낸다. 서버가 해석하는 경로는 같다. Wazuh의 규칙 번호도 같을까?'),
    ol('같은 주소에서 물음표 뒤를 page=..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd&bookcase=book05-browser-path로 바꾸고 Enter를 누른다(B05-08-path-encoded-url.txt). 두 요청을 공격 일지에 적는다.'),
    q('agent.name: "web"\nAND data.url: *book05-browser-path*',
      '두 경로 요청의 경보를 함께 찾는다.',
      '두 요청의 표식에 모두 book05-browser-path가 들어 있으므로 한 번에 나온다.',
      '두 행의 data.url·data.id·rule.id를 비교한다.'),
    screen('path-data','화면 5-20. 경로 조작 요청의 수집 기록.'),
    tab(['보낸 형태','응답','Wazuh 규칙'],[
        ['슬래시 그대로(../)','403','31104 · Common web attack.'],
        ['슬래시를 %2F로','403','31101 · Web server 400 error code.']],[42,18,67],keep=True),
    p('규칙 31104의 조건에는 ../..와 %2E%2E 같은 문자열이 있지만 ..%2F는 없다. 그래서 인코딩한 요청은 31104에 일치하지 않았다. 대신 응답 코드가 4로 시작하면 일치하는 31101(400번대 응답)이 붙었다. [6]'),
    box('blind','31101은 공격 문자열이 아니라 403 응답 때문에 붙었다. 규칙 조건으로 보면, 같은 인코딩 요청이 200으로 처리되었다면 일치하는 공격 규칙이 없어 경보가 생기지 않는다. 그 요청은 wazuh-archives-*에만 남는다. 경보만으로 경로 조작 시도를 찾으면 이런 요청을 놓친다.'),
    p('두 요청은 WAF에서 차단되었고 파일 내용이 돌아온 기록은 없다. 파일이 노출되었는지는 4·5 지점, 즉 응답 본문에 /etc/passwd의 내용이 있는지로 판정한다.'),
    p('애플리케이션에서는 page에 파일 경로를 직접 받지 않고, home·help 같은 허용된 이름을 받아 서버가 고정된 파일에 대응시키는 방식으로 바꾼다. 경로를 받아야 한다면 정규화한 최종 경로가 허용 디렉터리 안에 있는지 검사한다.'))

# ── 5.9 ──────────────────────────────────────────────────────
section('5.9  도달 지점 판정',
    img(FIG+'evidence.png','도식 5-8. 응답·차단 결정·로그 분류의 대조.'),
    tab(['요청','응답','WAF','Wazuh','도달 지점'],[
        ['User ID 1','200','-','경보 없음','5 · 사용자 1 표시'],
        ['SQL 인젝션','403','차단','31103','3에서 차단'],
        ['XSS','403','차단','31105','3에서 차단'],
        ['경로(../)','403','차단','31104','3에서 차단'],
        ['경로(%2F)','403','차단','31101','3에서 차단']],[27,15,15,20,50],keep=True),
    p('검증 환경의 결과이다. 자신의 결과로 같은 표를 만들고, 공격 일지의 각 줄 옆에 도달 지점을 적는다.'),
    p('Wazuh에는 공격 규칙(31103·31104·31105)에 일치한 요청이 200 응답을 받으면 붙는 31106(A web attack returned code 200 (success).)도 있다. 이 규칙의 조건은 공격 문자열과 응답 코드 200이다. 도식 5-3으로 보면 4 지점의 일부만 확인한 것이므로, 31106을 보면 응답 본문과 서버 동작에서 5 지점의 근거를 찾는다. [6]'),
    h('조건을 넓혀 찾기'),
    p('bookcase는 실습에서 붙인 표식이다. 실제 조사에서는 요청 경로·출발지·공격 문자열·탐지 규칙을 조합한다.'),
    q('agent.name: "web" AND\n(rule.id: "31104" OR data.url: *etc*passwd*)',
      '경로 조작 규칙에 일치한 요청과 파일명 문자열이 들어간 요청을 함께 찾는다.',
      '괄호 안의 OR로 두 조건 중 하나를 만족하는 기록을 고른다. *etc*passwd*는 etc와 passwd 사이가 / 이든 %2F이든 일치한다.',
      '31104 요청과 31101 요청이 함께 나온다. 실습 밖의 기록도 나올 수 있다.'),
    q('agent.name: "web" AND data.srcip: "10.20.30.254"\nAND (rule.id: "31104" OR data.url: *etc*passwd*)',
      '같은 출발지의 경로 조작 요청만 남긴다.',
      '10.20.30.254를 5.4에서 읽은 자신의 data.srcip로 바꾼다. 기간은 실습 시작부터 끝까지로 정한다.',
      '같은 출발지의 요청을 시각 순서로 읽는다.'),
    p('입력값 검증은 예상한 형식·범위·허용값만 받아들이는 처리이다. SQL에는 문장을 고정하고 값을 따로 전달하는 매개변수 바인딩을, XSS에는 출력 위치에 맞는 처리를, 파일 기능에는 접근 범위 제한을 적용한다. WAF는 그 앞에서 알려진 공격 형태를 줄여 주는 장치이다.'))

# ── 5.10 ─────────────────────────────────────────────────────
section('5.10  결과가 다를 때',
    tab(['증상','확인 순서'],[
        ['사이트 이름을 찾을 수 없다','주소창의 이름 → Windows hosts의 이름·IP'],
        ['연결 거부 또는 시간 초과','kt66 기동 → Windows와 kt66의 네트워크 → WEB_HOST_IP와 80번 포트'],
        ['다른 사이트가 열린다','LAB_DOMAIN → 주소창 → hosts의 이름'],
        ['공격 요청이 200 또는 302','응답 본문 → 로그인 상태 → 입력값 → WAF 적용 모드(아래)'],
        ['Apache 원문이 없다','이름·접속 경로 → dvwa_access.log → 요청 시각·URL'],
        ['원문은 있으나 Discover에 없다','인덱스·기간 → DQL → web 에이전트 연결 → localfile 설정(아래)'],
        ['예상한 규칙이 없다','URL 인코딩 → data.id → 다른 rule.id → WAF 감사 기록']],[42,85],keep=True),
    p('조건을 고친 뒤에는 요청을 새로 보내 새 시각으로 찾는다. 이미 저장된 기록은 바뀐 조건으로 다시 분석되지 않는다(4.9).'),
    h('WAF와 수집 설정 확인'),
    c('docker exec -it kt66-web /bin/bash',
      'kt66-web 컨테이너의 셸로 들어간다.',
      'C05-03과 같다.',
      '프롬프트가 kt66-web 안으로 바뀐다.',HOST),
    c("grep -n -E '^SecRuleEngine|^SecAuditEngine' \\\n  /etc/modsecurity/modsecurity.conf\ngrep -n -E 'ServerName|SecRuleEngine' \\\n  /etc/apache2/sites-enabled/020-dvwa.conf",
      'WAF의 동작 모드와 DVWA 사이트 설정을 읽는다.',
      '-n은 줄 번호를 붙이고 -E는 확장 정규표현식을 쓴다. 이 정규표현식에서 ^는 줄의 시작, 파이프(|)는 또는(OR)을 뜻한다.',
      '첫 명령은 SecRuleEngine On과 SecAuditEngine RelevantOnly를 출력한다. 둘째 명령은 ServerName에 자신의 dvwa 도메인을 보여 주고 SecRuleEngine 줄은 없다. DVWA 사이트가 전역 설정 On을 그대로 쓴다는 뜻이다.',WEB),
    tab(['값','뜻'],[
        ['SecRuleEngine On','규칙을 검사하고 차단까지 적용한다.'],
        ['SecRuleEngine DetectionOnly','검사·기록만 하고 차단하지 않는다.'],
        ['SecAuditEngine RelevantOnly','차단 등 관련 조건을 만족한 요청만 감사 기록에 남긴다.']],[50,77]),
    c("grep -F -B 1 -A 1 '*_access.log' \\\n  /var/ossec/etc/ossec.conf\ngrep -F -B 1 -A 1 'modsec_audit.log' \\\n  /var/ossec/etc/ossec.conf",
      'web 에이전트가 접속 로그와 감사 로그를 수집하는 설정을 읽는다.',
      '4.2와 같은 형식이다. 작은따옴표 안의 *는 grep -F에서 글자 그대로의 별표로 찾는다.',
      '첫 명령은 log_format apache와 /var/log/apache2/*_access.log를, 둘째 명령은 log_format json과 /var/log/apache2/modsec_audit.log를 보여 준다. 설정의 *는 여러 사이트의 access 로그를 모두 수집한다는 뜻이다.',WEB),
    c('exit',
      'kt66-web 셸에서 나온다.',
      'C05-05와 같다.',
      'kt66 VM의 프롬프트로 돌아온다.',WEB),
    c('docker exec -it kt66-siem /bin/bash',
      'Manager 컨테이너 kt66-siem의 셸로 들어간다.',
      'C05-03과 같은 형식이다.',
      '프롬프트가 kt66-siem 안으로 바뀐다.',HOST),
    c("grep -n -A 9 '<rule id=\"31104\"' \\\n  /var/ossec/ruleset/rules/0245-web_rules.xml",
      '경로 조작 규칙 31104의 설치된 정의를 읽는다.',
      '-A 9는 일치한 줄 뒤의 아홉 줄을 함께 출력한다.',
      'if_sid 31100과 url 조건의 ../.., %2E%2E, 설명 Common web attack.을 확인한다. ..%2F가 조건에 없는 것을 5.8의 결과와 대조한다.',SIEM),
    c('exit',
      'kt66-siem 셸에서 나온다.',
      'C05-05와 같다.',
      'kt66 VM의 프롬프트로 돌아온다.',SIEM))

# ── 5.11 ─────────────────────────────────────────────────────
section('5.11  원상복구와 기록',
    ol('**DVWA Security**를 열어 5.2에서 적은 원래 단계로 바꾸고 **Submit**을 누른다. 현재 값이 원래대로인지 확인한다.',
       '**Logout**을 누른다. 로그인 화면이 나오면 DVWA 세션이 끝난 것이다.',
       'Windows hosts에 줄을 추가했다면, 6장에서도 DVWA 이름을 쓰므로 그대로 둔다. 지울 때는 관리자 권한 메모장으로 추가한 줄만 지우거나 사건 노트에 적은 원래 값으로 되돌리고, 저장 후 다시 열어 확인한다.',
       'Network의 로그 보존을 끄고 개발자 도구를 닫는다. Discover의 검색식과 필터를 비우고 wazuh-alerts-*, Last 24 hours로 되돌린다.'),
    p('학습용 DB는 다음 실습에서도 쓴다. Create / Reset Database는 원상복구 버튼이 아니며 누르면 자료가 초기화된다. 접속 로그와 경보는 조사 자료로 남긴다.'),
    h('공격 일지와 조사 기록'),
    p('공격 일지에는 보낸 요청 다섯 건(정상 1, 공격 4)이 있어야 한다. 예를 들면 다음과 같다.'),
    code('21:14 | Windows 브라우저 | <PC IP> | dvwa sqli |\nB05-03 | 403 Forbidden'),
    p('조사 기록에는 Wazuh와 WAF에서 확인한 사실을 적는다. 항목은 examples/rev01/chapter05/investigation.txt를 따른다. 공격 일지의 출발지와 조사 기록의 data.srcip가 다르면 그 차이도 적는다. 11장에서 두 기록을 대조할 때 출발지가 다른 이유를 설명해야 한다.'),
    {'type':'image','path':'assets/illustrations/chapter05/review.png','caption':'삽화. 요청 결과 검토.','width_mm':45,'align':'right'})

# ── 5.12 ─────────────────────────────────────────────────────
section('5.12  선택 실습: 같은 요청을 curl로 보내기',
    p('curl은 URL로 HTTP 요청을 보내고 응답을 터미널에 출력하는 도구이다. 같은 입력을 명령으로 보내 보면 브라우저가 대신 해 주던 인코딩과 로그인 상태 유지를 직접 지정해야 한다는 것을 알 수 있다. 실행 위치는 1.9에서 준비한 공격자 VM이다.'),
    c('curl --version\nip -br -4 address',
      'curl 설치와 공격자 VM의 IP를 확인한다.',
      '--version은 curl의 버전을 출력한다. ip -br -4 address는 IPv4 주소를 인터페이스마다 한 줄로 간략하게 출력한다.',
      'curl 버전(검증 환경 7.81.0)과 ens33 등 인터페이스의 주소가 나온다. 이 주소를 공격 일지의 출발지 IP로 적는다. lo의 127.0.0.1은 자기 자신이다.',ATT),
    h('이름과 시각 준비'),
    p('공격자 VM의 /etc/hosts는 Windows의 hosts와 별개이다. 1.9에서 등록하지 않았다면 여기서 등록한다.'),
    c("grep -n -F 'dvwa.' /etc/hosts",
      '(사전 확인) DVWA 이름이 이미 등록되어 있는지 확인한다.',
      '-n은 줄 번호를 붙이고 -F는 점(.)을 글자 그대로 찾는다.',
      '이름과 IP가 맞는 줄이 있으면 C05-16으로 건너뛴다. 고칠 줄이 있으면 사건 노트에 원래 값을 적는다.',ATT),
    c('sudo nano /etc/hosts',
      'DVWA 이름과 kt66 IP를 등록한다.',
      'sudo는 관리자 권한으로 실행한다. 기존 줄이 있으면 고치고, 없으면 맨 끝에 192.168.0.189 dvwa.kt66.lab 형식으로 한 줄을 추가한다.',
      '**Ctrl+O**, **Enter**로 저장하고 **Ctrl+X**로 닫는다.',ATT),
    c("getent hosts dvwa.kt66.lab\nDVWA='http://dvwa.kt66.lab'\necho \"$DVWA\"",
      '이름이 kt66 IP로 해석되는지 확인하고, 주소를 셸 변수에 저장한다.',
      'getent hosts는 시스템이 이름을 해석한 결과를 출력한다. DVWA=…는 현재 셸에 변수를 만든다. 등호 양쪽에 공백을 두지 않는다. $DVWA는 변수 값으로 바뀌고 큰따옴표는 그 값을 하나의 인자로 묶는다. 도메인은 자신의 값으로 바꾼다.',
      'getent가 kt66의 WEB_HOST_IP를, echo가 DVWA 주소를 출력한다. 이후 명령은 같은 터미널에서 실행한다.',ATT),
    c('date -Is\ntimedatectl status',
      '공격자 VM의 시각과 시간 동기화 상태를 확인한다.',
      '2.4와 같은 명령이다. NTP는 시간 서버를 기준으로 시계를 맞추는 방식이다.',
      'System clock synchronized: yes와 NTP service: active를 확인한다. no이면 다음 명령을 실행한다.',ATT),
    c('sudo timedatectl set-ntp true',
      '(동기화가 꺼져 있을 때만) NTP 시간 동기화를 켠다.',
      'set-ntp true는 NTP 동기화를 켠다. 관리자 권한이 필요하다.',
      'timedatectl status를 다시 실행해 yes를 확인한다. 계속 no이면 인터넷 연결을 확인한다.',ATT),
    h('요청 보내기'),
    tab(['옵션·구문','동작'],[
        ['-sS','진행 표시를 숨기고(-s) 오류 메시지는 표시한다(-S).'],
        ['-i','응답 헤더와 본문을 함께 출력한다.'],
        ['--max-time 15','전체 요청 시간을 15초로 제한한다.'],
        ['--get','뒤의 입력값을 URL 쿼리에 붙여 GET으로 보낸다.'],
        ['--data-urlencode 이름=값','값을 URL 인코딩해 보낸다. 반복하면 매개변수가 여러 개가 된다.'],
        ['--data 이름=값','값을 인코딩하지 않고 그대로 보낸다.'],
        ['줄 끝의 \\','다음 줄까지 한 명령으로 잇는다.']],[45,82],keep=True),
    c('curl -sS -i --max-time 15 "$DVWA/login.php"',
      '로그인 페이지를 요청해 응답의 구조를 본다.',
      '"$DVWA/login.php"는 변수의 주소 뒤에 경로를 붙인 하나의 인자이다.',
      '첫 줄에 HTTP/1.1 200 OK, 이어서 헤더, 빈 줄, HTML 본문이 나온다. curl은 HTML을 화면으로 그리거나 스크립트를 실행하지 않고 문자 그대로 출력한다.',ATT),
    c(CURL+'  "$DVWA/vulnerabilities/sqli/" \\\n  --data-urlencode \'id=1\' \\\n  --data-urlencode \'Submit=Submit\' \\\n  --data-urlencode \'bookcase=book05-normal\'',
      '브라우저의 정상 조회와 같은 매개변수를 보낸다.',
      'id와 Submit은 브라우저 폼이 보낸 값이고, bookcase는 로그에서 이 요청을 찾기 위한 표식이다.',
      '302 Found와 Location: login.php가 나온다. curl은 브라우저의 로그인 쿠키를 갖고 있지 않아 DVWA가 로그인 화면으로 보낸 것이다. -L 옵션이 없으므로 curl은 이동하지 않는다.',ATT),
    c('PAYLOAD="'+PAYLOAD+'"\n'+CURL+'  "$DVWA/vulnerabilities/sqli/" \\\n  --data-urlencode "id=$PAYLOAD" \\\n  --data-urlencode \'Submit=Submit\' \\\n  --data-urlencode \'bookcase=book05-sqli\'',
      'SQL 인젝션 입력을 보낸다.',
      '첫 줄은 SQL 입력을 셸 변수 PAYLOAD에 저장한다. 큰따옴표 안의 작은따옴표는 입력의 일부이며 -- 뒤 공백도 포함된다. --data-urlencode가 공백과 작은따옴표를 인코딩한다.',
      '403 Forbidden이 나온다. 이전 검증에서 Wazuh는 31103으로 분류했다. Discover에서 data.url: *book05-sqli*로 찾는다.',ATT),
    c(CURL+'  "$DVWA/vulnerabilities/xss_r/" \\\n  --data-urlencode \'name=<script>alert(1)</script>\' \\\n  --data-urlencode \'bookcase=book05-xss\'',
      'XSS 입력을 보낸다.',
      '작은따옴표는 꺾쇠와 소괄호를 셸이 해석하지 않도록 묶는다.',
      '403이 나온다. 이전 검증에서 Wazuh는 31105로 분류했다. curl 출력으로는 스크립트 실행 여부를 확인할 수 없다. 응답과 WAF 차단을 확인한다.',ATT),
    c(CURL+'  "$DVWA/vulnerabilities/fi/" \\\n  --data-urlencode \'page=../../../../../etc/passwd\' \\\n  --data \'bookcase=book05-path\'\n'+CURL+'  "$DVWA/vulnerabilities/fi/" \\\n  --data \'page=../../../../../etc/passwd\' \\\n  --data \'bookcase=book05-path-raw\'',
      '같은 경로를 인코딩한 형태와 그대로의 형태로 한 번씩 보낸다.',
      '첫 요청은 --data-urlencode로 슬래시를 %2F로 바꾸고, 둘째 요청은 --data로 슬래시를 그대로 보낸다. 특수문자가 없는 bookcase는 --data로 보낸다.',
      '두 요청 모두 403이 나온다. 이전 검증에서 Wazuh는 첫 요청을 31101, 둘째 요청을 31104로 분류했다. 5.8의 브라우저 결과와 같다.',ATT),
    p('보낸 요청을 공격 일지에 적는다. 실행 위치는 공격자 VM, 출발지는 C05-13에서 확인한 주소이다. Discover의 data.srcip와 비교한다.'),
    h('curl 실습 원상복구'),
    p('C05-15에서 hosts를 바꿨다면, 6장 이후에도 쓰는 이름이므로 그대로 둔다. 지울 때는 C05-14로 줄을 확인하고 C05-15로 추가한 줄만 지운 뒤 C05-14로 다시 확인한다. NTP 동기화는 켜 둔다.'),
    c('unset DVWA PAYLOAD\necho "$DVWA"',
      '셸 변수를 지우고 지워졌는지 확인한다.',
      'unset은 현재 셸의 변수를 지운다.',
      'echo가 빈 줄을 출력한다.',ATT))

# ── 장 끝 ─────────────────────────────────────────────────────
page('5장 정리',
    h('핵심 정리'),
    ul('입력의 도달 범위는 브라우저 송신 → 웹 서버 도착 → WAF 판정 → 애플리케이션 처리 → 결과의 다섯 지점으로 나누고, 지점마다 Network·접속 로그·감사 기록·응답 본문으로 확인한다.',
       'Wazuh의 웹 공격 규칙(31103·31104·31105)은 접속 로그의 URL 문자열로 판단한다. 이 경보는 공격 입력이 웹 서버에 도착했다는 근거이다.',
       'WAF의 차단은 감사 기록의 intercepted와 CRS 규칙(942100·949110)으로 확인한다. WAF 규칙 번호와 Wazuh 규칙 번호는 다른 장비의 판단이다.',
       'URL 인코딩이 달라지면 같은 공격도 다른 규칙에 일치하거나 경보가 생기지 않을 수 있다. 아카이브의 원문으로 보완한다.'),
    h('확인 문제'),
    ol('31103 경보의 data.id가 403이다. 데이터베이스가 그 SQL을 실행했는가? 근거는?',
       '403 응답을 WAF가 보냈는지 확인하려면 어느 기록의 어떤 필드를 보는가?',
       '경로 조작 요청에 31101만 붙었다. 왜 31104가 아닌가?',
       '31106 경보가 생겼다. 공격이 성공했다고 적기 전에 무엇을 확인하는가?',
       '공격 일지의 출발지는 PC 주소인데 data.srcip는 다른 주소이다. 무엇을 뜻하는가?'),
    h('확인 문제 해설'),
    ol('실행하지 않았다. 같은 요청의 감사 기록에 intercepted: true가 있으면 WAF가 차단했으므로 DVWA와 데이터베이스까지 가지 않았다(5.6).',
       'wazuh-archives-*의 modsec_audit.log 기록에서 data.audit_data.action.intercepted와 response.status, messages의 949110을 본다.',
       '슬래시를 %2F로 인코딩해 31104의 조건 문자열(../.., %2E%2E)과 일치하지 않았다. 403 응답 때문에 400번대 응답 규칙 31101이 붙었다.',
       '응답 본문과 서버 동작에서 결과(DB 자료 반환, 스크립트 실행, 파일 내용)를 확인한다. 31106의 조건은 공격 문자열과 응답 코드 200이다.',
       '요청이 웹 서버에 도착하기 전에 네트워크 장비에서 출발지 주소가 바뀌었다. 조사 기록에 그 차이를 적는다.'),
    h('더 읽을거리'),
    p('OWASP의 SQL 인젝션 방어 문서이다. 5.9의 매개변수 바인딩이 코드에서 어떤 모습인지 언어별 예를 본다.'),
    link('OWASP · SQL Injection Prevention Cheat Sheet','https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html'),
    p('CRS의 점수 방식 설명이다. 5.6의 942100이 점수를 더하고 949110이 차단하는 구조를 읽는다.'),
    link('OWASP CRS · Anomaly Scoring','https://coreruleset.org/docs/2-how-crs-works/2-1-anomaly_scoring/'))

section('5장 참고 자료',
    p('화면은 Wazuh 4.10.0의 기존 kt66과 DVWA v1.10에서 2026년 11월 1일에 촬영했다.'),
    h('[1] DVWA와 실습 코드'),
    link('DVWA 공식 저장소','https://github.com/digininja/DVWA'),
    link('DVWA · SQL injection · low.php','https://github.com/digininja/DVWA/blob/master/vulnerabilities/sqli/source/low.php'),
    h('[2] kt66 WAF 구성과 CRS'),
    link('kt66 · web/Dockerfile · 63d4180','https://github.com/mrgrit/kt66/blob/'+COMMIT+'/web/Dockerfile'),
    link('OWASP CRS · Anomaly Scoring','https://coreruleset.org/docs/2-how-crs-works/2-1-anomaly_scoring/'),
    h('[3] curl'),
    link('curl · Manual','https://curl.se/docs/manpage.html'),
    h('[4] Apache 로그 형식'),
    link('Apache 2.4 · mod_log_config','https://httpd.apache.org/docs/2.4/mod/mod_log_config.html'),
    h('[5] SQL 인젝션'),
    link('OWASP · SQL Injection','https://owasp.org/www-community/attacks/SQL_Injection'),
    link('MySQL · Comments','https://dev.mysql.com/doc/refman/8.4/en/comments.html'),
    h('[6] Wazuh 웹 탐지 규칙'),
    link('Wazuh 4.10.0 · 0245-web_rules.xml','https://github.com/wazuh/wazuh/blob/v4.10.0/ruleset/rules/0245-web_rules.xml'),
    h('[7] XSS'),
    link('OWASP · Cross Site Scripting','https://owasp.org/www-community/attacks/xss/'),
    h('[8] 출력 위치에 맞는 처리'),
    link('OWASP · Cross Site Scripting Prevention Cheat Sheet','https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html'),
    h('[9] 경로 조작'),
    link('OWASP · Path Traversal','https://owasp.org/www-community/attacks/Path_Traversal'),
    h('[10] 브라우저의 Network 도구'),
    link('Chrome DevTools · Inspect network activity','https://developer.chrome.com/docs/devtools/network/'),
    link('Microsoft Edge · Inspect network activity','https://learn.microsoft.com/en-us/microsoft-edge/devtools/network/'),
    h('[11] Windows hosts 파일'),
    link('Microsoft Support · Hosts 파일 재설정','https://support.microsoft.com/en-us/windows/experience/how-to-reset-the-hosts-file-back-to-the-default'))

INVESTIGATION='''웹 요청 조사 기록 (요청 한 건마다)

실행 위치 · 시각 · 시간대:
요청 URL · 입력값 · 표식:
HTTP 응답 코드 · 화면 결과:
agent.name · data.srcip:
location · full_log:
_index · _id:
rule.id · data.id:
WAF transaction_id:
intercepted · CRS 규칙 · 차단 이유:
도달 지점(1~5)과 근거:
추가 확인할 사항:
hosts 변경 내용 · 원상복구 결과:
'''
README='''5장 REV01 복사용 입력

C05-01~ : 명령 블록 번호와 같은 파일. 실행 위치는 manifest.json의 where를 따른다.
Q05-01~07 : Discover 검색식. queries.json에 인덱스 패턴과 설명이 있다.
B05-01~08 : 브라우저 주소창·입력란에 붙여 넣는 값. 도메인 kt66.lab은 자신의 값으로 바꾼다.
browser/   : 검증 환경에서 기록된 접속 로그 원문과 경보(읽기 자료)
investigation.txt : 요청 한 건의 조사 기록 양식
'''

if __name__=='__main__':
    data={'title':'웹 공격의 시작과 입력값 검증','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','baseline':COMMIT,'revision':'REV01',
          'comments':'REV01 원고. 브라우저·Wazuh 결과는 2026-11-01 기존 kt66 실측(editorial/chapter05-review.json), curl은 이전 검증 기록을 따른다.','pages':pages}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'volume01-chapter05.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    EX.mkdir(parents=True,exist_ok=True)
    for old in list(EX.glob('C05-*.txt'))+list(EX.glob('Q05-*.txt')):old.unlink()
    for b in commands+queries:(EX/(b['id']+'.txt')).write_text(b['text']+'\n')
    (EX/'manifest.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
    (EX/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2)+'\n')
    for f in (ROOT/'examples/chapter05').glob('B05-*.txt'):shutil.copyfile(f,EX/f.name)
    (EX/'browser').mkdir(exist_ok=True)
    for f in (ROOT/'examples/chapter05/browser').iterdir():shutil.copyfile(f,EX/'browser'/f.name)
    (EX/'investigation.txt').write_text(INVESTIGATION)
    (EX/'README.txt').write_text(README)
    print(len(pages),'pages',len(commands),'commands',len(queries),'queries')
