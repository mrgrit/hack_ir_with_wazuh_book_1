"""5장: HTTP 요청 한 건을 보내고 웹 로그·WAF·Wazuh 결과를 대조한다."""
import json
from pathlib import Path
from write_chapter01 import p,h,tab,img,code
ROOT=Path(__file__).resolve().parents[1]
pages=[];commands=[];queries=[]
A='공격자 VM · 터미널';H='kt66 VM · 호스트 터미널';W='kt66-web 컨테이너 안';S='kt66-siem 컨테이너 안'
def page(title,*blocks):pages.append({'title':title,'kind':'body','blocks':list(blocks)})
def c(text,why,result,where=A):
 b={'type':'command','id':f'C05-{len(commands)+1:02d}','text':text,'why':why,'result':result,'where':where};commands.append(b);return b
def q(text,why,result,index='wazuh-alerts-*'):
 b={'type':'query','id':f'Q05-{len(queries)+1:02d}','text':text,'why':why,'result':result,'where':'Windows · Discover · '+index};queries.append(b);return b
def sc(n,caption,width=127):return img('assets/screens/chapter05/'+n+'.png',caption,width)
def fig(n,caption):return img('assets/figures/chapter05/'+n+'.png',caption)
def spot(n,caption):return {'type':'image','path':'assets/illustrations/chapter05/'+n+'.png','caption':caption,'width_mm':55,'align':'right'}
def req(endpoint,*values):
 return 'curl -sS -i --max-time 15 --get \\\n  "$DVWA/vulnerabilities/'+endpoint+'/" \\\n  '+' \\\n  '.join(values)
page('5장  웹 공격의 시작과 입력값 검증',
 h('5.1  요청·응답·로그를 연결하기'),
 p('DVWA에 SQL 구문, 스크립트, 파일 경로를 보낸다. 응답을 읽고 같은 요청을 웹 로그와 Wazuh에서 찾는다. Module 01 실습 01~03에 해당한다.'),
 tab(['항목','준비·확인'],[['실행 위치','공격자 VM, kt66 VM, Windows 브라우저'],['선행 조건','1.12의 공격자 VM 준비, kt66 실행, web 에이전트 연결, 3~4장의 Discover 사용'],['대상','자신의 kt66에 설치된 DVWA'],['성공 기준','보낸 입력과 응답 코드, 원문, 탐지 규칙을 대조하고 차단 근거를 설명한다.'],['실패 시','5.10에서 이름 해석 → 접속 → 원본 로그 → 수집 → 검색 순서로 확인한다.'],['원상복구','5.11에서 추가한 hosts 항목과 셸 변수를 정리한다.']],[30,97]),
 p('DVWA(Damn Vulnerable Web Application)는 웹 취약점을 학습하도록 만든 애플리케이션이다. kt66이 컨테이너로 실행한다. 이 장에서는 그 앞의 WAF가 공격 입력을 검사하는 과정도 함께 확인한다. [1]'))
page('5.1  웹 요청과 로그 수집 경로',
 p('Apache는 HTTP 요청을 받아 응답하는 웹 서버이다. kt66의 Apache는 DVWA로 요청을 전달하는 프록시 역할도 한다. 접속 기록은 kt66-web에 남는다.'),
 p('WAF(Web Application Firewall)는 웹 요청과 응답을 검사하는 방화벽이다. kt66은 Apache에 ModSecurity를 설치하고 OWASP CRS의 공격 탐지 규칙을 적용한다. DVWA 앞에서는 차단 모드로 동작한다. [2]'),
 fig('request-log-path','도식 5-1. 웹 요청과 로그 수집 경로.'),
 p('fw와 ips는 1장에서 구성한 방화벽·침입방지 장비이다. 이 장에서는 그 뒤의 웹 요청과 Apache·ModSecurity 기록을 조사한다.'),
 p('ModSecurity는 요청을 처리하는 중에 차단 여부를 결정한다. Wazuh는 web 에이전트가 보낸 로그를 분석해 경보로 분류한다. 두 도구의 규칙 번호는 서로 다르다.'))
page('5.2  실습 주소와 도구 확인',
 p('1.12의 Ubuntu 22.04 Live Server 공격자 VM을 켠다. 두 VM의 네트워크는 Bridged로 연결한다. 먼저 kt66의 주소와 실습 도메인을 읽는다.'),
 c("grep -E '^(WEB_HOST_IP|LAB_DOMAIN)=' .env",'kt66 저장소 디렉터리에서 실행한다. -E는 확장 정규표현식, ^는 줄 시작이다. 괄호 안의 파이프(|)는 또는(OR)을 뜻한다. 두 설정의 이름 뒤에 등호가 있는 행을 찾는다.','WEB_HOST_IP와 LAB_DOMAIN 값을 기록한다. 예시는 192.168.0.189와 kt66.lab이다.','kt66 VM · ~/kt66'),
 c('ip -br -4 address','ip는 네트워크 주소와 경로를 확인하는 명령이다. -br은 간략 표시, -4는 IPv4, address는 인터페이스 주소 조회이다.','공격자 VM의 ens33 등 네트워크 인터페이스 주소를 적는다. lo의 127.0.0.1은 자기 자신을 가리킨다.'),
 c('curl --version','curl은 URL로 요청을 보내고 응답을 받는 명령줄 도구이다. 이 장에서는 HTTP 입력값을 직접 지정해 보내는 데 쓴다. --version은 설치 버전을 출력한다.','1.12에서 설치했다면 버전이 나온다. 검증 환경은 7.81.0이다. 명령이 없으면 1.12의 도구 설치를 완료한다.'),
 p('본문의 주소는 자신의 값으로 바꾼다. LAB_DOMAIN이 ccc.com이면 웹 이름은 dvwa.ccc.com이다. 검증 화면은 이 이름과 공격자 주소 192.168.0.202를 사용했다.'))
