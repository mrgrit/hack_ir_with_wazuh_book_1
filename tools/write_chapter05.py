"""5장: HTTP 요청 한 건을 보내고 웹 로그·WAF·Wazuh 결과를 대조한다."""
import json
from pathlib import Path
from write_chapter01 import p,h,tab,img,code
ROOT=Path(__file__).resolve().parents[1]
pages=[];commands=[];queries=[];browser_inputs=[]
A='공격자 VM · 터미널';H='kt66 VM · 호스트 터미널';W='kt66-web 컨테이너 안';S='kt66-siem 컨테이너 안'
def page(title,*blocks):pages.append({'title':title,'kind':'body','blocks':list(blocks)})
def c(text,why,result,where=A):
 b={'type':'command','id':f'C05-{len(commands)+1:02d}','text':text,'why':why,'result':result,'where':where};commands.append(b);return b
def q(text,why,result,index='wazuh-alerts-*'):
 b={'type':'query','id':f'Q05-{len(queries)+1:02d}','text':text,'why':why,'result':result,'where':'Windows · Discover · '+index};queries.append(b);return b
def sc(n,caption,width=127):return img('assets/screens/chapter05/'+n+'.png',caption,width)
def bs(n,caption,width=127):return img('assets/screens/chapter05/browser/'+n+'.png',caption,width)
def bi(name,text):
 browser_inputs.append({'file':name+'.txt','text':text})
 return code(text)
def fig(n,caption):return img('assets/figures/chapter05/'+n+'.png',caption)
def spot(n,caption):return {'type':'image','path':'assets/illustrations/chapter05/'+n+'.png','caption':caption,'width_mm':55,'align':'right'}
def req(endpoint,*values):
 return 'curl -sS -i --max-time 15 --get \\\n  "$DVWA/vulnerabilities/'+endpoint+'/" \\\n  '+' \\\n  '.join(values)
page('5장  웹 공격의 시작과 입력값 검증',
 h('5.1  요청·응답·로그를 연결하기'),
 p('DVWA에 SQL 구문, 스크립트, 파일 경로를 보낸다. 응답을 읽고 같은 요청을 웹 로그와 Wazuh에서 찾는다. Module 01 실습 01~03에 해당한다.'),
 tab(['항목','준비·확인'],[['실행 위치','Windows 브라우저, 로그 조회는 kt66 VM'],['선행 조건','kt66 실행, web 에이전트 연결, 3~4장의 Discover 사용'],['대상','자신의 kt66에 설치된 DVWA'],['성공 기준','보낸 입력과 응답 코드, 원문, 탐지 규칙을 대조하고 차단 근거를 설명한다.'],['실패 시','5.10에서 이름 해석 → 접속 → 원본 로그 → 수집 → 검색 순서로 확인한다.'],['원상복구','5.11에서 학습 단계와 hosts 변경을 복구하고 로그아웃한다.']],[30,97]),
 p('브라우저에서 값을 입력하고 버튼을 누른 뒤 응답과 Wazuh 기록을 읽는다. 같은 요청을 curl로 보내는 방법은 선택 실습인 5.13에 모았다.'),
 p('DVWA(Damn Vulnerable Web Application)는 웹 취약점을 학습하도록 만든 애플리케이션이다. kt66이 컨테이너로 실행한다. 이 장에서는 그 앞의 WAF가 공격 입력을 검사하는 과정도 함께 확인한다. [1]'))
page('5.1  웹 요청과 로그 수집 경로',
 p('Apache는 HTTP 요청을 받아 응답하는 웹 서버이다. kt66의 Apache는 DVWA로 요청을 전달하는 프록시 역할도 한다. 접속 기록은 kt66-web에 남는다.'),
 p('WAF(Web Application Firewall)는 웹 요청과 응답을 검사하는 방화벽이다. kt66은 Apache에 ModSecurity를 설치하고 OWASP CRS의 공격 탐지 규칙을 적용한다. DVWA 앞에서는 차단 모드로 동작한다. [2]'),
 fig('request-log-path','도식 5-1. 웹 요청과 로그 수집 경로.'),
 p('fw와 ips는 1장에서 구성한 방화벽·침입방지 장비이다. 이 장에서는 그 뒤의 웹 요청과 Apache·ModSecurity 기록을 조사한다.'),
 p('ModSecurity는 요청을 처리하는 중에 차단 여부를 결정한다. Wazuh는 web 에이전트가 보낸 로그를 분석해 경보로 분류한다. 두 도구의 규칙 번호는 서로 다르다.'))
page('5.2  브라우저 접속 준비',
 p('Windows PC에서 Chrome 또는 Edge를 연다. kt66 VM은 실행해 두며, 웹 실습에는 Windows 브라우저를 사용한다. 별도 공격자 VM은 5.13의 curl 실습을 선택할 때 필요하다.'),
 c("grep -E '^(WEB_HOST_IP|LAB_DOMAIN)=' .env",'kt66 저장소 디렉터리에서 실행한다. grep은 조건에 맞는 행을 찾는다. -E는 확장 정규표현식, ^는 행 시작, 괄호 안의 파이프(|)는 또는(OR)이다. 두 이름 뒤에 등호가 있는 설정을 찾는다.','WEB_HOST_IP와 LAB_DOMAIN을 적는다. 예시는 192.168.0.189와 kt66.lab이다.','kt66 VM · ~/kt66'),
 fig('name-and-host','도식 5-2. 웹 이름과 접속 주소.'),
 p('IP는 접속할 장비를 정하고 HTTP의 Host 헤더는 요청할 사이트 이름을 알린다. 같은 kt66 IP에 여러 웹 사이트가 있으므로 DVWA 이름으로 접속한다.'),
 p('LAB_DOMAIN이 ccc.com이면 주소는 http://dvwa.ccc.com이다. 아래 예시의 kt66.lab을 자신의 도메인으로 바꾼다.'))
page('5.2  Windows에 웹 이름 등록하기',
 p('hosts는 이름과 IP를 연결하는 파일이다. Windows에서 DVWA 이름을 kt66의 웹 진입 IP로 연결한다. [12]'),
 p('① 시작 메뉴에서 메모장을 검색한다. 마우스 오른쪽 버튼을 눌러 관리자 권한으로 실행을 선택한다.'),
 p('② 파일 → 열기에서 아래 폴더를 연다. 파일 형식을 모든 파일로 바꾸고 hosts를 선택한다.'),
 code(r'C:\Windows\System32\drivers\etc'),
 p('③ dvwa 이름이 있는지 찾는다. 있으면 기존 행을 메모하고 IP와 이름을 확인한다. 올바르면 그대로 둔다. 없으면 마지막에 다음 행을 추가한다.'),
 code('192.168.0.189 dvwa.kt66.lab'),
 p('④ Ctrl+S로 저장한다. 파일을 다시 열어 입력한 행이 남아 있는지 확인한다. 파일 이름은 확장자 없는 hosts이다.'),
 p('⑤ 브라우저 주소창에 아래 주소를 입력한다. DVWA 로고와 Username·Password 입력란이 나타나면 이름 연결이 된 것이다.'),
 bi('B05-01-login','http://dvwa.kt66.lab/login.php'),
 p('접속되지 않으면 kt66 기동 상태, hosts의 IP·이름, http 주소를 차례로 확인한다. 다른 사이트가 열리면 LAB_DOMAIN과 DVWA 이름을 다시 대조한다.'))
page('5.2  DVWA 로그인',
 p('kt66은 DVWA 프로그램을 컨테이너로 실행한다. 처음 사용할 때 필요한 학습용 DB는 다음 페이지에서 초기화한다. DVWA 로그인 계정은 Wazuh 계정과 다르다. [1]'),
 p('Username에 admin, Password에 password를 입력하고 Login을 누른다.'),
 bs('login-filled','화면 5-1. DVWA 계정 입력.',105),
 tab(['열린 화면','다음 행동'],[['Home과 실습 메뉴','로그인됐다. DVWA Security 설정으로 진행한다.'],['Database Setup','처음 사용하는 DB의 초기화를 진행한다.'],['Login failed','계정 입력과 기존 환경의 변경된 암호를 확인한다.']],[46,81]),
 p('기존 환경에서 계정이나 데이터를 사용 중이면 초기화하지 않고 해당 계정으로 로그인한다.'))