page('5.2  웹 이름을 IP에 연결하기',
 p('/etc/hosts는 호스트 이름과 IP를 연결하는 파일이다. 공격자 VM에서 dvwa.kt66.lab이 kt66의 웹 진입 IP로 해석되도록 한다.'),
 c("grep -n -F 'dvwa.' /etc/hosts",'기존 DVWA 항목을 찾는다. -n은 줄 번호, -F는 작은따옴표 안의 문자열을 그대로 검색한다.','출력이 있으면 이름과 IP를 먼저 확인한다. 올바르면 편집을 건너뛴다.'),
 c('sudo nano /etc/hosts','sudo는 관리자 권한으로 실행하고 nano는 파일을 편집한다. 아래처럼 자신의 IP와 웹 이름을 한 행에 적는다. 같은 이름의 기존 항목이 있으면 그 행을 고친다.','기존 값을 메모한다. Ctrl+O, Enter로 저장하고 Ctrl+X로 닫는다.'),
 code('192.168.0.189 dvwa.kt66.lab'),
 c('getent hosts dvwa.kt66.lab','getent hosts 이름은 시스템이 해석한 주소를 출력한다. 다른 도메인을 선택했다면 이름도 바꾼다.','기록한 WEB_HOST_IP가 나와야 한다. 다른 주소이면 hosts의 중복 항목부터 확인한다.'),
 p('새로 추가한 행과 수정 전 값을 적어 둔다. 실습 후 5.11에서 이 변경만 되돌린다.'))
page('5.2  이름·주소와 대상 변수',
 fig('name-and-host','도식 5-2. 접속 주소와 HTTP Host의 역할.'),
 p('IP는 접속할 장비를 정하고, HTTP의 Host 헤더는 그 장비에서 요청할 사이트 이름을 알린다. 같은 kt66 IP에도 DVWA와 다른 실습 사이트가 있으므로 웹 이름으로 접속한다.'),
 c("DVWA='http://dvwa.kt66.lab'",'DVWA는 이 터미널에서 사용할 셸 변수이다. 등호 양쪽을 붙여 쓰고 URL을 작은따옴표로 묶어 저장한다. 도메인이 다르면 여기서 바꾼다.','화면 출력 없이 저장된다. 이후 명령의 $DVWA가 이 주소로 바뀐다.'),
 c('echo "$DVWA"','echo는 값을 출력한다. 달러 기호($) 뒤의 변수 이름을 값으로 바꾸고, 큰따옴표는 그 값을 하나의 인자로 묶는다.','자신의 DVWA 주소가 나와야 한다. 이후 요청도 같은 터미널에서 실행한다.'),
 p('이 변수는 현재 셸에서 사용한다. 새 터미널에서는 다시 지정한다.'))
page('5.2  시각 확인',
 p('요청 시각과 경보 시각을 대조하려면 두 VM의 시계가 맞아야 한다. NTP는 네트워크의 시간 서버를 기준으로 시계를 맞추는 방식이다.'),
 c('date -Is','현재 시각을 ISO 8601 형식으로 출력한다. -I의 s는 초 단위까지 표시한다는 뜻이다.','공격자 VM의 시각과 +09:00 같은 시간대 값을 기록한다.'),
 c('date -Is','같은 시점에 kt66의 시각을 읽는다.','두 시각을 같은 시간대로 환산해 대조한다. UTC의 +00:00과 한국 표준시의 +09:00은 9시간 차이이다.',H),
 c('timedatectl status','timedatectl은 시스템 시각과 동기화 상태를 관리하는 명령이다. status는 현재 상태를 보여 준다.','System clock synchronized: yes와 NTP service: active를 확인한다.'),
 p('동기화가 꺼져 있을 때만 다음 명령을 실행한다.'),
 c('sudo timedatectl set-ntp true','set-ntp true는 시스템의 NTP 동기화를 켠다. 관리자 권한이 필요하다.','timedatectl status로 다시 확인한다. 계속 no이면 인터넷 연결과 시간 서버 설정을 점검한 뒤 진행한다.'),
 p('검증 환경의 공격자 VM은 이미 kt66 시간 서버와 동기화되어 있었다.'))
page('5.3  HTTP 요청과 응답',
 p('HTTP는 클라이언트가 요청을 보내고 서버가 응답하는 통신 규약이다. 브라우저와 curl이 클라이언트가 될 수 있다. 요청에는 대상 경로와 동작, 헤더, 필요한 경우 본문이 들어간다.'),
 code('GET /login.php HTTP/1.1\nHost: dvwa.kt66.lab'),
 tab(['부분','뜻'],[['GET','지정한 자원을 요청하는 메서드'],['/login.php','서버 안에서 요청할 경로'],['HTTP/1.1','사용하는 HTTP 버전'],['Host','요청할 웹 사이트 이름']],[33,94]),
 c('curl -sS -i --max-time 15 "$DVWA/login.php"','curl [옵션] URL 형식으로 요청한다. -s는 진행 표시를 숨기고 -S는 오류를 표시한다. -i는 응답 헤더와 본문을 함께 출력한다. --max-time 15는 전체 요청 시간을 15초로 제한한다.','첫 줄의 HTTP 상태 코드와 아래 HTML 본문을 읽는다. 정상 접속이면 로그인 페이지의 200 응답이 나온다.'),
 p('응답은 상태 줄, 헤더, 빈 줄, 본문 순서이다. HTML은 웹 페이지의 구조를 표현하는 문서 형식이다. curl은 그 내용을 터미널에 출력한다.'))
page('5.3  브라우저 화면과 상태 코드',
 p('Windows 브라우저에서는 kt66 시작 화면의 DVWA 링크를 연다. 터미널에서 받은 로그인 페이지를 브라우저는 입력란과 버튼으로 표시한다.'),
 sc('dvwa-login','화면 5-1. DVWA 로그인 페이지.',110),
 tab(['상태 코드','확인할 내용'],[['200 OK','요청이 처리되었다. 반환된 본문을 읽는다.'],['302 Found','다른 주소로 이동하도록 안내한다. Location 헤더에서 목적지를 확인한다.'],['403 Forbidden','서버가 요청을 거부했다. 차단 주체와 이유는 로그에서 확인한다.']],[38,89]),
 p('이 장의 공격 문자열은 DVWA에 로그인하기 전에도 WAF가 검사한다. 먼저 응답과 로그를 수집한 뒤, 입력값의 처리 원리와 탐지 근거를 대조한다.'))
page('5.3  URL에 입력값 넣기',
 p('URL의 물음표(?) 뒤에는 이름=값 형식의 쿼리 매개변수를 붙인다. 여러 매개변수는 앰퍼샌드(&)로 구분한다.'),
 code('/vulnerabilities/sqli/?id=1&Submit=Submit'),
 tab(['부분','역할'],[['/vulnerabilities/sqli/','DVWA의 SQL 인젝션 실습 경로'],['id=1','조회할 사용자 번호'],['Submit=Submit','DVWA가 조회 처리를 시작할 때 확인하는 값']],[52,75]),
 p('공백이나 꺾쇠처럼 URL에서 특별한 의미가 있는 문자는 퍼센트 인코딩으로 보낼 수 있다. 바이트 값을 %와 16진수 두 자리로 표현한다. [3]'),
 tab(['표기','해석'],[['%27','작은따옴표(\')'],['%20 또는 +','이 실습의 쿼리 값에서 공백'],['%3C · %3E','여는 꺾쇠(<) · 닫는 꺾쇠(>)'],['%2F · %2C','슬래시(/) · 쉼표(,)'],['%28 · %29','여는 소괄호 · 닫는 소괄호']],[43,84]),
 p('curl의 --get은 입력값을 URL의 쿼리에 붙여 GET으로 보낸다. --data-urlencode 이름=값은 값에 필요한 인코딩을 적용한다. 여러 번 쓰면 여러 매개변수를 보낸다.'))
page('5.4  정상 입력의 기준 기록',
 p('먼저 id=1을 보낸다. bookcase는 이 책의 요청을 로그에서 구분하려고 붙이는 표식이다. 뒤에서 공격 문자열만 바꾸어 응답과 로그를 비교한다.'),
 c(req('sqli',"--data-urlencode 'id=1'","--data-urlencode 'Submit=Submit'","--data-urlencode 'bookcase=book05-normal'"),'--get과 --data-urlencode로 세 매개변수를 보낸다. 작은따옴표는 각 이름=값을 하나의 인자로 묶는다. 줄 끝의 역슬래시(\\)는 다음 줄까지 한 명령으로 잇는다.','로그인 전에는 HTTP/1.1 302 Found와 Location: login.php를 확인한다.'),
 code('HTTP/1.1 302 Found\nLocation: login.php'),
 p('302는 로그인 화면으로 이동하라는 응답이다. 이번 요청에서 사용자 정보가 조회된 것은 아니다. 출력한 응답과 발생 시각을 기록한다.'),
 spot('request','삽화. 웹 요청 시험.'))
page('5.4  아카이브에서 기준 기록 찾기',
 p('Windows의 Discover에서 wazuh-archives-*와 Last 24 hours를 선택한다. 정상 입력은 경보가 없어도 아카이브에 수집될 수 있다.'),
 q('agent.name: "web" AND data.url: *book05-normal*','agent.name은 수집 에이전트이다. 별표(*)는 앞뒤의 임의 문자열에 일치한다. web이 보낸 URL 중 book05-normal을 포함한 기록을 찾는다.','행을 펼쳐 data.id의 302, data.srcip의 공격자 IP, data.url의 표식을 확인한다.','wazuh-archives-*'),
 sc('normal-data','화면 5-2. 정상 입력의 수집 기록.'),
 p('data.protocol은 이 웹 로그에서 HTTP 메서드인 GET을 담는다. data.id는 HTTP 응답 코드이다. rule.id는 Wazuh 탐지 규칙 번호이므로 구분한다.'),
 p('location은 /var/log/apache2/dvwa_access.log이다. 결과가 없으면 다음 페이지에서 원본 파일부터 확인한다.'))