page('5.2  처음 사용하는 DB 초기화',
 p('로그인 후 Database Setup으로 이동했다면 학습용 테이블을 준비한다. 직접 열 때는 주소창에 다음 주소를 입력한다.'),
 bi('B05-02-setup','http://dvwa.kt66.lab/setup.php'),
 p('① 페이지 아래의 Create / Reset Database를 누른다. 사용자와 방명록 테이블, 연습용 자료를 만든다. 기존 DB가 있으면 그 자료와 계정이 초기 상태로 바뀐다.'),
 bs('setup-button','화면 5-2. 학습용 DB 초기화 버튼.'),
 p('② Setup successful!과 users·guestbook 테이블 생성 메시지를 확인한다.'),
 bs('setup-success','화면 5-3. 학습용 DB 생성 결과.'),
 p('③ 약 5초 뒤 로그인 화면으로 이동한다. 먼저 이동하려면 login 링크를 누른다. admin / password로 다시 로그인해 실습 메뉴를 확인한다.'),
 p('생성 오류가 나오면 오류 문구와 kt66-dvwa 실행 상태부터 확인한다. Setup Check의 allow_url_include나 reCAPTCHA 표시는 이번 장의 세 실습에 필요한 DB 생성 결과와 구분한다.'))
page('5.2  학습 단계와 메뉴 확인',
 p('DVWA Security는 애플리케이션의 입력 처리 단계를 고르는 메뉴이다. Low는 입력 검사가 약한 코드를 실행한다. 앞단 WAF의 검사·차단 설정은 별도로 적용된다.'),
 p('① 왼쪽 DVWA Security를 누른다. Security level is currently 옆의 현재 값을 메모한다.'),
 bs('security-current','화면 5-4. 현재 학습 단계.'),
 p('② 선택 상자에서 Low를 고르고 Submit을 누른다. 위의 현재 값이 low로 바뀌었는지 확인한다.'),
 bs('security-select','화면 5-5. Low 선택과 적용.'),
 p('③ 실습 메뉴는 SQL Injection, XSS (Reflected), File Inclusion 순서로 사용한다. 각각 사용자 번호 조회, 문자열 출력, 파일 선택 기능이다.'),
)
page('5.2  실습 메뉴',
 p('왼쪽 메뉴에서 이번 장의 세 기능을 선택한다. 거부 화면에서는 뒤로 가기로 DVWA에 돌아온 뒤 다음 메뉴를 연다.'),
 bs('menu','화면 5-6. DVWA 실습 메뉴.',43))
page('5.3  HTTP 요청과 브라우저 기록',
 p('HTTP는 클라이언트의 요청에 서버가 응답하는 통신 규약이다. 브라우저에서 링크나 Submit을 누르면 요청이 전송된다. HTTP 메서드는 요청의 동작을 나타내며, GET은 지정한 자원을 요청한다.'),
 code('GET /vulnerabilities/sqli/?id=1&Submit=Submit HTTP/1.1\nHost: dvwa.kt66.lab'),
 p('URL의 물음표(?) 뒤는 이름=값 형식의 쿼리 매개변수이다. 앰퍼샌드(&)는 여러 값을 구분한다.'),
 tab(['부분','뜻'],[['/vulnerabilities/sqli/','SQL 인젝션 실습 경로'],['id=1','조회할 사용자 번호'],['Submit=Submit','조회 버튼으로 전송한 값'],['HTTP/1.1','사용하는 HTTP 버전'],['Host','요청한 사이트 이름']],[52,75]),
 p('개발자 도구의 Network는 브라우저가 보낸 요청과 받은 응답을 보여 준다. Wazuh의 Dev Tools와는 다른 도구이다. [11]'),
 p('① DVWA 탭에서 Ctrl+Shift+I를 눌러 개발자 도구를 연다. Network(네트워크)를 선택한다. 탭이 숨겨졌으면 »에서 찾는다.'),
 p('② Preserve log 또는 Keep log(로그 보존)를 켠다. 페이지가 바뀌어도 요청 기록을 남긴다. 녹화 표시가 빨간색인지 확인한다. 회색이면 눌러 기록을 시작한다.'))
page('5.3  Network에서 확인할 항목',
 p('Network를 연 상태에서 페이지를 새로 고치면 요청이 한 행씩 나온다. HTML 외에 CSS와 이미지 요청도 생긴다. 분석할 문서 요청은 Type이 document인 행이다.'),
 bs('network-list','화면 5-7. Network의 요청 목록.'),
 tab(['항목','뜻'],[['Name','요청 경로와 쿼리'],['Status','HTTP 응답 코드'],['Type','document는 페이지 문서, stylesheet는 CSS 등 요청 자원 종류'],['Headers','Request URL·Request Method·Status Code와 헤더'],['Payload','전송한 쿼리 매개변수 또는 폼 값'],['Response','서버가 반환한 본문']],[38,89]),
 p('요청 이름을 누르면 세부 탭이 열린다. Headers의 General에서 URL·메서드·상태 코드를 읽는다. Payload에서는 id 같은 이름과 전달된 값을 대조한다.'),
 p('실습 전에 Windows의 설정 → 시간 및 언어 → 날짜 및 시간에서 시각이 맞는지 확인한다. 요청 시각을 기록해 Discover의 시간 범위를 맞춘다.'))
page('5.3  응답 코드와 입력값 읽기',
 tab(['응답','확인할 내용'],[['200 OK','반환된 본문과 화면을 읽는다.'],['302 Found','Location 헤더의 주소로 이동하라는 응답이다. 브라우저는 보통 자동으로 이동한다.'],['403 Forbidden','요청 거부이다. 차단 주체와 이유는 WAF 기록에서 확인한다.']],[38,89]),
 p('브라우저는 폼의 특수문자를 URL에 넣을 수 있게 인코딩한다. 바이트 값을 %와 16진수 두 자리로 표현한다. 주소창에서 읽는 표시와 Network의 실제 요청 URL을 대조한다.'),
 tab(['표기','해석'],[['%27','작은따옴표(\')'],['%20 또는 +','이 실습의 쿼리 값에서 공백'],['%3C · %3E','여는 꺾쇠(<) · 닫는 꺾쇠(>)'],['%2F · %2C','슬래시(/) · 쉼표(,)'],['%28 · %29','여는 소괄호 · 닫는 소괄호']],[43,84]),
 p('Network에서 기록을 지우는 Clear 버튼은 목록만 비운다. Wazuh와 서버에 수집된 로그는 그대로 남는다.'))

page('5.4  정상 값을 입력하고 조회하기',
 p('① DVWA 왼쪽 SQL Injection을 누른다. User ID에 1을 입력한다.'),
 bs('normal-input','화면 5-8. 사용자 번호 입력.'),
 p('② Network의 Clear 버튼으로 목록을 비운다. DVWA의 Submit을 누른다.'),
 bs('normal-result','화면 5-9. 사용자 1의 조회 결과.'),
 p('③ 화면에 ID: 1, First name: admin, Surname: admin이 나온다. 입력한 번호로 한 사용자를 조회한 결과이다.'),
 spot('request','삽화. 웹 요청 시험.'))
page('5.4  정상 요청의 응답 확인',
 p('Network에서 sqli/?id=1&Submit=Submit 문서 요청을 누른다. Headers를 열어 GET과 200 OK를 확인한다.'),
 bs('normal-headers','화면 5-10. 정상 요청의 URL·메서드·응답.'),
 p('Payload의 Query String Parameters에서 id가 1, Submit이 Submit인지 확인한다. Response에는 앞에서 본 이름이 HTML 본문에 들어 있다.'),
 p('실습 시각과 Request URL을 적는다. 다음 Wazuh 검색에서는 같은 경로와 입력값을 찾는다. 로그인 상태라서 사용자 정보가 조회됐다. 로그인 전의 요청은 로그인 화면으로 이동할 수 있다.'))

page('5.4  아카이브에서 기준 기록 찾기',
 p('Windows의 Discover에서 wazuh-archives-*와 Last 24 hours를 선택한다. 정상 입력은 경보가 없어도 아카이브에 수집될 수 있다.'),
 q('agent.name: "web"\nAND data.url: "/vulnerabilities/sqli/?id=1&Submit=Submit"','agent.name은 수집 에이전트이다. web이 수집한 URL 중 정상 조회 경로와 입력값이 일치하는 기록을 찾는다.','실습 시각의 행을 펼쳐 data.id의 200과 data.url을 확인한다. data.srcip은 요청을 보낸 PC의 출발지 주소이다.','wazuh-archives-*'),
 bs('normal-data','화면 5-2. 정상 입력의 수집 기록.'),
 p('출발지 주소가 네트워크 장비에서 변환되면 PC의 주소와 다를 수 있다. 이후 검색에는 해당 요청에서 읽은 data.srcip 값을 쓴다.'),
 p('data.protocol은 이 웹 로그에서 HTTP 메서드인 GET을 담는다. data.id는 HTTP 응답 코드이다. rule.id는 Wazuh 탐지 규칙 번호이므로 구분한다.'),
 p('location은 /var/log/apache2/dvwa_access.log이다. 결과가 없으면 다음 페이지에서 원본 파일부터 확인한다.'))
page('5.4  Apache 원본 로그 확인',
 p('웹 로그는 kt66-web 컨테이너에 있다. access 로그는 접속과 응답, error 로그는 처리 오류와 ModSecurity 메시지를 기록한다. modsec_audit.log는 WAF가 검사한 요청의 상세 기록이다.'),
 c('docker exec -it kt66-web /bin/bash','kt66 호스트에서 웹 컨테이너의 Bash로 들어간다. -i는 입력 유지, -t는 터미널 할당이다.','이후 두 명령은 kt66-web 안에서 실행한다.',H),
 c('cd /var/log/apache2','cd는 작업 디렉터리를 옮긴다. Apache 로그 디렉터리로 이동한다.','이제 파일명으로 로그를 조회할 수 있다.',W),
 c("grep -F '/vulnerabilities/sqli/?id=1&Submit=Submit' \\\n  dvwa_access.log",'grep은 조건에 맞는 행을 찾는다. -F는 작은따옴표 안의 URL을 정규표현식으로 해석하지 않고 그대로 찾는다. 줄 끝의 역슬래시(\\)는 다음 줄까지 한 명령으로 잇는다.','실습 시각의 행에서 출발지 IP, GET 요청과 200 응답을 읽는다.',W),
 c('exit','웹 컨테이너의 셸을 끝낸다.','kt66 호스트 터미널로 돌아온다.',W),
 p('파일에 기록이 없으면 DVWA 이름이 올바른 사이트로 연결되는지 확인한다. 파일에는 있으나 Discover에 없으면 web 에이전트 연결과 수집 설정을 확인한다.'))
page('5.4  접속 로그 한 행 읽기',
 p('아래는 브라우저 접속 로그의 요청·응답 부분이다. 원문 전체는 examples/chapter05/browser/normal.log에 있다. [4]'),
 code('10.20.30.254 - -\n[01/Nov/2026:21:12:21 +0900]\n"GET /vulnerabilities/sqli/?id=1&Submit=Submit\nHTTP/1.1"\n200 1792'),
 tab(['원문의 부분','뜻·Wazuh 필드'],[['첫 번째 IP','접속 출발지 · data.srcip'],['뒤의 두 개 -','원격 사용자 식별값·인증 사용자명이 기록되지 않았다.'],['[날짜:시각 시간대]','Apache가 기록한 시각·시간대'],['GET','HTTP 메서드 · data.protocol'],['/vulnerabilities/sqli/?…','요청 대상과 입력값 · data.url'],['HTTP/1.1','HTTP 버전'],['200','응답 코드 · data.id'],['1792','이 환경에서는 헤더를 포함한 송신 바이트 수'],['뒤의 두 따옴표 값','Referer · User-Agent']],[51,76]),
 p('Referer는 이전 페이지 주소를 알리는 헤더이다. 이번에는 SQL 입력 화면의 주소가 들어간다. User-Agent는 브라우저가 보낸 제품·환경 문자열이다.'),
 p('원문 전체는 full_log, 수집 파일은 location에 저장된다. 브라우저 화면의 결과와 응답 코드, 로그 시각을 함께 대조한다.'))

page('5.5  SQL 인젝션 · 조회 입력',
 p('DVWA는 사용자 자료를 테이블에 저장한다. 테이블의 한 행은 사용자 한 명, 열은 이름·번호 같은 항목이다. id로 받은 번호를 조회 조건에 쓴다. SQL은 데이터베이스에서 자료를 조회·변경하는 언어이다. 다음은 입력 검사가 약한 low 단계의 조회문 구조이다. [1][5]'),
 code("SELECT first_name, last_name\nFROM users\nWHERE user_id = '1';"),
 tab(['구문','뜻'],[['SELECT first_name, last_name','이름과 성 열을 조회한다.'],['FROM users','조회할 테이블은 users이다.'],["WHERE user_id = '1'",'사용자 번호가 1인 행을 선택한다.'],["작은따옴표(') · 세미콜론(;)",'문자열 값을 감싼다 · SQL 문장을 끝낸다.']],[64,63]),
 p('SQL 인젝션은 입력값이 SQL 문법의 일부로 해석되어 원래 조회 의도가 바뀌는 취약점이다. 입력을 SQL 문자열에 그대로 결합하면 이런 문제가 생길 수 있다.'),
 fig('sql-context','도식 5-3. 입력값을 SQL 문자열에 결합하는 처리.'),
 p('조회 코드는 kt66-dvwa 컨테이너의 다음 파일에 있다.'),
 code('/var/www/html/vulnerabilities/sqli/source/low.php'),
 p('Discover의 DQL은 저장된 기록을 검색하는 식이다. 여기서 애플리케이션이 데이터베이스에 보내는 SQL과 구분한다.'))
page('5.5  SQL 인젝션 · 입력 구문',
 p('id 값에 다음 문자열을 넣는다. 페이로드(payload)는 공격 동작을 유도하려고 보내는 입력값을 뜻한다.'),
 bi('B05-03-sqli',"1' UNION SELECT user,password FROM users-- "),
 tab(['부분','의도'],[["1'",'번호 뒤의 작은따옴표로 기존 문자열 값을 끝낸다.'],['UNION','기존 조회 결과에 다른 SELECT의 결과를 결합한다.'],['SELECT user,password','계정명과 저장된 암호값 열을 선택한다.'],['FROM users','그 값을 users 테이블에서 읽으려 한다.'],['-- 뒤의 공백','MySQL에서 뒤에 붙을 나머지 SQL을 주석으로 처리한다.']],[49,78]),
 p('앞 조회는 두 열을 반환한다. 두 번째 SELECT도 user와 password라는 두 열을 지정한다. 실제 동작 여부는 DB 구문, 열의 형식, 애플리케이션 처리와 접근 권한에 달려 있다.'),
 p('User ID에 넣을 값이다. -- 뒤에는 공백 한 칸을 둔다. 복사용 값은 B05-03-sqli.txt에 있다.'),
 p('이 실습에서는 먼저 WAF가 이 입력을 어떻게 처리하는지 확인한다.'))
page('5.5  SQL 구문을 입력하고 전송하기',
 p('① SQL Injection의 User ID를 앞의 SQL 문자열로 바꾼다. 입력란이 짧아도 복사용 값 전체를 붙여 넣는다.'),
 bs('sqli-input','화면 5-11. User ID에 SQL 구문 입력.'),
 p('② Network 목록을 비우고 Submit을 누른다. 검증 환경에서는 Forbidden 화면으로 바뀌었다.'),
 bs('sqli-blocked','화면 5-12. SQL 요청의 거부 응답.'),
 p('③ Network의 해당 문서 요청을 누른다. Headers에서 403을 확인하고 Payload에서 입력한 SQL이 전달됐는지 읽는다.'))