page('5.4  Apache 원본 로그 확인',
 p('웹 로그는 kt66-web 컨테이너에 있다. access 로그는 접속과 응답, error 로그는 처리 오류와 ModSecurity 메시지를 기록한다. modsec_audit.log는 WAF가 검사한 요청의 상세 기록이다.'),
 c('docker exec -it kt66-web /bin/bash','kt66 호스트에서 웹 컨테이너의 Bash로 들어간다. -i는 입력 유지, -t는 터미널 할당이다.','이후 두 명령은 kt66-web 안에서 실행한다.',H),
 c('cd /var/log/apache2','cd는 작업 디렉터리를 옮긴다. Apache 로그 디렉터리로 이동한다.','이제 파일명으로 로그를 조회할 수 있다.',W),
 c("grep -F 'book05-normal' dvwa_access.log",'grep은 조건에 맞는 행을 찾는다. -F는 표식을 정규표현식으로 해석하지 않고 그대로 찾는다.','공격자 IP와 GET 요청, 302 응답이 있는 한 행을 찾는다.',W),
 c('exit','웹 컨테이너의 셸을 끝낸다.','kt66 호스트 터미널로 돌아온다.',W),
 p('파일에 기록이 없으면 DVWA 이름이 올바른 사이트로 연결되는지 확인한다. 파일에는 있으나 Discover에 없으면 web 에이전트 연결과 수집 설정을 확인한다.'))
page('5.4  접속 로그 한 행 읽기',
 p('아래는 기준 요청의 원문이다. 원본 파일에는 한 행으로 저장된다. [4]'),
 code('192.168.0.202 - -\n[01/Nov/2026:20:13:48 +0900]\n"GET /vulnerabilities/sqli/?id=1&Submit=Submit&\nbookcase=book05-normal HTTP/1.1"\n302 429 "-" "curl/7.81.0"'),
 tab(['부분','뜻·Wazuh 필드'],[['192.168.0.202','접속 출발지 · data.srcip'],['첫 두 개의 -','원격 사용자 식별값과 인증 사용자명이 기록되지 않았다.'],['대괄호의 시각','Apache가 기록한 시각·시간대'],['GET','HTTP 메서드 · data.protocol'],['경로와 쿼리','요청 대상과 입력값 · data.url'],['HTTP/1.1','HTTP 버전'],['302','응답 코드 · data.id'],['429','이 환경의 로그 형식에서 헤더를 포함한 송신 바이트 수'],['"-" · "curl/7.81.0"','Referer 없음 · 클라이언트가 보낸 User-Agent']],[38,89]),
 p('Referer는 이전 페이지 주소를 알리는 헤더이고, User-Agent는 클라이언트가 자기 정보를 적는 헤더이다. 원문 전체는 full_log, 수집 파일은 location에 들어간다.'))
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
 code("1' UNION SELECT user,password FROM users-- "),
 tab(['부분','의도'],[["1'",'번호 뒤의 작은따옴표로 기존 문자열 값을 끝낸다.'],['UNION','기존 조회 결과에 다른 SELECT의 결과를 결합한다.'],['SELECT user,password','계정명과 저장된 암호값 열을 선택한다.'],['FROM users','그 값을 users 테이블에서 읽으려 한다.'],['-- 뒤의 공백','MySQL에서 뒤에 붙을 나머지 SQL을 주석으로 처리한다.']],[49,78]),
 p('앞 조회는 두 열을 반환한다. 두 번째 SELECT도 user와 password라는 두 열을 지정한다. 실제 동작 여부는 DB 구문, 열의 형식, 애플리케이션 처리와 접근 권한에 달려 있다.'),
 c('PAYLOAD="1\' UNION SELECT user,password FROM users-- "','긴 입력값을 셸 변수 PAYLOAD에 저장한다. 큰따옴표 안의 작은따옴표는 문자열의 일부이다. -- 뒤의 공백도 값에 포함한다.','다음 요청의 "id=$PAYLOAD"에서 변수 값이 id에 들어간다.'),
 p('이 실습에서는 먼저 WAF가 이 입력을 어떻게 처리하는지 확인한다.'))
page('5.5  SQL 인젝션 · 요청과 응답',
 c(req('sqli','--data-urlencode "id=$PAYLOAD"',"--data-urlencode 'Submit=Submit'","--data-urlencode 'bookcase=book05-sqli'"),'기준 요청의 id를 SQL 구문으로 바꾸어 보낸다. --data-urlencode가 작은따옴표와 공백 등을 URL에 넣을 수 있는 형태로 바꾼다.','차단 모드의 검증 환경에서는 403 Forbidden과 거부 안내 본문이 나왔다.'),
 code('HTTP/1.1 403 Forbidden'),
 p('응답 코드와 시각을 적는다. 다음 검색은 문자열을 보냈다는 사실과 탐지 결과를 대조하는 단계이다.'),
 q('agent.name: "web" AND data.url: *book05-sqli*','Discover에서 wazuh-alerts-*와 Last 24 hours를 선택한다. SQL 시험의 표식으로 찾는다.','행을 펼쳐 원문에 UNION·SELECT가 있는지 읽는다. rule.id, data.id, data.srcip을 기록한다.'),
 p('현재 환경에서 200이나 302가 나오면 응답 본문과 로그를 확인한다. 설정·탐지 조건이 다른 원인을 찾기 전에는 공격 성공으로 판단하지 않는다.'))