page('5.5  SQL 요청을 Wazuh에서 찾기',
 bs('sqli-headers','화면 5-13. SQL 요청의 URL과 응답 코드.'),
 q('agent.name: "web" AND data.url: *vulnerabilities/sqli/*\nAND data.url: *UNION*','Discover에서 wazuh-alerts-*를 선택하고 실습 시간으로 좁힌다. 별표(*)는 임의 문자열에 일치한다. SQL 실습 경로에서 UNION을 보낸 요청을 찾는다.','출발지와 시각이 맞는 행을 펼친다. rule.id, data.id, data.url을 기록한다.'),
 p('200이나 302가 나왔다면 본문·로그인 상태·입력값·WAF 설정 순서로 확인한다. DB 자료가 반환됐는지까지 읽어야 실행 결과를 판단할 수 있다.'))

page('5.5  SQL 인젝션 · 경보 해석',
 bs('sqli-data','화면 5-3. SQL 입력과 응답 코드.'),
 bs('sqli-rule','화면 5-4. SQL 인젝션 탐지 설명.'),
 tab(['확인 항목','이 사례의 해석'],[['data.url','%27은 작은따옴표, +는 공백, %2C는 쉼표로 읽는다. UNION SELECT 구문을 찾는다.'],['data.id: 403','웹 서버가 요청을 거부했다.'],['data.srcip','브라우저 요청이 웹 서버에 도착할 때의 출발지 주소이다.'],['rule.id: 31103','Wazuh가 SQL 인젝션 시도로 분류했다.'],['rule.description','SQL injection attempt. · SQL 인젝션 시도'],['rule.firedtimes','해당 규칙에 일치한 누적 횟수이다.']],[45,82]),
 p('화면의 URL에서 &amp;는 매개변수를 구분하는 &의 HTML 표기이다. full_log의 원문과 대조한다.'),
 p('Wazuh의 기본 규칙 31103은 URL의 SQL 공격 관련 문자열을 찾는다. 데이터베이스가 그 SQL을 실행했는지는 이 접속 로그로 확인되지 않는다. [6]'))
page('5.6  WAF 차단 근거 찾기',
 p('403만으로 차단 주체를 확정할 수는 없다. 같은 요청의 ModSecurity 감사 기록을 찾아 WAF가 차단했는지 확인한다.'),
 q('agent.name: "web"\nAND location: "/var/log/apache2/modsec_audit.log"\nAND data.request.request_line: *UNION*','Discover의 패턴을 wazuh-archives-*로 바꾼다. location은 감사 로그 파일, request_line의 UNION으로 SQL 요청을 찾는다. AND로 세 조건을 모두 만족하는 기록을 찾는다.','한 행을 펼쳐 data.request.request_line의 SQL 입력, transaction의 출발지와 시각을 앞의 접속 로그와 대조한다.','wazuh-archives-*'),
 bs('waf-action','화면 5-5. ModSecurity의 차단 결정.'),
 tab(['필드','뜻'],[['action.intercepted: true','WAF가 해당 요청의 처리를 차단했다.'],['action.phase: 2','요청 본문 검사 단계이다. URL 매개변수도 이 단계의 규칙으로 검사할 수 있다.'],['action.message','차단 평가의 비교 조건이다. anomaly_score가 기준 이상인지 검사했다.']],[57,70]),
 p('화면의 전체 필드 이름은 data.audit_data.action으로 시작한다. action은 처리 결정, intercepted는 가로막았는지를 나타낸다.'))
page('5.6  감사 기록의 응답과 규칙',
 bs('waf-response','화면 5-6. 감사 기록의 응답과 접속 정보.'),
 tab(['필드','확인할 내용'],[['data.response.status','응답 코드 403'],['transaction.remote_address','요청의 출발지 주소'],['transaction.local_address','요청을 받은 web 주소 10.20.32.80'],['transaction.local_port','web이 요청을 받은 HTTP 포트 80'],['transaction.remote_port','공격자 연결에 임시 배정된 출발지 포트'],['transaction.time','원본 처리 시각과 시간대'],['transaction.transaction_id','WAF가 요청을 구별하는 식별자']],[61,66]),
 p('transaction으로 시작한 항목은 data.transaction 아래에 있다. 시각·출발지·요청 URL이 같은지 대조한다.'))
page('5.6  WAF 규칙과 차단 이유',
 p('감사 기록의 JSON 탭을 연다. data.audit_data.messages에는 일치한 CRS 규칙과 차단 이유가 들어 있다. 다음 번호와 문구를 찾는다.'),
 code('942100 · SQL Injection Attack Detected\n949110 · Access denied with code 403'),
 p('CRS는 탐지 규칙이 부여한 점수를 합산하고 차단 기준과 비교한다. 이 요청은 점수가 기준 5 이상이어서 949110이 차단했다. 실제 합산 점수는 감사 기록의 메시지에서 읽는다. 942100은 WAF 규칙, 31103은 Wazuh 규칙이다. [2]'),
 p('시각·출발지·요청 URL이 같은지 대조한 뒤 “SQL 인젝션 입력을 WAF가 차단했다”로 기록한다.'))
page('5.7  XSS · 입력이 실행되는 위치',
 p('DVWA의 반사형 XSS 실습은 name에 받은 값을 응답 HTML에 넣는다. XSS(Cross-Site Scripting)는 입력한 스크립트가 웹 페이지의 코드로 해석되어 브라우저에서 실행되는 취약점이다. [7]'),
 bi('B05-04-xss','<script>alert(1)</script>'),
 tab(['부분','뜻'],[['<script> · </script>','HTML에서 스크립트 영역의 시작과 끝을 표시한다.'],['alert(1)','JavaScript의 알림 창에 숫자 1을 표시한다. 소괄호 안은 함수에 전달하는 값이다.']],[48,79]),
 fig('xss-context','도식 5-4. 반사형 XSS의 실행 과정.'),
 p('반사형은 요청의 입력값이 곧바로 응답에 포함되는 방식이다. 이 장의 사례는 WAF가 해당 요청을 차단한 경우이다.'),
 p('SQL 인젝션은 데이터베이스의 SQL 해석을, XSS는 브라우저의 HTML·스크립트 해석을 노린다.'))
page('5.7  이름 입력란에 스크립트 보내기',
 p('① 거부 화면에서는 뒤로 가기를 눌러 DVWA로 돌아온다. 왼쪽 XSS (Reflected)를 누른다.'),
 p('② What’s your name?에 <script>alert(1)</script>를 넣는다. Network 목록을 비우고 Submit을 누른다.'),
 bs('xss-input','화면 5-14. 이름 입력란의 스크립트.'),
 bs('xss-blocked','화면 5-15. XSS 요청의 거부 응답.'),
 p('③ 검증 환경에서는 403 응답이 나왔고 알림 창은 열리지 않았다. Network의 Payload에서 name 값을 대조한다.'))
page('5.7  XSS 요청의 경보 읽기',
 q('agent.name: "web" AND data.url: *vulnerabilities/xss_r/*\nAND rule.id: "31105"','wazuh-alerts-*에서 실습 시간의 XSS 경보를 찾는다.','출발지·시각·name 값을 대조하고 data.id의 403을 읽는다.'),
 bs('xss-data','화면 5-16. 스크립트 입력의 수집 기록.'),
 p('URL의 %3Cscript%3E는 <script>이다. %28과 %29는 소괄호, %2F는 닫는 태그의 슬래시이다. 인코딩을 읽어 입력한 값과 대조한다.'))

page('5.7  XSS · 판정과 대응',
 p('31105의 설명은 XSS (Cross Site Scripting) attempt.이다. 이 규칙은 URL의 script 관련 문자열 등을 검사한다. 브라우저에서 코드가 실행됐다는 뜻은 아니다. [6]'),
 tab(['관찰','판정·다음 확인'],[['요청 URL에 스크립트가 있다','XSS 입력을 전송했다.'],['403과 WAF intercepted: true','같은 요청을 WAF가 차단했다.'],['응답이 200이다','응답 HTML에서 입력이 어떻게 들어갔는지 확인한다.'],['브라우저에서 시험 코드가 실행된다','그 페이지에서의 XSS 실행 근거가 된다.']],[57,70]),
 p('5.6의 감사 로그 검색에서 마지막 조건을 data.request.request_line: *xss_r*로 바꾼다. request_line과 response.status, action.intercepted를 확인한다.'),
 p('애플리케이션은 입력값을 HTML의 문자로 표시하도록 출력 위치에 맞게 처리해야 한다. 예를 들어 HTML 본문에서 <를 &lt;로 출력하면 태그 시작으로 해석되지 않는다. HTML 속성·JavaScript·URL은 각각 다른 처리가 필요하다. [8]'),
 spot('review','삽화. 응답과 탐지 기록 대조.'))