page('5.5  SQL 인젝션 · 경보 해석',
 sc('sqli-data','화면 5-3. SQL 입력과 응답 코드.'),
 sc('sqli-rule','화면 5-4. SQL 인젝션 탐지 설명.'),
 tab(['확인 항목','이 사례의 해석'],[['data.url','%27은 작은따옴표, +는 공백, %2C는 쉼표로 읽는다. UNION SELECT 구문을 찾는다.'],['data.id: 403','웹 서버가 요청을 거부했다.'],['data.srcip','공격자 VM 192.168.0.202이다.'],['rule.id: 31103','Wazuh가 SQL 인젝션 시도로 분류했다.'],['rule.description','SQL injection attempt. · SQL 인젝션 시도'],['rule.firedtimes','해당 규칙에 일치한 누적 횟수이다.']],[45,82]),
 p('화면의 URL에서 &amp;는 매개변수를 구분하는 &의 HTML 표기이다. full_log의 원문과 대조한다.'),
 p('Wazuh의 기본 규칙 31103은 URL의 SQL 공격 관련 문자열을 찾는다. 데이터베이스가 그 SQL을 실행했는지는 이 접속 로그로 확인되지 않는다. [6]'))
page('5.6  WAF 차단 근거 찾기',
 p('403만으로 차단 주체를 확정할 수는 없다. 같은 요청의 ModSecurity 감사 기록을 찾아 WAF가 차단했는지 확인한다.'),
 q('agent.name: "web"\nAND location: "/var/log/apache2/modsec_audit.log"\nAND full_log: "book05-sqli"','Discover의 패턴을 wazuh-archives-*로 바꾼다. location은 감사 로그 파일, full_log의 큰따옴표는 표식의 구문 검색이다. AND로 세 조건을 모두 만족하는 기록을 찾는다.','한 행을 펼쳐 data.request.request_line의 표식, transaction의 출발지와 시각을 앞의 접속 로그와 대조한다.','wazuh-archives-*'),
 sc('waf-action','화면 5-5. ModSecurity의 차단 결정.'),
 tab(['필드','뜻'],[['action.intercepted: true','WAF가 해당 요청의 처리를 차단했다.'],['action.phase: 2','요청 본문 검사 단계이다. URL 매개변수도 이 단계의 규칙으로 검사할 수 있다.'],['action.message','차단 평가의 비교 조건이다. anomaly_score가 기준 이상인지 검사했다.']],[57,70]),
 p('화면의 전체 필드 이름은 data.audit_data.action으로 시작한다. action은 처리 결정, intercepted는 가로막았는지를 나타낸다.'))
page('5.6  감사 기록의 응답과 규칙',
 sc('waf-response','화면 5-6. 감사 기록의 응답과 접속 정보.'),
 tab(['필드','확인할 내용'],[['data.response.status','응답 코드 403'],['transaction.remote_address','공격자 IP 192.168.0.202'],['transaction.local_address','요청을 받은 web 주소 10.20.32.80'],['transaction.local_port','web이 요청을 받은 HTTP 포트 80'],['transaction.remote_port','공격자 연결에 임시 배정된 출발지 포트'],['transaction.time','원본 처리 시각과 시간대'],['transaction.transaction_id','WAF가 요청을 구별하는 식별자']],[61,66]),
 p('transaction으로 시작한 항목은 data.transaction 아래에 있다. 시각·출발지·요청 URL이 같은지 대조한다.'))
page('5.6  WAF 규칙과 차단 이유',
 p('감사 기록의 JSON 탭을 연다. data.audit_data.messages에는 일치한 CRS 규칙과 차단 이유가 들어 있다. 다음 번호와 문구를 찾는다.'),
 code('942100 · SQL Injection Attack Detected\n949110 · Access denied with code 403'),
 p('CRS는 탐지 규칙이 부여한 점수를 합산하고 차단 기준과 비교한다. 이 요청은 점수 20이 기준 5 이상이어서 949110이 차단했다. 942100은 WAF 규칙, 31103은 Wazuh 규칙이다. [2]'),
 p('시각·출발지·요청 URL이 같은지 대조한 뒤 “SQL 인젝션 입력을 WAF가 차단했다”로 기록한다.'))