page('5.8  경로 조작과 파일 포함',
 p('DVWA의 파일 포함 실습은 page 값으로 읽을 파일을 고른다. 디렉터리 트래버설은 ../ 같은 경로 표현으로 허용한 디렉터리 밖의 파일에 접근하려는 공격이다. [9]'),
 p('LFI(Local File Inclusion)는 웹 애플리케이션이 입력값에 따라 서버 내부 파일을 포함하는 취약점이다. 이 실습에서는 파일 포함 기능에 상위 경로를 넣는다.'),
 code('../../../../../etc/passwd'),
 tab(['부분','뜻'],[['../','현재 디렉터리의 상위 디렉터리로 이동한다.'],['다섯 번의 ../','예시 시작 경로에서 루트 디렉터리까지 올라간다.'],['/etc/passwd','리눅스 계정 이름·UID·홈·로그인 셸 등이 있는 파일이다. 암호 해시 파일은 /etc/shadow이다.']],[43,84]),
 fig('path-context','도식 5-5. 입력 경로를 그대로 사용한 파일 접근.'),
 p('시작 디렉터리와 파일 접근 권한에 따라 결과가 달라진다. 경로 문자열이 로그에 있다는 사실과 파일 내용이 응답에 나왔다는 사실을 구분한다.'))
page('5.8  파일 선택 기능 확인',
 p('① DVWA의 File Inclusion을 누른다. file1.php, file2.php, file3.php 링크가 보인다.'),
 bs('file-menu','화면 5-17. File Inclusion의 파일 선택.'),
 p('② file1.php를 누른다. 주소창의 ?page=file1.php와 본문의 파일 내용을 확인한다. page 값으로 서버가 포함할 파일을 고르는 기능이다.'),
 bs('file-normal','화면 5-18. file1.php를 선택한 결과.'),
 p('File 1 화면의 IP는 DVWA에 요청을 전달한 웹 프록시의 주소이다. 요청을 보낸 PC의 출발지는 Wazuh의 data.srcip에서 확인한다.'),
 p('allow_url_include 관련 문구는 URL을 통해 원격 파일을 포함하는 PHP 설정을 가리킨다. 다음 단계는 서버 내부의 경로를 보내므로 이 설정을 켤 필요가 없다.'))
page('5.8  주소창에서 파일 경로 바꾸기',
 p('① 주소창에서 물음표 뒤의 page=file1.php를 아래 값으로 바꾼다. 앞의 http 주소·이름·/vulnerabilities/fi/는 그대로 둔다.'),
 bi('B05-05-path-raw-query','page=../../../../../etc/passwd\n&bookcase=book05-browser-path-raw'),
 p('위의 두 줄은 줄바꿈 없이 붙인다. bookcase는 로그에서 이 요청을 찾을 표식이다. 전체 주소는 B05-06-path-raw-url.txt에서 복사할 수 있다.'),
 p('② Enter를 누른다. 검증 환경에서는 Forbidden 화면이 나왔다. Network의 문서 요청을 눌러 URL의 page 값과 403 응답을 확인한다.'),
 bs('path-blocked','화면 5-19. 파일 경로 요청의 거부 응답.'),
 q('agent.name: "web"\nAND data.url: *book05-browser-path*','wazuh-alerts-*에서 경로 요청의 표식을 찾는다. 다음 인코딩 비교 요청도 같은 검색에 포함된다.','현재 요청의 data.url·data.id·rule.id를 기록한다. 검증 환경은 403과 31104였다.'))
page('5.8  주소창에서 인코딩만 바꾸어 비교',
 p('① 같은 주소에서 물음표 뒤를 다음 값으로 바꾼다. %2F는 슬래시이다. 경로 값의 뜻은 유지하고 URL에 보내는 표기만 바꾼다.'),
 bi('B05-07-path-encoded-query','page=..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd\n&bookcase=book05-browser-path'),
 p('두 줄을 붙여 입력한 뒤 Enter를 누른다. 전체 주소는 B05-08-path-encoded-url.txt에 있다. Network에서 실제 Request URL과 403 응답을 확인한다.'),
 p('② 앞의 Discover 검색에서 Refresh를 누른다. 시각과 표식으로 두 요청을 골라 data.url과 rule.id를 비교한다.'),
 tab(['보낸 형태','검증 환경의 Wazuh 결과'],[['슬래시를 그대로 전달','31104 · Common web attack.'],['슬래시를 %2F로 인코딩','31101 · 400번대 응답 분류']],[64,63]),
 bs('path-data','화면 5-20. 경로 조작 요청의 수집 기록.'),
 p('기본 규칙 31104에는 ../.. 등의 문자열 조건이 있다. 서버에서 같은 경로로 해석해도 URL에 남은 문자열에 따라 분류가 달라진다. [6]'))

page('5.8  파일이 읽혔는지 판단하기',
 p('이 실습의 두 요청은 WAF에서 차단되었다. 파일 내용이 반환된 기록은 없다. 다음과 같이 근거를 나누어 적는다.'),
 tab(['대상','확인 근거'],[['접근 시도','page 값에 상위 경로와 etc/passwd가 있다.'],['WAF 차단','같은 요청의 intercepted: true와 응답 403'],['파일 노출','응답 본문에 대상 파일의 내용이 있는지 확인해야 한다.'],['후속 조사','같은 출발지가 다른 파일과 경로도 요청했는지 찾는다.']],[38,89]),
 p('애플리케이션은 page에 실제 파일 경로를 직접 받기보다 home, help처럼 허용한 이름을 받고 서버에서 고정된 파일에 대응시키는 방식으로 바꾼다. 경로를 받을 필요가 있으면 정규화한 최종 경로가 허용 디렉터리 안에 있는지 검사한다.'),
 p('LFI에는 상위 경로 외에 PHP의 파일 처리 기능을 이용하는 변형도 있다. 문자열 필터 한두 개로 모든 파일 접근을 막을 수 있다고 가정하지 않는다. 이 장의 재현 대상은 앞의 경로 조작 두 요청이다.'))
page('5.9  탐지 조건을 넓혀 찾기',
 p('bookcase는 실습에서 붙인 표식이다. 실제 조사에서는 요청 경로·출발지·공격 문자열·탐지 규칙을 조합한다. 아래 조건은 이 장에서 확인한 경로 조작을 찾는 예이다.'),
 q('agent.name: "web" AND\n(rule.id: "31104" OR data.url: *etc*passwd*)','OR는 양쪽 조건 중 하나를 만족하면 선택한다. 소괄호는 그 범위를 묶는다. *etc*passwd*는 etc와 passwd 사이의 / 또는 %2F도 포함하도록 찾는다.','경로 조작 규칙에 일치한 요청과 파일명 문자열이 들어간 요청을 함께 읽는다. 이 장 밖의 기록도 나올 수 있다.'),
 p('자신의 브라우저 요청의 출발지 IP와 실습 시간을 추가해 범위를 좁힌다. data.srcip의 값은 앞에서 읽은 data.srcip 값으로 바꾼다.'),
 q('agent.name: "web" AND data.srcip: "10.20.30.254"\nAND (rule.id: "31104" OR data.url: *etc*passwd*)','AND로 출발지 조건을 추가한다. 기간은 실습 시작·종료 시각으로 지정한다.','같은 출발지의 요청을 URL과 응답 코드로 묶어 읽는다.'),
 p('공격 문자열 검색은 조사 후보를 찾는 방법이다. 정상 입력과 비슷한 문자열도 함께 나올 수 있으므로 원문과 응답, 애플리케이션의 기능을 확인한다. [10]'))