page('5.7  XSS · 입력이 실행되는 위치',
 p('DVWA의 반사형 XSS 실습은 name에 받은 값을 응답 HTML에 넣는다. XSS(Cross-Site Scripting)는 입력한 스크립트가 웹 페이지의 코드로 해석되어 브라우저에서 실행되는 취약점이다. [7]'),
 code('<script>alert(1)</script>'),
 tab(['부분','뜻'],[['<script> · </script>','HTML에서 스크립트 영역의 시작과 끝을 표시한다.'],['alert(1)','JavaScript의 알림 창에 숫자 1을 표시한다. 소괄호 안은 함수에 전달하는 값이다.']],[48,79]),
 fig('xss-context','도식 5-4. 반사형 XSS의 실행 과정.'),
 p('반사형은 요청의 입력값이 곧바로 응답에 포함되는 방식이다. curl은 응답 문자를 출력하므로 스크립트 실행 여부는 브라우저에서 확인해야 한다. 이 장의 사례는 WAF가 해당 요청을 차단한 경우이다.'),
 p('SQL 인젝션은 데이터베이스의 SQL 해석을, XSS는 브라우저의 HTML·스크립트 해석을 노린다.'))
page('5.7  XSS · 요청과 경보',
 c(req('xss_r',"--data-urlencode 'name=<script>alert(1)</script>'","--data-urlencode 'bookcase=book05-xss'"),'name 값으로 스크립트를 보낸다. 작은따옴표가 꺾쇠와 소괄호를 셸에서 해석하지 않도록 묶고, --data-urlencode가 URL용으로 인코딩한다.','검증 환경에서는 403 Forbidden이 나왔다. 응답과 시각을 기록한다.'),
 q('agent.name: "web" AND data.url: *book05-xss*','패턴을 wazuh-alerts-*로 바꾸고 XSS 요청 표식을 찾는다.','data.url과 403 응답을 확인한다. 검증 환경의 rule.id는 31105이다.'),
 sc('xss-data','화면 5-7. 스크립트 입력의 수집 기록.'),
 p('URL의 %3Cscript%3E는 <script>이다. %28과 %29는 소괄호, %2F는 닫는 태그의 슬래시이다. 복원한 값이 보낸 페이로드와 같은지 읽는다.'))
page('5.7  XSS · 판정과 대응',
 p('31105의 설명은 XSS (Cross Site Scripting) attempt.이다. 이 규칙은 URL의 script 관련 문자열 등을 검사한다. 브라우저에서 코드가 실행됐다는 뜻은 아니다. [6]'),
 tab(['관찰','판정·다음 확인'],[['요청 URL에 스크립트가 있다','XSS 입력을 전송했다.'],['403과 WAF intercepted: true','같은 요청을 WAF가 차단했다.'],['응답이 200이다','응답 HTML에서 입력이 어떻게 들어갔는지 확인한다.'],['브라우저에서 시험 코드가 실행된다','그 페이지에서의 XSS 실행 근거가 된다.']],[57,70]),
 p('5.6의 감사 로그 검색에서 표식을 book05-xss로 바꾼다. request_line과 response.status, action.intercepted를 확인한다.'),
 p('애플리케이션은 입력값을 HTML의 문자로 표시하도록 출력 위치에 맞게 처리해야 한다. 예를 들어 HTML 본문에서 <를 &lt;로 출력하면 태그 시작으로 해석되지 않는다. HTML 속성·JavaScript·URL은 각각 다른 처리가 필요하다. [8]'),
 spot('review','삽화. 응답과 탐지 기록 대조.'))
page('5.8  경로 조작과 파일 포함',
 p('DVWA의 파일 포함 실습은 page 값으로 읽을 파일을 고른다. 디렉터리 트래버설은 ../ 같은 경로 표현으로 허용한 디렉터리 밖의 파일에 접근하려는 공격이다. [9]'),
 p('LFI(Local File Inclusion)는 웹 애플리케이션이 입력값에 따라 서버 내부 파일을 포함하는 취약점이다. 이 실습에서는 파일 포함 기능에 상위 경로를 넣는다.'),
 code('../../../../../etc/passwd'),
 tab(['부분','뜻'],[['../','현재 디렉터리의 상위 디렉터리로 이동한다.'],['다섯 번의 ../','예시 시작 경로에서 루트 디렉터리까지 올라간다.'],['/etc/passwd','리눅스 계정 이름·UID·홈·로그인 셸 등이 있는 파일이다. 암호 해시 파일은 /etc/shadow이다.']],[43,84]),
 fig('path-context','도식 5-5. 입력 경로를 그대로 사용한 파일 접근.'),
 p('시작 디렉터리와 파일 접근 권한에 따라 결과가 달라진다. 경로 문자열이 로그에 있다는 사실과 파일 내용이 응답에 나왔다는 사실을 구분한다.'))
page('5.8  인코딩한 경로 요청',
 c(req('fi',"--data-urlencode 'page=../../../../../etc/passwd'","--data 'bookcase=book05-path'"),'page 값을 URL 인코딩해 보낸다. --data는 값을 별도로 인코딩하지 않고 전달한다. --get과 함께 사용하므로 본문 대신 쿼리에 붙는다. 여기서는 단순한 표식에 사용한다.','403 응답을 기록한다. URL의 슬래시는 %2F로 바뀐다.'),
 q('agent.name: "web" AND data.url: *book05-path*','인코딩한 요청과 다음 페이지의 비교 요청을 함께 찾는 조건이다. 처음에는 한 요청만 나온다.','현재 요청의 rule.id와 data.id를 기록한다. 검증 환경에서는 31101과 403이었다.'),
 p('31101의 설명은 Web server 400 error code.이다. 이 이름은 400번대 응답을 분류한 것이다. 경로 조작 전용 이름이 나오지 않아도 보낸 URL과 WAF 기록을 확인한다.'),
 p('감사 로그의 book05-path 기록에는 CRS 930100의 Path Traversal Attack 문구와 intercepted: true가 있었다. WAF의 검사와 Wazuh의 접속 로그 분류는 서로 다른 규칙으로 수행된다.'))