page('5.9  세 종류의 근거 대조',
 fig('evidence','도식 5-6. 응답·차단 결정·로그 분류의 대조.'),
 tab(['관찰한 값','해석'],[['HTTP 403','클라이언트가 거부 응답을 받았다.'],['WAF intercepted: true','WAF가 요청 처리를 차단했다.'],['rule.id 31103·31105·31104','접속 로그가 SQL·XSS·일반 웹 공격 조건에 일치했다.'],['rule.id 31106','공격 관련 URL이 200 응답을 받았다. 침투 성공 여부는 본문과 서버 동작으로 확인한다.']],[57,70]),
 p('31106의 설명에는 success가 들어 있지만 조건은 공격 관련 상위 규칙과 응답 코드 200이다. DB 자료 노출·브라우저 실행·파일 반환을 직접 확인하는 규칙은 아니다. [6]'),
 p('입력값 검증은 예상한 형식·범위·허용값만 받아들이는 작업이다. SQL은 문장을 고정하고 값을 별도로 전달하는 매개변수 바인딩을 적용한다. XSS에는 출력 위치에 맞는 처리, 파일 기능에는 접근 범위 제한을 적용한다.'))
page('5.10  결과가 다를 때',
 tab(['증상','확인 순서'],[['사이트 이름을 찾을 수 없다','주소창의 이름 → Windows hosts의 이름·IP'],['Connection refused 또는 시간 초과','kt66 기동 → Windows와 kt66의 주소·브리지 → 웹 진입 IP와 80번 포트'],['로그인 페이지 대신 다른 사이트','LAB_DOMAIN → 주소창 → Windows hosts 항목'],['공격 응답이 200 또는 302','응답 본문 → 요청 입력값 → 올바른 사이트인지 → WAF의 적용 설정'],['Apache 원문이 없다','이름·접속 경로 → kt66-web의 dvwa_access.log → 요청 시각·URL'],['원문은 있으나 검색 결과가 없다','인덱스·기간 → DQL·필터 → web 에이전트 상태 → localfile 설정'],['예상한 공격 규칙이 없다','인코딩된 URL → data.id → 다른 rule.id → WAF 감사 로그']],[48,79]),
 p('조건을 고친 뒤 요청 한 건을 다시 보내고 새 시각으로 찾는다. 기존 경보는 바뀐 요청의 결과를 보여 주지 않는다.'))
page('5.10  WAF와 수집 설정 확인',
 c('docker exec -it kt66-web /bin/bash','kt66 호스트에서 웹 컨테이너에 들어간다.','아래 설정 조회를 컨테이너 안에서 진행한다.',H),
 c("grep -n -E '^SecRuleEngine|^SecAuditEngine' \\\n  /etc/modsecurity/modsecurity.conf",'-n은 줄 번호, -E는 확장 정규표현식이다. 캐럿(^)은 행 시작, 파이프(|)는 또는(OR)을 의미한다.','기준 환경은 SecRuleEngine On, SecAuditEngine RelevantOnly이다.',W),
 c("grep -n -E 'ServerName|SecRuleEngine' \\\n  /etc/apache2/sites-enabled/020-dvwa.conf",'DVWA 사이트의 이름과 별도 검사 모드가 있는지 읽는다.','ServerName이 자신의 dvwa 도메인인지 확인한다. 기준 DVWA 파일에는 검사 모드 재정의가 없어 전역 On을 사용한다.',W),
 p('On은 차단 동작을 적용한다. DetectionOnly는 규칙을 검사하고 기록하지만 차단하지 않는 모드이다. RelevantOnly는 관련 응답·감사 조건을 만족한 요청의 상세 기록을 남긴다.'),
 )
page('5.10  수집 설정 확인',
 p('앞 페이지에서 접속한 kt66-web 안에서 계속한다. Wazuh 에이전트의 localfile은 수집할 파일 경로와 해석 형식을 지정한다.'),
 c("grep -F -B 1 -A 1 '*_access.log' \\\n  /var/ossec/etc/ossec.conf",'-F로 경로 문자열을 찾고 -B 1과 -A 1로 앞뒤 한 줄을 함께 출력한다. 작은따옴표 안의 *는 grep에 문자 그대로 전달한다.','log_format apache와 /var/log/apache2/*_access.log를 확인한다. 설정 경로의 *는 여러 사이트의 access 파일을 수집하도록 지정한 것이다.',W),
 c("grep -F -B 1 -A 1 'modsec_audit.log' \\\n  /var/ossec/etc/ossec.conf",'감사 로그의 수집 항목과 앞뒤 한 줄을 읽는다.','log_format json과 /var/log/apache2/modsec_audit.log를 확인한다.',W),
 c('exit','설정 확인을 마친다.','호스트 터미널로 돌아온다.',W))
page('5.10  Wazuh 규칙 파일 확인',
 p('웹 접속 로그의 기본 탐지 조건은 kt66-siem의 아래 파일에 있다. Wazuh Manager가 설치할 때 제공하는 규칙이다.'),
 code('/var/ossec/ruleset/rules/0245-web_rules.xml'),
 c('docker exec -it kt66-siem /bin/bash','웹 로그를 분석하는 Manager 컨테이너에 접속한다.','아래 조회는 kt66-siem 안에서 실행한다.',H),
 c('cd /var/ossec/ruleset/rules','기본 규칙 디렉터리로 이동한다.','파일명으로 웹 규칙을 조회할 수 있다.',S),
 c('grep -n -A 9 \'<rule id="31104"\' \\\n  0245-web_rules.xml','줄 번호를 붙이고 일치한 행 뒤의 아홉 줄까지 읽는다. -n은 줄 번호, -A 9는 뒤쪽 문맥이다.','if_sid는 상위 규칙, url은 요청 URL의 문자열 조건이다. ../.. 조건과 Common web attack. 설명을 읽는다.',S),
 c('exit','규칙 조회를 마친다.','kt66 호스트 터미널로 돌아온다.',S))
page('5.11  원상복구와 결과 보관',
 p('① DVWA Security를 연다. 5.2에서 메모한 단계로 돌리고 Submit을 누른다. Security level is currently 옆의 값이 원래대로인지 확인한다.'),
 p('② Logout을 누른다. 로그인 화면이 나오면 DVWA 세션을 종료한 것이다.'),
 p('③ Windows hosts를 수정했다면 메모장을 관리자 권한으로 열고 변경한 행을 확인한다. 다음 실습에서도 쓸 이름은 유지한다. 제거할 때는 추가한 행만 지우거나 수정 전 값으로 되돌린다. 저장 후 파일을 다시 열어 확인한다.'),
 p('④ Network의 로그 보존을 끄고 개발자 도구를 닫는다. Discover의 검색식·필터를 비우고 wazuh-alerts-*, Last 24 hours로 되돌린다.'),
 p('초기화로 만든 학습용 DB는 다음 실습에서도 사용한다. Create / Reset Database는 복구 버튼이 아니며 다시 누르면 자료가 초기화된다. 접속 로그와 경보는 조사 자료로 남긴다.'))
page('5.12  조사 결과 정리',
 tab(['브라우저에서 한 행동','관찰 결과'],[['User ID에 1 입력·Submit','200 · 사용자 1의 이름 표시'],['User ID에 SQL 입력·Submit','403 · Wazuh 31103 · WAF 차단'],['이름 입력란에 스크립트·Submit','403 · Wazuh 31105 · WAF 차단'],['주소창에 원래 경로 입력','403 · Wazuh 31104'],['주소창에 인코딩한 경로 입력','403 · Wazuh 31101']],[62,65]),
 p('표는 검증 환경의 결과이다. 자신의 요청마다 아래 항목을 적는다.'),
 tab(['항목','기록할 내용'],[['요청','실행 PC·시각·메뉴·입력값·Request URL'],['응답','HTTP 상태·화면 결과·관련 본문'],['접속 로그','출발지·시각·location·full_log'],['Wazuh','인덱스·문서 ID·rule.id·data.id'],['WAF','transaction_id·intercepted·규칙·차단 이유'],['판단','입력 시도·차단·실행 여부와 각각의 근거']],[30,97]),
 p('양식은 examples/chapter05/investigation.txt이다. 다음 장에서는 웹 경로 탐색과 인증 요청의 기록을 조사한다.'))