page('5.8  경로 표기만 바꾸어 비교',
 c(req('fi',"--data 'page=../../../../../etc/passwd'","--data 'bookcase=book05-path-raw'"),'앞 요청과 같은 경로를 --data로 보낸다. 이 값에는 공백이 없어 슬래시를 그대로 쿼리에 넣을 수 있다. 표식 뒤의 raw로 두 요청을 구분한다.','검증 환경에서는 이번에도 403이었고 Wazuh 규칙은 31104였다.'),
 p('앞 검색식을 유지하고 Refresh를 누른다. 두 기록의 data.url에서 ../와 ..%2F를 비교한다.'),
 tab(['보낸 형태','Wazuh 결과'],[['슬래시를 %2F로 인코딩','31101 · 400번대 응답 분류'],['슬래시를 그대로 전달','31104 · Common web attack.']],[64,63]),
 sc('path-data','화면 5-8. 경로 조작 요청의 수집 기록.'),
 p('기본 규칙 31104에는 ../.. 등의 문자열 조건이 있다. 두 입력은 경로 해석 시 같은 뜻이어도 URL에 남은 형태는 다르다. rule.id 하나로만 검색하면 관련 요청을 놓칠 수 있다. [6]'))
page('5.8  파일이 읽혔는지 판단하기',
 p('이 실습의 두 요청은 WAF에서 차단되었다. 파일 내용이 반환된 기록은 없다. 다음과 같이 근거를 나누어 적는다.'),
 tab(['대상','확인 근거'],[['접근 시도','page 값에 상위 경로와 etc/passwd가 있다.'],['WAF 차단','같은 요청의 intercepted: true와 응답 403'],['파일 노출','응답 본문에 대상 파일의 내용이 있는지 확인해야 한다.'],['후속 조사','같은 출발지가 다른 파일과 경로도 요청했는지 찾는다.']],[38,89]),
 p('애플리케이션은 page에 실제 파일 경로를 직접 받기보다 home, help처럼 허용한 이름을 받고 서버에서 고정된 파일에 대응시키는 방식으로 바꾼다. 경로를 받을 필요가 있으면 정규화한 최종 경로가 허용 디렉터리 안에 있는지 검사한다.'),
 p('LFI에는 상위 경로 외에 PHP의 파일 처리 기능을 이용하는 변형도 있다. 문자열 필터 한두 개로 모든 파일 접근을 막을 수 있다고 가정하지 않는다. 이 장의 재현 대상은 앞의 경로 조작 두 요청이다.'))
page('5.9  탐지 조건을 넓혀 찾기',
 p('bookcase는 실습에서 붙인 표식이다. 실제 조사에서는 요청 경로·출발지·공격 문자열·탐지 규칙을 조합한다. 아래 조건은 이 장에서 확인한 경로 조작을 찾는 예이다.'),
 q('agent.name: "web" AND\n(rule.id: "31104" OR data.url: *etc*passwd*)','OR는 양쪽 조건 중 하나를 만족하면 선택한다. 소괄호는 그 범위를 묶는다. *etc*passwd*는 etc와 passwd 사이의 / 또는 %2F도 포함하도록 찾는다.','경로 조작 규칙에 일치한 요청과 파일명 문자열이 들어간 요청을 함께 읽는다. 이 장 밖의 기록도 나올 수 있다.'),
 p('자신의 공격자 IP와 실습 시간을 추가해 범위를 좁힌다. data.srcip의 값은 자신의 주소로 바꾼다.'),
 q('agent.name: "web" AND data.srcip: "192.168.0.202"\nAND (rule.id: "31104" OR data.url: *etc*passwd*)','AND로 출발지 조건을 추가한다. 기간은 실습 시작·종료 시각으로 지정한다.','같은 출발지의 요청을 URL과 응답 코드로 묶어 읽는다.'),
 p('공격 문자열 검색은 조사 후보를 찾는 방법이다. 정상 입력과 비슷한 문자열도 함께 나올 수 있으므로 원문과 응답, 애플리케이션의 기능을 확인한다. [10]'))
page('5.9  세 종류의 근거 대조',
 fig('evidence','도식 5-6. 응답·차단 결정·로그 분류의 대조.'),
 tab(['관찰한 값','해석'],[['HTTP 403','클라이언트가 거부 응답을 받았다.'],['WAF intercepted: true','WAF가 요청 처리를 차단했다.'],['rule.id 31103·31105·31104','접속 로그가 SQL·XSS·일반 웹 공격 조건에 일치했다.'],['rule.id 31106','공격 관련 URL이 200 응답을 받았다. 침투 성공 여부는 본문과 서버 동작으로 확인한다.']],[57,70]),
 p('31106의 설명에는 success가 들어 있지만 조건은 공격 관련 상위 규칙과 응답 코드 200이다. DB 자료 노출·브라우저 실행·파일 반환을 직접 확인하는 규칙은 아니다. [6]'),
 p('입력값 검증은 예상한 형식·범위·허용값만 받아들이는 작업이다. SQL은 문장을 고정하고 값을 별도로 전달하는 매개변수 바인딩을 적용한다. XSS에는 출력 위치에 맞는 처리, 파일 기능에는 접근 범위 제한을 적용한다.'))