page('5.13  다른 방법 · 같은 요청을 curl로 보내기',
 p('앞의 실습은 브라우저로 마쳤다. curl은 URL로 요청을 보내고 응답을 터미널에 출력하는 도구이다. 같은 입력을 명령으로 지정하는 방법을 비교하려면 이 절을 진행한다.'),
 p('실행 위치는 1.12의 Ubuntu 22.04 공격자 VM이다. kt66과 같은 Bridged 네트워크에 연결한다. 1.12의 일괄 설치에 curl이 포함돼 있다.'),
 c('curl --version','curl [옵션] URL 형식으로 요청을 보낸다. --version은 설치 버전을 보여 준다.','버전이 출력되는지 확인한다. 기존 검증은 curl 7.81.0을 사용했다.'),
 c('ip -br -4 address','ip는 네트워크 주소를 확인하는 명령이다. -br은 간략 표시, -4는 IPv4, address는 인터페이스 주소 조회이다.','ens33 등의 주소를 기록한다. lo의 127.0.0.1은 자기 자신이다.'),
 p('브라우저와 curl은 로그인 상태를 자동으로 공유하지 않는다. 아래 명령은 로그인 쿠키 없이 요청한다. 정상 조회는 로그인 페이지로 이동하는 302, 공격 입력은 WAF 차단에 따른 403을 관찰했다.'))
page('5.13  공격자 VM의 이름 설정',
 p('/etc/hosts는 Ubuntu의 이름·IP 연결 파일이다. Windows에서 한 설정과 별개이므로 공격자 VM에서도 확인한다.'),
 c("grep -n -F 'dvwa.' /etc/hosts",'-n은 줄 번호, -F는 작은따옴표 안의 문자를 그대로 검색한다.','기존 이름과 IP가 올바르면 편집을 건너뛴다. 바꿀 때는 기존 행을 메모한다.'),
 c('sudo nano /etc/hosts','sudo는 관리자 권한으로 실행하고 nano는 파일을 편집한다. 기존 이름이 있으면 그 행을 고치고, 없으면 아래 행을 추가한다.','Ctrl+O, Enter로 저장하고 Ctrl+X로 닫는다.'),
 code('192.168.0.189 dvwa.kt66.lab'),
 c('getent hosts dvwa.kt66.lab','getent hosts 이름은 시스템이 해석한 주소를 출력한다. 자신의 도메인으로 바꾼다.','kt66의 WEB_HOST_IP가 나와야 한다.'),
 c("DVWA='http://dvwa.kt66.lab'",'현재 셸에서 사용할 변수에 주소를 저장한다. 등호 양쪽을 붙이며 작은따옴표는 문자열을 묶는다.','화면 출력 없이 저장된다. 자신의 도메인으로 바꾼다.'),
 c('echo "$DVWA"','echo는 값을 출력한다. $DVWA는 변수의 값으로 바뀌고 큰따옴표는 이를 하나의 인자로 묶는다.','자신의 DVWA 주소가 나온다. 이후 요청도 이 터미널에서 실행한다.'))
page('5.13  시각 확인',
 p('NTP는 시간 서버를 기준으로 시스템 시계를 맞추는 방식이다. 요청과 Wazuh 기록의 시각을 대조하기 전에 확인한다.'),
 c('date -Is','date는 현재 시각을 출력한다. -I의 s는 ISO 8601 형식으로 초까지 표시한다는 뜻이다.','시각과 +09:00 같은 시간대 값을 적는다.'),
 c('date -Is','kt66의 현재 시각도 읽는다.','두 시각을 같은 시간대로 환산해 대조한다. +00:00과 +09:00은 9시간 차이이다.',H),
 c('timedatectl status','timedatectl은 시각과 동기화 상태를 관리한다. status는 현재 상태를 조회한다.','System clock synchronized: yes와 NTP service: active를 확인한다.'),
 c('sudo timedatectl set-ntp true','동기화가 꺼져 있을 때만 실행한다. set-ntp true는 NTP 동기화를 켜며 관리자 권한이 필요하다.','timedatectl status로 다시 확인한다. 계속 no이면 인터넷 연결과 시간 서버 설정을 확인한다.'))
page('5.13  curl의 기본 응답 확인',
 tab(['옵션·구문','동작'],[['-s · -S','진행 표시를 숨긴다 · 오류 메시지는 표시한다. -sS로 붙여 쓸 수 있다.'],['-i','응답 헤더와 본문을 함께 출력한다.'],['--max-time 15','전체 요청 시간을 15초로 제한한다.'],['"$DVWA/login.php"','변수의 주소 뒤에 로그인 경로를 붙인다. 큰따옴표로 하나의 인자로 전달한다.']],[43,84]),
 c('curl -sS -i --max-time 15 "$DVWA/login.php"','로그인 페이지를 요청한다. 옵션은 위 표와 같다.','첫 줄에 200 OK, 아래에는 헤더와 HTML 본문이 나온다.'),
 p('HTML은 웹 페이지 구조를 표현하는 문서 형식이다. curl은 응답 문자를 출력하며 HTML을 화면으로 그리거나 스크립트를 실행하지 않는다. 브라우저에서는 같은 내용을 화면과 Network로 읽었다.'),
 p('응답은 상태 줄·헤더·빈 줄·본문 순서이다. -i를 생략하면 기본 출력에는 본문만 나온다.'))
page('5.13  curl로 정상 값 보내기',
 tab(['옵션·기호','동작'],[['--get','뒤의 입력값을 URL 쿼리에 붙여 GET으로 보낸다.'],['--data-urlencode 이름=값','값에 URL 인코딩을 적용한다. 반복하면 여러 매개변수를 보낸다.'],["작은따옴표(')",'공백·기호를 포함한 입력을 한 인자로 묶는다.'],['줄 끝 역슬래시(\\)','다음 줄까지 한 명령으로 이어 준다.']],[54,73]),
 c(req('sqli',"--data-urlencode 'id=1'","--data-urlencode 'Submit=Submit'","--data-urlencode 'bookcase=book05-normal'"),'id와 Submit은 브라우저 폼이 전송한 값이다. bookcase는 로그에서 구분하기 위한 표식이다. -sS·-i·--max-time은 앞 페이지의 응답 표시·시간 제한 옵션이다.','로그인 쿠키가 없어 302 Found와 Location: login.php가 나왔다.'),
 p('curl은 이 명령에서 이동 안내를 자동으로 따라가지 않는다. 브라우저가 로그인된 상태에서 받은 200과 구분한다.'))
page('5.13  curl로 SQL 입력 보내기',
 c('PAYLOAD="1\' UNION SELECT user,password FROM users-- "','SQL 입력을 셸 변수에 저장한다. 큰따옴표 안의 작은따옴표는 입력 문자의 일부이며, -- 뒤 공백도 포함한다.','다음 명령에서 $PAYLOAD가 이 문자열로 바뀐다.'),
 c(req('sqli','--data-urlencode "id=$PAYLOAD"',"--data-urlencode 'Submit=Submit'","--data-urlencode 'bookcase=book05-sqli'"),'--data-urlencode가 SQL의 공백과 작은따옴표를 인코딩하고 --get이 URL에 붙인다. 큰따옴표는 변수 값 전체를 하나의 인자로 묶는다.','기존 검증에서는 403과 Wazuh 규칙 31103이 나왔다.'),
 p('브라우저와 같은 SQL 입력을 보냈다. Discover에서 data.url: *book05-sqli*로 찾고 같은 시각의 WAF 기록을 대조한다.'))
page('5.13  curl로 스크립트 보내기',
 c(req('xss_r',"--data-urlencode 'name=<script>alert(1)</script>'","--data-urlencode 'bookcase=book05-xss'"),'name은 브라우저의 이름 입력란에 대응한다. 작은따옴표는 꺾쇠·소괄호를 셸 문법으로 처리하지 않도록 묶는다. --data-urlencode는 값을 인코딩하고 --get은 URL 쿼리로 보낸다.','기존 검증에서는 403과 Wazuh 규칙 31105가 나왔다.'),
 p('curl 출력만으로 JavaScript 실행을 확인할 수는 없다. 이 요청에서는 응답과 WAF 차단을 확인한다. Discover에서 data.url: *book05-xss*로 찾는다.'))