page('5.10  결과가 다를 때',
 tab(['증상','확인 순서'],[['Could not resolve host','DVWA 변수의 이름 → getent hosts 결과 → /etc/hosts의 이름·IP'],['Connection refused 또는 시간 초과','kt66 기동 → 두 VM의 브리지·주소 → 웹 진입 IP와 80번 포트'],['로그인 페이지 대신 다른 사이트','LAB_DOMAIN → DVWA 변수 → hosts 항목과 Host 이름'],['공격 응답이 200 또는 302','응답 본문 → 요청 입력값 → 올바른 사이트인지 → WAF의 적용 설정'],['Apache 원문이 없다','이름·접속 경로 → kt66-web의 dvwa_access.log → 요청 시각·표식'],['원문은 있으나 검색 결과가 없다','인덱스·기간 → DQL·필터 → web 에이전트 상태 → localfile 설정'],['예상한 공격 규칙이 없다','인코딩된 URL → data.id → 다른 rule.id → WAF 감사 로그']],[48,79]),
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
 p('웹 이름을 추가하거나 고쳤다면 5.2에서 적어 둔 변경 내용을 확인한다. 이후 장에서도 같은 이름을 쓸 때는 유지하고, 이 장에서 추가한 설정을 제거하려면 아래 절차를 따른다.'),
 c("grep -n -F 'dvwa.' /etc/hosts",'복구할 행을 먼저 찾는다.','새로 추가한 행 또는 수정한 행이 메모와 같은지 대조한다.'),
 c('sudo nano /etc/hosts','이 장에서 추가한 행을 지우거나 수정 전 값으로 되돌린다.','Ctrl+O, Enter로 저장하고 Ctrl+X로 닫는다. 다른 호스트 항목은 유지한다.'),
 c("grep -n -F 'dvwa.' /etc/hosts",'편집 후 같은 조건으로 다시 확인한다.','추가한 행이 사라졌거나 기존 값으로 돌아왔는지 확인한다.'),
 c('unset DVWA PAYLOAD','unset은 현재 셸의 변수를 제거하는 명령이다.','echo "$DVWA"를 실행하면 값 없이 빈 줄이 나온다.'),
 p('NTP를 켰다면 실습 후에도 동기화를 유지한다. Discover의 검색식·필터를 비우고 wazuh-alerts-*, Last 24 hours로 되돌린다. 요청으로 생긴 접속 로그와 경보는 조사 자료로 보관한다.'))
page('5.12  조사 결과 정리',
 tab(['표식','관찰 결과'],[['book05-normal','302 · 로그인 페이지로 이동 안내'],['book05-sqli','403 · Wazuh 31103 · WAF 차단'],['book05-xss','403 · Wazuh 31105 · WAF 차단'],['book05-path','403 · Wazuh 31101 · 인코딩한 경로'],['book05-path-raw','403 · Wazuh 31104 · 슬래시를 그대로 보낸 경로']],[55,72]),
 p('표는 검증 환경에서 확인한 결과이다. 자신의 요청마다 아래 항목을 기록한다.'),
 tab(['항목','기록할 내용'],[['요청','실행 위치·시각·URL·입력값'],['응답','HTTP 상태·Location·관련 본문'],['접속 로그','출발지·원문 시각·location·full_log'],['Wazuh','인덱스·문서 ID·rule.id·data.id'],['WAF','transaction_id·intercepted·규칙과 차단 이유'],['판단','입력 시도·차단·실행 여부와 각각의 근거']],[30,97]),
 p('양식은 examples/chapter05/investigation.txt이다. 다음 장에서는 웹 경로 탐색과 인증 요청을 여러 번 보냈을 때의 기록을 조사한다.'))
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
if __name__=='__main__':
 out=ROOT/'examples/chapter05';out.mkdir(parents=True,exist_ok=True)
 (ROOT/'manuscript/volume01-chapter05.json').write_text(json.dumps({'title':'웹 공격의 시작과 입력값 검증','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','pages':pages},ensure_ascii=False,indent=2)+'\n')
 for b in commands+queries:(out/(b['id']+'.txt')).write_text(b['text']+'\n')
 (out/'manifest.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n');(out/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2)+'\n')
 (out/'investigation.txt').write_text('실행 위치·시각·시간대:\n요청 URL·입력값·표식:\nHTTP 상태·관련 헤더·본문:\nagent.name·data.srcip:\nlocation·full_log:\n_index·_id:\nrule.id·data.id:\nWAF transaction_id:\nintercepted·CRS 규칙·차단 이유:\n확인한 사실:\n추가 확인할 사항:\nhosts 변경 내용·원상복구 결과:\n')
 print(len(pages),'pages',len(commands),'commands',len(queries),'queries')