page('5.13  curl로 인코딩한 경로 보내기',
 p('새 옵션 --data는 값을 URL 인코딩하지 않고 전달한다. 기본적으로 요청 본문에 넣지만 여기서는 --get과 함께 써서 쿼리에 붙인다. --data-urlencode와 구분한다.'),
 tab(['이번 명령의 입력','전송 형태'],[["--data-urlencode 'page=…'",'슬래시를 %2F로 바꾼 경로 값'],["--data 'bookcase=…'",'인코딩할 특수문자가 없는 표식']],[68,59]),
 c(req('fi',"--data-urlencode 'page=../../../../../etc/passwd'","--data 'bookcase=book05-path'"),'page는 읽을 파일 경로이다. ../는 상위 디렉터리이며 다섯 번 사용했다. 작은따옴표로 값을 묶고 역슬래시로 명령을 이어 쓴다. -sS·-i는 응답 표시, --max-time 15는 시간 제한이다.','기존 검증에서는 403과 Wazuh 규칙 31101이 나왔다. URL의 슬래시는 %2F로 기록됐다.'),
 p('본문의 브라우저 주소창에서 %2F를 입력한 경우와 같은 경로 값을 보낸다.'))
page('5.13  curl로 슬래시를 그대로 보내기',
 c(req('fi',"--data 'page=../../../../../etc/passwd'","--data 'bookcase=book05-path-raw'"),'page도 --data로 전달한다. --get과 함께 사용하므로 슬래시가 그대로 URL 쿼리에 들어간다. 공백이 없는 경로이며, raw 표식으로 앞 요청과 구분한다.','기존 검증에서는 403과 Wazuh 규칙 31104가 나왔다.'),
 p('Discover에서 data.url: *book05-path*로 두 요청을 찾는다. 5.8에서 비교한 ../와 ..%2F의 차이를 읽는다. WAF 차단은 해당 요청의 감사 기록에서 확인한다.'))
page('5.13  curl 실습 원상복구',
 p('공격자 VM에서 hosts를 변경했다면 수정 전 메모와 대조한다. 다음 실습에서도 사용할 이름은 유지한다.'),
 c("grep -n -F 'dvwa.' /etc/hosts",'변경한 행을 줄 번호와 함께 찾는다.','복구 대상이 이번 실습에서 바꾼 행인지 확인한다.'),
 c('sudo nano /etc/hosts','추가한 행을 제거하거나 수정 전 값으로 되돌린다.','Ctrl+O, Enter로 저장하고 Ctrl+X로 닫는다.'),
 c("grep -n -F 'dvwa.' /etc/hosts",'같은 조건으로 다시 읽는다.','추가한 행이 사라졌거나 기존 값으로 돌아왔는지 확인한다.'),
 c('unset DVWA PAYLOAD','unset은 현재 셸의 변수를 제거한다.','echo "$DVWA"를 실행하면 값 없이 빈 줄이 나온다.'),
 p('NTP 동기화는 유지한다. 요청으로 생긴 로그와 경보는 조사 자료로 보관한다.'))

page('5장 참고 자료',
 h('[1] DVWA와 실습 코드'),
 {'type':'link','text':'DVWA 공식 저장소','url':'https://github.com/digininja/DVWA'},
 {'type':'link','text':'DVWA · SQL injection · low.php','url':'https://github.com/digininja/DVWA/blob/master/vulnerabilities/sqli/source/low.php'},
 h('[2] kt66 WAF 구성과 CRS'),
 {'type':'link','text':'kt66 · web/Dockerfile · 63d4180','url':'https://github.com/mrgrit/kt66/blob/63d4180b1d6866de986ef263a3bd831d6082b5d5/web/Dockerfile'},
 {'type':'link','text':'OWASP CRS · Anomaly Scoring','url':'https://coreruleset.org/docs/2-how-crs-works/2-1-anomaly_scoring/'},
 h('[3] curl 요청·인코딩 옵션'),
 {'type':'link','text':'curl · Manual','url':'https://curl.se/docs/manpage.html'})
page('5장 참고 자료 · 계속',
 h('[4] Apache 로그 형식'),
 {'type':'link','text':'Apache 2.4 · mod_log_config','url':'https://httpd.apache.org/docs/2.4/mod/mod_log_config.html'},
 {'type':'link','text':'Apache 2.4 · mod_logio','url':'https://httpd.apache.org/docs/2.4/mod/mod_logio.html'},
 h('[5] SQL 인젝션'),
 {'type':'link','text':'OWASP · SQL Injection','url':'https://owasp.org/www-community/attacks/SQL_Injection'},
 {'type':'link','text':'MySQL · Comments','url':'https://dev.mysql.com/doc/refman/8.4/en/comments.html'},
 h('[6] Wazuh 웹 탐지 규칙'),
 {'type':'link','text':'Wazuh 4.10.0 · 0245-web_rules.xml','url':'https://github.com/wazuh/wazuh/blob/v4.10.0/ruleset/rules/0245-web_rules.xml'})
page('5장 참고 자료 · XSS와 파일 접근',
 h('[7] XSS'),
 {'type':'link','text':'OWASP · Cross Site Scripting','url':'https://owasp.org/www-community/attacks/xss/'},
 h('[8] 출력 위치에 맞는 처리'),
 {'type':'link','text':'OWASP · Cross Site Scripting Prevention Cheat Sheet','url':'https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html'},
 h('[9] 경로 조작'),
 {'type':'link','text':'OWASP · Path Traversal','url':'https://owasp.org/www-community/attacks/Path_Traversal'},
 h('[10] DQL'),
 {'type':'link','text':'OpenSearch 2.16 · Dashboards Query Language','url':'https://docs.opensearch.org/2.16/dashboards/dql/'})
page('5장 참고 자료 · 브라우저',
 h('[11] 브라우저의 Network 도구'),
 {'type':'link','text':'Chrome DevTools · Inspect network activity','url':'https://developer.chrome.com/docs/devtools/network/'},
 {'type':'link','text':'Chrome DevTools · Network features reference','url':'https://developer.chrome.com/docs/devtools/network/reference/'},
 {'type':'link','text':'Microsoft Edge · Inspect network activity','url':'https://learn.microsoft.com/en-us/microsoft-edge/devtools/network/'},
 h('[12] Windows hosts 파일'),
 {'type':'link','text':'Microsoft Support · Hosts 파일 위치와 편집','url':'https://support.microsoft.com/en-us/windows/experience/how-to-reset-the-hosts-file-back-to-the-default'})
browser_inputs.extend([
 {'file':'B05-06-path-raw-url.txt','text':'http://dvwa.kt66.lab/vulnerabilities/fi/?page=../../../../../etc/passwd&bookcase=book05-browser-path-raw'},
 {'file':'B05-08-path-encoded-url.txt','text':'http://dvwa.kt66.lab/vulnerabilities/fi/?page=..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd&bookcase=book05-browser-path'}])
# Figure captions follow the actual reading order.
number=0
for pg in pages:
 for block in pg['blocks']:
  if block.get('type')=='image' and block.get('caption','').startswith('화면 '):
   number+=1;block['caption']='화면 5-'+str(number)+'. '+block['caption'].split('. ',1)[1]
if __name__=='__main__':
 out=ROOT/'examples/chapter05';out.mkdir(parents=True,exist_ok=True)
 (ROOT/'manuscript/volume01-chapter05.json').write_text(json.dumps({'title':'웹 공격의 시작과 입력값 검증','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','pages':pages},ensure_ascii=False,indent=2)+'\n')
 for old in list(out.glob('C05-*.txt'))+list(out.glob('Q05-*.txt')):old.unlink()
 for item in browser_inputs:(out/item['file']).write_text(item['text'].replace('\n','')+'\n')
 (out/'browser-inputs.json').write_text(json.dumps(browser_inputs,ensure_ascii=False,indent=2)+'\n')
 for b in commands+queries:(out/(b['id']+'.txt')).write_text(b['text']+'\n')
 (out/'manifest.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n');(out/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2)+'\n')
 (out/'investigation.txt').write_text('실행 위치·시각·시간대:\n요청 URL·입력값·표식:\nHTTP 상태·관련 헤더·본문:\nagent.name·data.srcip:\nlocation·full_log:\n_index·_id:\nrule.id·data.id:\nWAF transaction_id:\nintercepted·CRS 규칙·차단 이유:\n확인한 사실:\n추가 확인할 사항:\nhosts 변경 내용·원상복구 결과:\n')
 print(len(pages),'pages',len(commands),'commands',len(queries),'queries')
