"""6장: 웹 탐색과 인증 공격. 실제 요청·응답·로그를 대조하는 수동 실습."""
from illustration_assets import resolve_path
import json
from pathlib import Path
from write_chapter01 import p,h,tab,img,code
ROOT=Path(__file__).resolve().parents[1];pages=[];commands=[];queries=[];browser_inputs=[]
A='공격자 VM · 터미널';H='kt66 VM · 호스트 터미널';W='kt66-web 컨테이너 안';S='kt66-siem 컨테이너 안'
def page(title,*blocks):pages.append({'title':title,'kind':'body','blocks':list(blocks)})
def c(text,why,result,where=A):
 b={'type':'command','id':f'C06-{len(commands)+1:02d}','text':text,'why':why,'result':result,'where':where};commands.append(b);return b
def q(text,why,result,index='wazuh-alerts-*'):
 b={'type':'query','id':f'Q06-{len(queries)+1:02d}','text':text,'why':why,'result':result,'where':'Windows · Discover · '+index};queries.append(b);return b
def sc(n,caption,width=127):return img('assets/screens/chapter06/'+n+'.png','화면 6-0. '+caption,width)
def fig(n,caption):return img('assets/figures/chapter06/'+n+'.png',caption)
def spot(n,caption):return {'type':'image','path':resolve_path('06','assets/illustrations/chapter06/'+n+'.png'),'caption':'삽화. '+caption,'width_mm':55,'align':'right'}
def bi(name,text,display=None):
 browser_inputs.append({'file':name+'.txt','text':text});return code(display or text)
def ref(text,url):return {'type':'link','text':text,'url':url}
page('6장  웹 탐색과 인증 공격',
 p('여러 경로를 요청하고 암호를 바꾸어 입력한다. 요청 헤더·HTTP 메서드·URL 길이도 바꾸어 응답과 Wazuh 기록을 대조한다. Module 01 실습 04~06, 13~15에 해당한다.'),
 tab(['항목','준비·확인'],[['실행 위치','Windows 브라우저. 목록 탐색과 선택 curl 실습은 공격자 VM.'],['선행 조건','5장의 DVWA 접속·DB 준비, web 에이전트 연결, 아카이브 수집.'],['대상','자신의 kt66에 설치한 DVWA.'],['성공 기준','입력·응답·원본 로그·Wazuh 필드를 연결하고 판단 근거를 적는다.'],['문제 해결','6.9에서 주소 → 응답 → 원본 로그 → 수집 → 검색 순서로 확인한다.'],['원상복구','6.9에서 User-Agent·학습 단계를 복구하고 만든 목록 파일을 정리한다.']],[29,98]),
 fig('roadmap','도식 6-1. 실습 순서.'))
page('6.1  접속과 준비 상태 확인',
 p('Windows에서 Chrome 또는 Edge를 열고 5장에서 등록한 DVWA 이름으로 접속한다. 본문의 kt66.lab은 자신의 LAB_DOMAIN으로 바꾼다. 촬영 환경의 도메인은 ccc.com이다.'),
 bi('B06-01-login','http://dvwa.kt66.lab/login.php'),
 p('① admin / password로 로그인한다. 기존 환경에서 암호를 바꿨으면 그 값을 쓴다.'),
 sc('login-input','DVWA 계정 입력.',105),
 p('② Database Setup이 나타나면 처음 사용하는 DB이다. 5.2의 Create / Reset Database → Setup successful! 확인 → 재로그인 절차를 수행한다. 기존 DB를 초기화하면 사용자와 방명록 자료가 지워진다.'),
 p('③ DVWA Security를 열어 현재 단계를 메모한다. Low를 선택하고 Submit을 누른다.'),
 sc('security','DVWA의 Low 단계.'),
 p('④ Home으로 돌아온다. Brute Force와 DVWA Security 메뉴가 보이면 준비됐다.'))
page('6.1  브라우저와 Discover 준비',
 p('① DVWA 탭에서 Ctrl+Shift+I를 누른다. Network를 선택하고 Preserve log 또는 Keep log를 켠다. 목록을 지우는 Clear 버튼과 요청 이름을 눌러 여는 Headers 위치를 확인한다. [1]'),
 p('② 다른 탭에서 https://kt66-IP:5601에 접속한다. Wazuh 데모 계정은 admin / SecretPassword이다. Discover를 열고 실습 시각이 포함된 기간을 지정한다.'),
 tab(['기록','선택할 인덱스'],[['404·403 등 경보로 분류된 요청','wazuh-alerts-*'],['정상 요청·인증 요청·WAF 감사 기록','wazuh-archives-*']],[70,57]),
 p('③ Network의 Request URL·Request Method·Status Code를 적는다. Discover에서는 같은 시각의 data.url·data.protocol·data.id와 대조한다.'),
 tab(['필드','읽는 법'],[['agent.name','로그를 보낸 에이전트. 이 실습은 web.'],['data.srcip','Apache가 기록한 접속 출발지.'],['data.protocol','웹 access 로그에서는 GET·POST 같은 메서드.'],['data.id','웹 access 로그에서는 HTTP 응답 코드.'],['rule.id','Wazuh가 적용한 규칙 번호.'],['location · full_log','수집 파일 경로 · 원문 한 행.']],[39,88]),
 p('네트워크 주소 변환(NAT)이 있으면 data.srcip이 PC 주소와 다를 수 있다. 자신의 요청 한 건을 찾은 뒤 그 출발지 값을 이후 검색에 쓴다.'))
page('6.2  경로를 하나씩 요청하기',
 p('웹 경로 탐색은 파일·디렉터리 이름을 바꾸어 요청하고 응답 차이를 조사하는 작업이다. 먼저 브라우저에서 존재하는 페이지와 없는 경로를 비교한다.'),
 fig('path-scan','도식 6-2. 경로 탐색과 반복 요청의 기록.'),
 p('① DVWA 탭의 주소창에 다음 주소를 입력한다. 로그인 폼과 Network의 200을 확인한다.'),
 bi('B06-02-known','http://dvwa.kt66.lab/login.php?book06=known'),
 p('② 주소를 다음과 같이 바꾼다. book06-missing은 이번 실습에서 없는 경로로 사용할 이름이다.'),
 bi('B06-03-missing','http://dvwa.kt66.lab/book06-missing'),
 p('③ Network에서 book06-missing 문서 요청을 누른다. 응답과 본문을 함께 읽는다. 같은 경로가 이미 있는 환경이면 다른 이름으로 바꾸고 이후 검색식도 맞춘다.'))
page('6.2  없는 경로의 응답과 경보',
 sc('path-missing','없는 경로의 404 응답.'),
 q('agent.name: "web"\nAND data.url: "/book06-missing"','wazuh-alerts-*에서 실습 기간으로 좁힌다. AND는 두 조건을 모두 만족하는 기록을 찾는다.','행을 펼쳐 data.id가 404, data.protocol이 GET인지 확인한다.'),
 sc('path-data','없는 경로의 수집 기록.'),
 p('검증 환경에서는 404와 규칙 31101이 나왔다. 이 규칙은 4xx 응답을 분류한다. 잘못 입력한 주소와 끊어진 링크도 같은 기록을 만들 수 있다.'),
 p('여러 경로를 짧은 간격으로 요청했는지 조사하려면 같은 출발지의 앞뒤 기록을 함께 읽는다. 6.8에서 같은 URL을 Apache 원본 파일에서도 찾는다.'))
page('6.2  목록 탐색 도구 준비',
 p('Gobuster는 단어 목록의 각 행을 URL 경로에 붙여 요청하는 도구이다. 브라우저로 확인한 요청을 여러 후보에 반복한다. 설치와 실행은 Ubuntu 22.04 공격자 VM에서 한다. [2]'),
 p('1.12의 도구 설치를 마쳤으면 설치 상태부터 확인한다.'),
 c('gobuster -h','기본 구문은 gobuster 옵션이다. -h는 사용법을 표시한다. 이 장은 Ubuntu 22.04 패키지의 Gobuster 2.0.1을 기준으로 한다.','-m, -u, -w, -t, -a 옵션이 보이는지 확인한다. 명령을 찾지 못하면 아래 설치 절차를 수행한다.'),
 c('sudo apt update','apt는 Ubuntu 패키지 관리자이다. update는 설치 가능한 패키지 목록을 갱신한다. sudo는 관리자 권한으로 실행한다.','저장소 접속 오류가 없는지 확인한다. Gobuster가 설치돼 있으면 이 명령과 다음 설치 명령을 건너뛴다.'),
 c('sudo apt install gobuster','install 뒤에 지정한 패키지를 설치한다. 설치할 목록을 확인하고 계속할지 묻는 질문에 답한다.','완료 후 gobuster -h를 다시 실행해 사용법이 나오는지 확인한다.'),
 p('Gobuster 3 계열은 dir 하위 명령을 사용한다. 버전이 다르면 이 장의 2.0.1 구문을 그대로 적용하지 말고 설치 버전의 도움말을 확인한다.'),
 c('getent hosts dvwa.kt66.lab','getent는 시스템의 이름 조회 설정으로 주소를 찾는다. hosts 뒤에 DVWA 이름을 지정한다. kt66.lab은 자신의 도메인으로 바꾼다.','kt66 웹 진입 IP가 나와야 한다. 결과가 없거나 IP가 다르면 1.12의 공격자 VM hosts 설정을 확인한다.'))
page('6.2  탐색할 경로 목록 만들기',
 p('공격자 VM에서 이번 실습용 파일을 만든다. 아래 파일이 이미 있으면 내용을 확인하고 다른 파일명을 정한다.'),
 c('cd ~','cd는 작업 디렉터리를 옮긴다. 물결표(~)는 현재 사용자의 홈 디렉터리이다.','이후 목록 파일은 공격자 계정의 홈 디렉터리에 둔다.'),
 c('ls -l book06-paths.txt','ls는 파일 정보를 표시하고 -l은 권한·크기 등을 함께 표시한다. 변경 전 대상 파일의 존재 여부를 확인한다.','No such file or directory이면 새 파일로 만들 수 있다. 있으면 cat으로 내용을 먼저 읽는다.'),
 c('nano book06-paths.txt','nano는 터미널 텍스트 편집기이다. 뒤에 지정한 파일을 연다. 다음 페이지의 경로 목록을 한 행씩 입력한다.','Ctrl+O → Enter로 저장하고 Ctrl+X로 닫는다.'),
 c('cat book06-paths.txt','cat은 파일 내용을 출력한다. 저장 후 실제 내용을 확인한다.','다음 페이지의 23행과 비교한다. URL 전체가 아니라 경로만 들어 있어야 한다.'),
 p('파일이 이미 있었다면 덮어쓰지 말고 새 이름으로 작업한다. 이후 -w 옵션에도 그 파일명을 쓴다.'))
page('6.2  경로 목록',
 p('처음 세 행은 알려진 페이지와 관리 경로이다. 나머지 20행은 없는 경로를 요청하기 위한 실습 이름이다. 복사용 목록은 examples/chapter06/paths.txt에 있다.'),
 code((ROOT/'examples/chapter06/paths.txt').read_text().rstrip()),
 p('각 행을 별도의 경로로 요청한다. book06-scan-01은 http://dvwa.kt66.lab/book06-scan-01이 된다.'))
page('6.2  목록을 사용해 탐색하기',
 p('공격자 VM에서 다음 명령을 한 번 실행한다. -t 1로 동시에 처리할 요청을 하나로 제한한다.'),
 tab(['옵션','뜻'],[['-m dir','디렉터리·파일 경로 탐색 모드.'],['-u URL','대상 사이트의 기본 주소.'],['-w 파일','후보 경로를 읽을 단어 목록.'],['-t 1','동시에 작업할 스레드 수를 1로 지정.'],['-a book06-scan','요청의 User-Agent를 실습 표식으로 지정.']],[49,78]),
 c('gobuster -m dir \\\n  -u http://dvwa.kt66.lab/ \\\n  -w book06-paths.txt -t 1 -a book06-scan','줄 끝의 역슬래시(\\)는 다음 줄까지 한 명령으로 잇는다. 각 경로를 확인하고 응답 코드를 출력한다.','검증 환경에서는 /login.php와 /robots.txt가 200으로 표시됐다. 종료 후 Discover에서 같은 시각의 요청을 찾는다.'),
 code('/login.php (Status: 200)\n/robots.txt (Status: 200)'),
 p('기본 출력 대상은 200·204·301·302·307·403이다. 화면에서 빠진 404 요청도 웹 서버 로그에는 남는다. 시작할 때 무작위 경로로 없는 페이지의 응답을 확인하는 요청도 보낸다.'),
 p('예상 밖의 사이트가 열리면 Ctrl+C로 중단하고 도메인·IP를 확인한다. 파일 정리는 6.9에서 수행한다.'))
page('6.2  반복 요청 검색',
 q('agent.name: "web"\nAND full_log: "book06-scan"','full_log는 원문이다. 명령에서 지정한 User-Agent 표식이 있는 기록을 찾는다.','data.srcip이 공격자 VM 주소인지 확인하고 data.url과 data.id를 비교한다.'),
 sc('scan-data','경로 목록에서 발생한 404 기록.'),
 q('agent.name: "web" AND rule.id: "31151"\nAND full_log: "book06-scan"','같은 표식의 기록 중 반복된 4xx 응답 경보를 찾는다. rule.id는 HTTP 응답 코드와 다르다.','검증 환경에서 규칙 31151 한 건이 나왔다. 요청 목록 전체는 앞의 검색으로 확인한다.'),
 sc('scan-rule','반복된 4xx 응답 경보.'),
 p('오류 경로 여러 개와 짧은 시간 간격은 경로 탐색의 근거이다. 자동 점검 도구나 잘못된 링크도 원인이 될 수 있으므로 점검 일정·요청 경로·출발지를 대조한다.'))
page('6.2  반복 경보의 조건 확인',
 p('규칙 31151은 같은 출발지의 31101 해당 기록을 시간 범위 안에서 비교한다. Manager 컨테이너에서 실제 정의를 읽는다. [3]'),
 c('docker exec -it kt66-siem /bin/bash','docker exec는 실행 중인 컨테이너에서 명령을 시작한다. -i는 입력 유지, -t는 터미널 할당, /bin/bash는 대화형 셸이다.','이후 조회는 kt66-siem 안에서 수행한다.',H),
 c('cd /var/ossec/ruleset/rules','Wazuh 기본 규칙 디렉터리로 이동한다.','다음 명령에서 웹 규칙 파일을 조회한다.',S),
 c("sed -n '/<rule id=\"31151\"/,/<\/rule>/p' \\\n  0245-web_rules.xml",'sed는 텍스트의 행을 선택·변환하는 도구이다. -n은 기본 출력을 끄고 p는 선택한 행을 출력한다. 쉼표 앞·뒤의 /패턴/은 시작·끝 행을 지정한다. 끝 패턴의 \\/는 슬래시(/) 문자이다. 작은따옴표는 식을 셸 해석 없이 전달한다.','id 31151의 시작 태그부터 닫는 rule 태그까지 나온다.',S),
 c('exit','컨테이너의 셸을 끝낸다.','kt66 호스트 터미널로 돌아온다.',S),
 tab(['정의','뜻'],[['frequency="14" · timeframe="90"','반복 횟수 설정 14, 비교 시간 90초.'],['if_matched_sid 31101','이전에 해당한 4xx 규칙을 비교.'],['same_source_ip','출발지 IP가 같은 기록을 비교.']],[65,62]),
 p('직전 90초의 다른 4xx 요청도 계산에 들어간다. 목록의 몇 번째 행에서 경보가 생기는지는 앞선 요청에 따라 달라진다. rule.firedtimes는 이 규칙의 발생 횟수이며 경로 요청 수가 아니다.'))
page('6.3  User-Agent 바꾸기',
 p('접속 로그 끝에는 브라우저·도구가 보낸 User-Agent 문자열이 기록된다. 이는 클라이언트가 자신의 종류를 알리는 HTTP 헤더이다. 요청자가 값을 바꿀 수 있다.'),
 fig('user-agent','도식 6-3. User-Agent 검사와 로그 검색.'),
 p('이번에는 Chrome의 문자열을 sqlmap 이름으로 바꾼다. sqlmap은 SQL 인젝션을 시험하는 도구이며 여기서는 그 이름을 헤더 값으로만 사용한다.'),
 p('① DVWA 탭에서 개발자 도구의 Network를 연다. 상단의 More network conditions 버튼을 누른다. 메뉴로 열려면 개발자 도구의 ⋮ → More tools → Network conditions를 선택한다. [4]'),
 p('② User agent에서 Use browser default를 해제한다. Custom 입력란에 다음 값을 넣는다.'),
 bi('B06-04-user-agent','sqlmap/1.0 book06-ua'),
 sc('ua-settings','사용자 지정 User-Agent.'),
 p('선행 조건은 DVWA 접속이다. 전송 후 원문에 지정한 문자열이 남으면 헤더 변경을 확인한 것이다. 끝나면 Use browser default를 다시 켠다.'))
page('6.3  헤더 변경 요청 보내기',
 p('① 개발자 도구를 열어 둔 채 DVWA 주소창에 다음 주소를 입력한다.'),
 bi('B06-05-ua-url','http://dvwa.kt66.lab/book06-ua'),
 sc('ua-response','User-Agent 변경 요청의 거부 응답.'),
 p('② Network에서 이 요청을 누른다. Headers의 Request Headers에서 User-Agent가 sqlmap/1.0 book06-ua인지 확인한다. Status Code는 검증 환경에서 403이었다.'),
 p('③ Network conditions의 Use browser default를 다시 켠다. 다음 실습은 원래 브라우저 문자열로 진행한다.'),
 q('agent.name: "web" AND data.url: "/book06-ua"\nAND full_log: "sqlmap"','URL과 원문의 sqlmap 문자열을 함께 찾는다. access 로그의 data.url이 있는 기록으로 한정한다.','full_log 끝의 User-Agent와 data.id의 403을 확인한다.'),
 sc('ua-data','헤더 변경 요청의 접속 기록.'),
 p('이 기록으로 확인한 사실은 sqlmap이라는 문자열을 보냈다는 것이다. 실제 실행 도구를 판단하려면 요청 패턴이나 단말의 프로세스 기록이 더 필요하다.'))
page('6.3  WAF의 차단 이유 읽기',
 q('agent.name: "web"\nAND location: "/var/log/apache2/modsec_audit.log"\nAND data.request.request_line: *book06-ua*','wazuh-archives-*에서 WAF 감사 파일과 요청 경로로 찾는다. 별표(*)는 임의 문자열에 일치한다.','행을 펼쳐 요청 줄·응답·차단 결정·메시지를 대조한다.','wazuh-archives-*'),
 sc('ua-waf-request-line','WAF가 검사한 요청.'),
 sc('ua-waf-status','WAF의 응답 코드.'),
 sc('ua-waf-action','WAF의 차단 결정.'),
 p('data.audit_data.messages에서 913100과 949110을 찾는다. 913100은 User-Agent에서 sqlmap을 탐지한 CRS 규칙이다. 949110은 탐지 점수 합계가 기준에 도달해 차단한 규칙이다. [5]'),
 p('intercepted의 true는 WAF가 요청을 차단했다는 뜻이다. phase 2는 요청 본문을 처리하는 검사 단계이다. 헤더에서 탐지한 점수도 이 단계의 차단 평가에 반영된다.'),
 p('이 번호들은 ModSecurity의 CRS 규칙이다. Wazuh의 접속 로그 규칙 31101과 구분한다. 원본 감사 파일도 kt66-web의 /var/log/apache2/modsec_audit.log에 있다.'))
page('6.4  인증 결과를 구분하기',
 p('암호 추측 공격은 후보 암호를 반복 제출해 인증이 통과하는 값을 찾는 공격이다. 모든 조합을 시도하는 방법과 사전 목록을 쓰는 방법이 있다. 여기서는 학습 계정에 세 후보를 한 번씩 입력한다. [6]'),
 fig('login-flow','도식 6-4. DVWA 로그인 응답의 분기.'),
 p('DVWA의 일반 로그인과 Brute Force 메뉴를 비교한다. 전자는 실습 사이트에 로그인하는 화면이고 후자는 로그인한 사용자가 암호 추측을 연습하는 기능이다.'),
 tab(['순서','Username','Password'],[['1','admin','book06-wrong1'],['2','admin','book06-wrong2'],['3','admin','password']],[20,39,68]),
 p('기존 학습 계정의 암호를 바꿨으면 세 번째에 그 값을 쓴다. 성공 기준은 각 후보의 응답 코드와 인증 결과를 구분하는 것이다. 실습 뒤에는 Logout을 누른다.'))
page('6.4  일반 로그인 · 실패 확인',
 p('① DVWA의 Logout을 눌러 로그인 화면으로 이동한다. Network의 Keep log를 켜고 Clear로 목록을 비운다.'),
 p('② admin / book06-wrong1을 입력하고 Login을 누른다. Login failed 문구를 확인한다.'),
 sc('login-failed','일반 로그인 실패.',105),
 p('③ Network에서 처음 전송한 login.php 행을 누른다. Headers에서 POST·302를 확인한다. Response Headers의 Location은 login.php이다.'),
 sc('login-failed-headers','실패한 로그인 요청의 302 응답.'),
 p('302 뒤에 따라온 GET login.php는 로그인 화면을 다시 받은 요청이다. POST 행과 구분한다.'))
page('6.4  일반 로그인 · 성공 확인',
 p('① 두 번째 후보 book06-wrong2로 Login을 누른다. 실패 문구와 이동 주소를 확인한다.'),
 p('② 세 번째 후보 password로 Login을 누른다. Home과 실습 메뉴가 나타나는지 확인한다.'),
 sc('login-success','일반 로그인 성공 후 Home.'),
 p('③ 성공한 POST login.php의 Headers를 읽는다. 역시 302이며, Response Headers의 Location은 index.php이다.'),
 sc('login-success-headers','성공한 로그인 요청의 302 응답.'),
 tab(['구분','실패','성공'],[['POST 응답','302','302'],['Location','login.php','index.php'],['도착 화면','Login failed','Home·실습 메뉴']],[33,47,47]),
 p('HTTP 상태는 이동 동작을 나타낸다. 인증 결과는 Location과 도착 화면을 함께 확인한다.'))
page('6.4  일반 로그인 기록 찾기',
 q('agent.name: "web" AND data.protocol: "POST"\nAND data.url: "/login.php"','아카이브에서 로그인 폼을 제출한 요청을 찾는다. 조회 기간을 세 후보를 입력한 시각으로 좁힌다.','세 POST 요청의 출발지·시각·302 응답을 비교한다.','wazuh-archives-*'),
 sc('login-data','일반 로그인 요청의 접속 기록.'),
 p('이 Apache access 형식에는 POST 본문의 사용자명·암호, 응답의 Location, 인증 성공·실패 문구가 없다. 같은 출발지의 요청이 반복됐다는 사실까지 확인할 수 있다.'),
 p('운영 서비스의 인증 공격을 조사할 때는 애플리케이션이 남긴 계정·성공 여부·시각을 함께 수집한다. 계정별 실패 횟수, 성공으로 바뀐 시점, 성공 뒤의 권한 사용을 조사한다.'),
 p('DVWA의 login.php는 폼의 user_token도 확인한다. user_token은 세션 값과 폼 값을 대조하는 CSRF(사이트 간 요청 위조) 방지 토큰이다. 폼을 다시 표시할 때 갱신된다. 화면의 Login 버튼이 그 값을 함께 보낸다. [7]'),
 p('처리 코드는 kt66-dvwa의 /var/www/html/login.php에 있다. 입력 처리와 결과 분기를 확인하는 명령은 6.8에 모았다.'))
page('6.4  Brute Force 메뉴에 입력하기',
 p('① 로그인 상태에서 DVWA Security의 Low를 확인한다. 왼쪽 Brute Force를 누른다.'),
 p('② Username에 admin, Password에 book06-wrong1을 입력한다. Network의 목록을 비우고 Login을 누른다.'),
 sc('brute-input','Brute Force 메뉴의 계정 입력.'),
 sc('brute-failed','틀린 암호의 결과.'),
 p('Username and/or password incorrect.는 사용자명 또는 암호가 맞지 않는다는 뜻이다. Network에서 해당 요청의 응답 코드는 200이다.'),
 p('403이 나오면 WAF 기록에서 입력값의 차단 이유를 확인한다. 로그인 화면으로 이동했다면 세션이 끝난 것이므로 일반 로그인부터 다시 한다.'))
page('6.4  후보를 바꾸어 결과 비교',
 p('① Password만 book06-wrong2로 바꾸고 Login을 누른다. 실패 문구가 같은지 확인한다.'),
 p('② Password를 password로 바꾸고 Login을 누른다. Welcome to the password protected area admin 문구가 나오면 학습용 인증을 통과한 것이다.'),
 sc('brute-success','올바른 암호의 결과.'),
 sc('brute-success-headers','학습용 인증 요청의 GET·200 응답.'),
 p('일반 로그인과 달리 이 Low 실습은 GET 쿼리에 username과 password를 넣는다. 틀린 암호와 맞는 암호 모두 200이므로 본문의 결과 문구를 읽어야 한다.'),
 p('주소창·브라우저 기록·접속 로그에 암호가 남는다. 이 기능에는 실습용 암호만 입력한다.'))
page('6.4  인증 시도의 URL 읽기',
 q('agent.name: "web"\nAND data.url: *vulnerabilities/brute/*\nAND data.url: *username=admin*','아카이브에서 Brute Force 경로와 admin 입력을 함께 찾는다.','세 후보의 URL과 200 응답을 대조한다. 인증 결과 문구는 브라우저에서 적은 기록과 비교한다.','wazuh-archives-*'),
 sc('brute-data','Brute Force 요청의 쿼리 값.'),
 tab(['URL 부분','뜻'],[['username=admin','시험한 계정.'],['password=…','이번 요청에 넣은 후보 암호.'],['Login=Login','Login 버튼을 눌러 제출한 값.'],['& 또는 &amp;','매개변수 구분자. 화면의 &amp;는 &의 HTML 표기이다.']],[55,72]),
 p('세 건의 결과로 요청과 인증 결과의 차이를 확인했다. 대량 공격을 판단할 때는 같은 계정·출발지의 반복 횟수와 시간 간격을 추가로 조사한다.'),
 spot('log-review','인증 요청 기록 대조.'))
page('6.5  HTTP 메서드 확인',
 p('HTTP 메서드는 자원에 요청하는 동작을 나타낸다. 주소창으로 이동하면 보통 GET이 전송된다. 이번에는 메서드를 PROPFIND로 지정해 서버 정책과 비교한다. [8]'),
 p('WebDAV는 HTTP를 확장해 원격 파일과 속성을 관리하는 규약이다.'),
 tab(['메서드','동작'],[['GET · HEAD','자원의 표현을 요청한다 · 본문을 제외한 응답 정보를 요청한다.'],['POST','자료를 제출해 처리를 요청한다.'],['PUT · DELETE','자원 생성·대체를 요청한다 · 자원 삭제를 요청한다.'],['PROPFIND','WebDAV에서 자원 속성 조회를 요청한다.'],['TRACE','서버가 받은 요청을 돌려주는 진단 동작을 요청한다.']],[39,88]),
 fig('method','도식 6-5. 메서드와 허용 정책 비교.'),
 p('프로그램이 HTTP로 서비스 기능을 호출하는 웹 API에서는 PUT·DELETE를 쓸 수 있다. PROPFIND는 WebDAV 서비스에서 정상적으로 쓰인다. 서비스가 제공하는 기능과 허용 메서드를 기준으로 판단한다.'),
 p('선행 조건은 DVWA 접속이다. 한 요청의 메서드·응답·WAF 메시지를 연결하면 완료이다. 이 실습은 속성 조회 요청만 보내므로 파일 복구 작업은 없다.'))
page('6.5  브라우저에서 메서드 지정',
 p('DVWA에는 PROPFIND 전송 버튼이 없다. 브라우저 개발자 도구의 Console에서 요청 한 건을 보낸다. Console은 현재 페이지에서 JavaScript를 실행하고 결과를 확인하는 도구이다. [9]'),
 p('① DVWA의 login.php를 연다. Network의 Keep log를 켜고 목록을 비운다. Console 탭을 누른다.'),
 p('② 다음 식을 입력하고 Enter를 누른다. 줄을 바꿔 입력할 때는 Shift+Enter를 쓴다.'),
 bi('B06-06-method',"fetch('/book06-method', {method: 'PROPFIND'})\n  .then(r => console.log(r.status));"),
 tab(['구문','뜻'],[['fetch(주소, 설정)','HTTP 요청을 보낸다. /로 시작한 주소는 현재 사이트의 경로이다.'],["{method: 'PROPFIND'}",'중괄호 안에 요청 설정을 둔다. method의 값으로 메서드를 지정한다.'],['.then(…)','응답이 도착하면 괄호 안 동작을 수행한다.'],['r => console.log(r.status)','r은 받은 응답이다. 화살표(=>) 뒤에서 응답의 상태 코드를 Console에 출력한다.'],["'문자열' · ;",'작은따옴표는 문자열을 감싼다. 세미콜론은 문장을 끝낸다.']],[63,64]),
 p('fetch는 브라우저에 내장돼 있어 설치할 필요가 없다. 붙여넣기가 제한된 새 개발자 도구에서는 이 짧은 식을 직접 입력한다.'))
page('6.5  메서드 요청의 결과',
 sc('method-console','PROPFIND 요청과 403 응답.'),
 p('Promise {<pending>}는 요청의 응답을 기다리는 동안 표시될 수 있는 상태이다. 뒤에 출력된 403이 받은 응답 코드이다. Network로 돌아가 book06-method 행의 Headers를 연다.'),
 sc('method-headers','PROPFIND 요청의 Headers.'),
 q('agent.name: "web" AND data.protocol: "PROPFIND"\nAND data.url: "/book06-method"','wazuh-alerts-*에서 메서드와 경로를 함께 지정한다.','data.protocol의 PROPFIND와 data.id의 403을 확인한다.'),
 sc('method-data','PROPFIND 접속 기록.'),
 p('405는 해당 자원에서 메서드를 허용하지 않는 응답, 501은 서버가 그 기능을 구현하지 않았다는 응답이다. 이 환경의 403은 다음 감사 기록과 연결해 원인을 확인한다.'))
page('6.5  허용 메서드 정책과 대조',
 q('agent.name: "web"\nAND location: "/var/log/apache2/modsec_audit.log"\nAND data.request.request_line: *book06-method*','아카이브에서 같은 메서드 시험의 WAF 감사 기록을 찾는다.','메시지의 911100과 intercepted 값을 확인한다.','wazuh-archives-*'),
 sc('method-waf-request-line','WAF의 PROPFIND 요청 기록.'),
 sc('method-waf-status','WAF의 응답 코드.'),
 sc('method-waf-action','메서드 정책에 따른 차단.'),
 p('data.audit_data.messages의 CRS 규칙 911100은 허용 메서드 정책과 요청을 비교한다. 검증 환경에서는 PROPFIND가 허용 목록에 없어 탐지됐고, 규칙 949110의 점수 평가에서 차단됐다. [5]'),
 p('규칙 파일은 kt66-web의 다음 위치에 있다.'),
 code('/usr/share/modsecurity-crs/rules/\nREQUEST-911-METHOD-ENFORCEMENT.conf'),
 p('서비스에서 WebDAV가 필요한지, 해당 경로에서 허용하는 메서드는 무엇인지 확인한 뒤 정책을 정한다. 파일 생성 여부를 조사할 때는 응답 본문과 저장 위치·파일 변경 기록까지 확인한다.'))
page('6.6  관리 경로 요청',
 p('관리 페이지는 설정 변경이나 사용자 관리를 제공하는 화면이다. /admin/ 같은 이름을 요청해 페이지 존재 여부와 접근 제한을 조사한다. 일반 DVWA 접속이 가능하면 시작할 수 있다.'),
 p('① Network의 Keep log를 켠다. 다음 주소를 하나씩 주소창에 입력하고, 각 요청의 응답 코드와 본문을 적는다.'),
 bi('B06-07-admin','http://dvwa.kt66.lab/admin/'),
 bi('B06-08-phpmyadmin','http://dvwa.kt66.lab/phpmyadmin/'),
 bi('B06-09-wp-admin','http://dvwa.kt66.lab/wp-admin/'),
 bi('B06-10-manager','http://dvwa.kt66.lab/manager/html'),
 sc('admin','관리 경로 후보의 404 응답.'),
 p('검증 환경에서는 네 경로가 모두 404였다. 요청한 이름과 실제 응답을 기록하면 된다. 200이면 본문이 관리 화면인지, 로그인 화면인지, 공통 오류 페이지인지 구분한다.'),
 p('이 네 요청은 페이지 조회이다. 확인 후 DVWA의 login.php로 돌아간다.'))
page('6.6  관리 경로의 출발지 조사',
 q('agent.name: "web"\nAND data.url: ("/admin/" OR "/phpmyadmin/"\nOR "/wp-admin/" OR "/manager/html")','괄호는 경로 조건을 묶고 OR는 어느 하나에 일치하는 기록을 찾는다.','네 경로의 data.srcip·data.id를 확인한다. 경보가 없으면 같은 식으로 아카이브를 검색한다.'),
 sc('admin-data','관리 경로 후보의 접속 기록.'),
 p('② 행을 펼쳐 location이 dvwa_access.log인지 확인한다. 같은 이름의 경로라도 다른 사이트의 기록일 수 있다.'),
 p('③ 해당 출발지가 관리 접속을 허용한 장비인지 확인한다. 이 실습에서는 Windows 브라우저 또는 공격자 VM의 요청이다. NAT가 있으면 변환된 주소를 대조한다.'),
 tab(['관찰','추가 확인'],[['404','해당 사이트에서 요청 경로를 찾지 못했다. 서비스 목록과 경로를 대조한다.'],['403','접근 제어 또는 WAF 기록에서 거부 이유를 확인한다.'],['200','본문과 인증 상태를 읽고 관리 기능이 실제 제공되는지 확인한다.']],[26,101]),
 p('사설 IP라는 이유로 허용 장비로 분류하지 않는다. 네트워크 구간·접근 정책·실제 출발지를 확인한다.'))
page('6.7  긴 URL과 로그 길이',
 p('요청 URL이 길면 서버의 요청 크기 제한이나 긴 입력을 찾는 규칙에 걸릴 수 있다. 이번에는 문자 A 8,000개를 쿼리 값으로 보낸다. 반복 실행은 하지 않는다.'),
 fig('length','도식 6-6. HTTP 요청 줄과 접속 로그의 길이.'),
 p('Apache의 LimitRequestLine은 HTTP 요청 줄의 크기를 제한하며 기본값은 8,190바이트이다. Wazuh 규칙 31115의 maxsize는 수집한 로그 이벤트 크기를 비교한다. 두 값의 측정 대상이 다르다. [3][10]'),
 p('① DVWA에 로그인한 상태에서 login.php를 연다. Network의 목록을 비우고 Console을 선택한다.'),
 bi('B06-11-long',"location.href = '/?book06-long=' + 'A'.repeat(8000);"),
 tab(['구문','뜻'],[['location.href = …','현재 탭이 이동할 주소를 지정한다.'],["'/?book06-long='",'루트 경로의 쿼리 이름을 지정한다.'],["'A'.repeat(8000)",'A를 8,000번 반복한 문자열을 만든다.'],['+','두 문자열을 연결한다.']],[60,67]),
 p('② Enter를 누른 뒤 Network에서 book06-long 문서 요청의 상태를 읽는다. 검증 환경에서는 200이었다. 이 실습의 성공 기준은 긴 요청과 경보의 연결이다.'))
page('6.7  길이 경보 읽기',
 sc('long-network','긴 URL 요청의 Network 기록.'),
 q('agent.name: "web" AND rule.id: "31115"\nAND data.url: *book06-long*','경보 인덱스에서 긴 URL 실습 표식과 규칙 번호로 찾는다.','rule.id와 data.id를 구분하고 full_log의 요청 줄을 확인한다.'),
 sc('long-data','긴 요청의 200 응답 기록.'),
 sc('long-rule','긴 로그 이벤트의 경보.'),
 p('검증 기록의 요청 대상은 8,014바이트, GET·HTTP 버전을 포함한 요청 줄은 8,027바이트였다. 접속 로그 원문은 줄바꿈을 제외하고 8,228바이트였다. 영문 ASCII 문자로 시험한 값이다.'),
 p('로그인하지 않았다면 긴 요청 뒤에 302로 login.php로 이동할 수 있다. 긴 URL을 보낸 첫 요청과 뒤의 로그인 페이지 GET을 구분한다.'),
 p('31115의 maxsize="7900"은 로그 이벤트 크기 조건이다. 긴 URL이 로그를 늘려 이 조건에 해당했다. 모든 사이트의 URL 허용 길이가 7,900바이트라는 뜻으로 해석하지 않는다.'),
 p('반복 문자가 많다는 사실만으로 실행된 공격을 확정할 수는 없다. 요청 기능, 입력값, 오류 응답과 자원 사용량을 함께 조사한다. 확인 후 login.php로 돌아간다.'))
page('6.8  원본 access 로그 확인',
 p('Discover에서 찾은 요청을 서버 파일과 대조한다. kt66-web의 dvwa_access.log는 DVWA 접속을 기록한다. 사용자명·암호가 URL에 있으면 그대로 남을 수 있다.'),
 c('docker exec -it kt66-web /bin/bash','kt66 호스트에서 웹 컨테이너의 Bash로 접속한다. -it는 대화형 입력과 터미널을 유지한다.','다음 조회는 kt66-web 안에서 실행한다.',H),
 c('cd /var/log/apache2','Apache 로그 디렉터리로 이동한다.','dvwa_access.log를 파일명으로 조회할 수 있다.',W),
 c("grep -F 'book06-scan' dvwa_access.log",'grep은 조건에 맞는 행을 찾는다. -F는 작은따옴표 안의 문자열을 정규표현식이 아닌 문자 그대로 찾는다.','경로와 끝의 User-Agent를 읽고 출발지·시각·404 응답을 확인한다.',W),
 code('192.168.0.202 - - [01/Nov/2026:21:32:00 +0900]\n"GET /book06-scan-01 HTTP/1.1"\n404 451 "-" "book06-scan"'),
 p('원문의 첫 IP는 data.srcip, GET은 data.protocol, 경로는 data.url, 404는 data.id에 대응한다. 뒤의 숫자는 이 환경에서 헤더를 포함한 송신 바이트 수이다. 끝의 두 따옴표 값은 Referer와 User-Agent이다.'),
 c('exit','웹 컨테이너의 셸을 끝낸다.','kt66 호스트 터미널로 돌아온다.',W))
page('6.8  로그인 처리 코드의 위치',
 p('일반 로그인은 /var/www/html/login.php, Brute Force의 Low 처리는 /var/www/html/vulnerabilities/brute/source/low.php에 있다. 필요한 행만 찾아 입력 방식과 결과 분기를 확인한다.'),
 c('docker exec -it kt66-dvwa /bin/bash','DVWA 애플리케이션 컨테이너의 Bash로 들어간다.','다음 명령은 kt66-dvwa 안에서 실행한다.',H),
 c('cd /var/www/html','DVWA 프로그램 디렉터리로 이동한다.','login.php와 vulnerabilities 디렉터리를 기준으로 조회한다.','kt66-dvwa 컨테이너 안'),
 c("grep -nE 'checkToken|generateSessionToken|dvwaRedirect' \\\n  login.php",'-n은 행 번호, -E는 확장 정규표현식이다. 이 식의 파이프(|)는 또는(OR)을 의미한다. 토큰 확인·갱신과 페이지 이동 함수가 있는 행을 출력한다.','checkToken, generateSessionToken과 login.php·index.php로의 이동을 확인한다.','kt66-dvwa 컨테이너 안'),
 c("grep -nE 'GET|Welcome|incorrect' \\\n  vulnerabilities/brute/source/low.php",'GET 입력과 성공·실패 문구를 찾는다. 파일은 읽기만 한다.','$_GET에서 username·password를 읽고 결과 문구를 나누는 행이 나온다.','kt66-dvwa 컨테이너 안'),
 c('exit','DVWA 컨테이너의 셸을 끝낸다.','kt66 호스트 터미널로 돌아온다.','kt66-dvwa 컨테이너 안'),
 p('$_GET은 PHP가 URL 쿼리 값을 읽을 때 쓰는 변수이다. 일반 로그인에서 쓰는 $_POST는 POST 본문으로 제출한 폼 값을 읽는다.'))
page('6.9  결과가 다를 때',
 tab(['증상','확인 순서'],[['DVWA가 열리지 않음','도메인·hosts의 IP → kt66 기동 상태 → 브리지 연결.'],['로그인 뒤 Setup으로 이동','기존 DB 여부 확인 → 처음 쓰는 DB라면 5.2 초기화 → 재로그인.'],['정상 화면으로 돌아가지 않음','User-Agent 기본값 복구 → login.php 재접속 → 세션 확인.'],['Gobuster가 요청을 시작하지 못함','-h로 버전·옵션 → 목록 파일 경로·내용 → 이름 해석 → 시작 오류 문구.'],['31151이 없음','개별 404 기록 → 같은 출발지인지 → 90초 안에 수집됐는지 → 규칙 변경 여부.'],['인증 요청이 경보에 없음','같은 식으로 아카이브 조회 → 위치·기간 → Apache 원본.'],['긴 요청이 414 또는 403','Network의 실제 URL 길이 → 서버 요청 제한 → WAF 감사 메시지.']],[47,80]),
 p('Discover에 없으면 kt66-web의 /var/log/apache2/dvwa_access.log에서 같은 경로를 먼저 찾는다. 파일에는 있으면 web 에이전트 연결·수집 설정과 인덱스·기간을 확인한다.'),
 p('WAF를 확인할 때는 modsec_audit.log의 요청 줄·출발지·시각을 접속 로그와 맞춘다. 서로 다른 요청의 규칙이나 응답을 한 사건으로 묶지 않도록 이 세 값을 대조한다.'))
page('6.9  원상복구와 조사 기록',
 p('① Network conditions의 Use browser default를 켠다. DVWA login.php를 다시 열고 Headers의 User-Agent에서 원래 브라우저 문자열을 확인한다.'),
 p('② 로그인해 DVWA Security를 시작 전에 메모한 값으로 바꾸고 Submit을 누른다. 현재 단계 표시가 바뀌었는지 확인한 뒤 Logout을 누른다.'),
 p('③ 공격자 VM에서 이 실습을 위해 새로 만든 목록 파일을 확인하고 삭제한다. 이전부터 있던 파일은 삭제하지 않는다.'),
 c('cat ~/book06-paths.txt','삭제 전 경로 목록 내용을 확인한다. ~는 공격자 계정의 홈 디렉터리이다.','이번에 만든 목록인지 확인한다. 다른 이름으로 만들었으면 그 파일명을 쓴다.'),
 c('rm -i ~/book06-paths.txt','rm은 파일을 삭제한다. -i는 삭제 전에 확인을 묻는다. 표시된 경로가 맞으면 y를 입력한다.','이 실습에서 새로 만든 파일 한 개를 삭제한다.'),
 c('ls -l ~/book06-paths.txt','삭제 후 같은 경로를 다시 확인한다.','No such file or directory가 나오면 파일이 제거됐다.'),
 p('④ 조사 양식 examples/chapter06/investigation.txt에 시각·출발지·요청·응답·규칙·판단 근거를 적는다. 검토할 로그는 보존한다.'),
 spot('path-test','실습 요청 목록 확인.'))
page('6.10  다른 방법 · curl로 헤더 지정',
 p('curl은 터미널에서 HTTP 요청과 응답을 확인하는 도구이다. 브라우저에서 수행한 헤더·메서드 시험을 공격자 VM에서도 할 수 있다. 도구 준비는 1.12, 이름 해석은 6.2와 같다. [11]'),
 c('curl --version','--version은 설치된 버전과 기능을 표시한다.','검증 환경은 Ubuntu 22.04의 curl 7.81.0이다. 명령이 없으면 1.12의 도구 설치를 먼저 수행한다.'),
 p('기본 구문은 curl 옵션 URL이다. -i는 응답 헤더를 본문 앞에 표시하고 --max-time 15는 전체 실행 시간을 최대 15초로 제한한다. -A는 보낼 User-Agent를 지정한다.'),
 c('curl -i --max-time 15 \\\n  -A "sqlmap/1.0 book06-curl-ua" \\\n  http://dvwa.kt66.lab/book06-curl-ua','큰따옴표는 공백을 포함한 헤더 값을 하나의 인자로 묶는다. 줄 끝의 역슬래시(\\)는 다음 줄로 명령을 잇는다.','검증 환경에서는 HTTP/1.1 403 Forbidden이 나왔다. data.url: *book06-curl-ua*로 찾고 WAF 메시지의 913100을 확인한다.'),
 q('agent.name: "web" AND data.url: *book06-curl-ua*','curl로 보낸 User-Agent 시험 경로를 찾는다.','출발지와 403 응답을 확인한다.'),
 p('브라우저의 6.3과 같은 헤더 시험이다. 요청 도구와 출발지 주소는 다르므로 새 실습 시각과 data.srcip을 기록한다. 이 옵션은 해당 curl 요청에만 적용된다.'))
page('6.10  다른 방법 · curl로 메서드 지정',
 p('-X는 HTTP 메서드를 지정한다. 이번에도 한 건만 전송한다. PROPFIND는 자원의 속성 조회를 요청하며 이 실습에서는 앞단 WAF가 거부했다.'),
 c('curl -i --max-time 15 -X PROPFIND \\\n  http://dvwa.kt66.lab/book06-curl-method','-i로 헤더를 함께 보고 --max-time으로 대기 시간을 제한한다. -X 뒤의 PROPFIND가 요청 메서드가 된다.','검증 환경에서는 403이었다. data.url: *book06-curl-method*로 찾고 같은 시각의 WAF 메시지 911100을 대조한다.'),
 q('agent.name: "web" AND data.url: *book06-curl-method*','curl로 지정한 메서드의 시험 경로를 찾는다.','data.protocol의 PROPFIND와 403 응답을 확인한다.'),
 p('Chrome의 fetch는 TRACE 같은 일부 메서드 전송을 제한한다. 이처럼 브라우저가 제한하는 요청을 직접 조사할 때는 별도 HTTP 도구가 필요하다. 이번 실습은 브라우저와 curl 모두 지원하는 PROPFIND로 비교했다.'),
 p('curl은 브라우저의 로그인 세션을 자동으로 공유하지 않는다. 이 두 요청은 로그인 없이 검사할 수 있는 경로이므로 세션 값을 복사할 필요가 없다.'),
)
page('6장 참고 자료 · 브라우저와 도구',
 h('[1] Network'),ref('Chrome DevTools · Network','https://developer.chrome.com/docs/devtools/network/'),
 h('[2] Gobuster 2.0.1'),ref('Gobuster · 2.0.1 README','https://github.com/OJ/gobuster/tree/v2.0.1'),
 h('[3] Wazuh 규칙'),ref('Wazuh 4.10.0 · 웹 규칙','https://github.com/wazuh/wazuh/blob/v4.10.0/ruleset/rules/0245-web_rules.xml'),ref('Wazuh · Rules syntax','https://documentation.wazuh.com/current/user-manual/ruleset/ruleset-xml-syntax/rules.html'),
 h('[4] User-Agent 변경'),ref('Chrome DevTools · Network conditions','https://developer.chrome.com/docs/devtools/device-mode/override-user-agent'))
page('6장 참고 자료 · 탐지와 인증',
 h('[5] OWASP CRS 3.3.2'),ref('CRS · 허용 메서드 정책','https://github.com/coreruleset/coreruleset/blob/v3.3.2/rules/REQUEST-911-METHOD-ENFORCEMENT.conf'),ref('CRS · 스캐너 헤더 탐지','https://github.com/coreruleset/coreruleset/blob/v3.3.2/rules/REQUEST-913-SCANNER-DETECTION.conf'),
 h('[6] 암호 추측 공격'),ref('OWASP · Brute Force Attack','https://owasp.org/www-community/attacks/Brute_force_attack'),
 h('[7] DVWA'),ref('DVWA · 공식 저장소','https://github.com/digininja/DVWA'),
 p('설치본은 DVWA v1.10 Development이다. 일반 로그인과 Brute Force 처리 설명은 설치본의 login.php 및 vulnerabilities/brute/source/low.php와 대조했다.'))
page('6장 참고 자료 · HTTP와 Console',
 h('[8] HTTP 메서드'),ref('MDN · HTTP request methods','https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods'),ref('RFC 4918 · WebDAV PROPFIND','https://www.rfc-editor.org/rfc/rfc4918#section-9.1'),
 h('[9] Console과 fetch'),ref('Chrome DevTools · Run JavaScript','https://developer.chrome.com/docs/devtools/console/javascript'),ref('MDN · Using Fetch','https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch'),ref('WHATWG Fetch · 제한된 메서드','https://fetch.spec.whatwg.org/#forbidden-method'),
 h('[10] 요청 줄 제한'),ref('Apache 2.4 · LimitRequestLine','https://httpd.apache.org/docs/2.4/mod/core.html#limitrequestline'),
 h('[11] curl'),ref('curl · Manual','https://curl.se/docs/manpage.html'))
# Keep instructions and their results together without reducing type or screen text.
def split_at(title,index,new_title):
 i=next(i for i,pg in enumerate(pages) if pg['title']==title);pg=pages[i]
 pages.insert(i+1,{'title':new_title,'kind':'body','blocks':pg['blocks'][index:]});pg['blocks']=pg['blocks'][:index]
def get(title):return next(pg['blocks'] for pg in pages if pg['title']==title)
# Tool introduction, installation, and address lookup each precede actual scanning.
b=get('6.2  목록 탐색 도구 준비');version_note=b.pop(-2);b.insert(3,version_note)
split_at('6.2  목록 탐색 도구 준비',4,'6.2  설치와 이름 해석 확인')
get('6.2  목록 탐색 도구 준비').append(spot('path-test','실습 경로 목록 확인.'))
# Separate rule reading from interpretation.
split_at('6.2  반복 경보의 조건 확인',5,'6.2  반복 경보의 조건 해석')
get('6.2  반복 경보의 조건 해석').insert(0,code('<rule id="31151" level="10"\n      frequency="14" timeframe="90">\n  <if_matched_sid>31101</if_matched_sid>\n  <same_source_ip />'))
get('6.2  반복 경보의 조건 해석').insert(1,p('앞에서 조회한 정의 중 반복 비교 조건이다. 31101은 응답 코드가 4로 시작하는 웹 요청을 분류한다.'))
split_at('6.3  헤더 변경 요청 보내기',5,'6.3  User-Agent 기록 검색')
split_at('6.3  WAF의 차단 이유 읽기',3,'6.3  WAF 차단 필드 해석')
# Move short conclusions next to the related query, away from full screenshot pages.
get('6.4  일반 로그인 기록 찾기').insert(0,get('6.4  일반 로그인 · 실패 확인').pop())
get('6.4  일반 로그인 기록 찾기').insert(1,get('6.4  일반 로그인 · 성공 확인').pop())
get('6.4  인증 시도의 URL 읽기').insert(0,get('6.4  후보를 바꾸어 결과 비교').pop())
get('6.4  인증 시도의 URL 읽기').pop() # spot illustration moves to the interpretation page below
get('6.3  WAF 차단 필드 해석').append(spot('log-review','요청 기록과 차단 근거 대조.'))
split_at('6.5  메서드 요청의 결과',3,'6.5  메서드 요청의 접속 기록')
split_at('6.5  허용 메서드 정책과 대조',3,'6.5  메서드 차단 필드 해석')
split_at('6.7  길이 경보 읽기',4,'6.7  요청 줄과 로그 크기 대조')
b=get('6.7  요청 줄과 로그 크기 대조');get('6.7  길이 경보 읽기').append(b.pop(1));b.insert(0,get('6.7  긴 URL과 로그 길이').pop(1))
# Explain PHP variables before readers see them in the output.
b=get('6.8  로그인 처리 코드의 위치');last=b.pop();b[0]=p('DVWA의 일반 로그인은 login.php, Brute Force의 Low 처리는 vulnerabilities/brute/source/low.php에 있다. $_GET은 URL 쿼리, $_POST는 POST 폼 값을 읽는 PHP 변수이다.')
get('6.9  원상복구와 조사 기록').pop() # illustration is already placed in tool preparation
number=0
for pg in pages:
 for b in pg['blocks']:
  if b.get('type')=='image' and b.get('caption','').startswith('화면 '):number+=1;b['caption']='화면 6-'+str(number)+'. '+b['caption'].split('. ',1)[1]
if __name__=='__main__':
 out=ROOT/'examples/chapter06';out.mkdir(parents=True,exist_ok=True)
 (ROOT/'manuscript/volume01-chapter06.json').write_text(json.dumps({'title':'웹 탐색과 인증 공격','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','pages':pages},ensure_ascii=False,indent=2)+'\n')
 for old in list(out.glob('C06-*.txt'))+list(out.glob('Q06-*.txt')):old.unlink()
 for item in browser_inputs:(out/item['file']).write_text(item['text']+'\n')
 (out/'browser-inputs.json').write_text(json.dumps(browser_inputs,ensure_ascii=False,indent=2)+'\n')
 for b in commands+queries:(out/(b['id']+'.txt')).write_text(b['text']+'\n')
 (out/'manifest.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n');(out/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2)+'\n')
 (out/'investigation.txt').write_text('실행 위치·시각·시간대:\n대상 사이트·요청 URL·메서드:\n입력값·User-Agent:\nHTTP 상태·Location·본문 결과:\nagent.name·data.srcip·location:\n_index·_id·rule.id:\nWAF transaction_id·규칙·차단 근거:\n반복 요청의 횟수·시간 간격:\n확인한 사실·추가 확인할 자료:\nUser-Agent·학습 단계·파일 원상복구:\n')
 print(len(pages),'pages',len(commands),'commands',len(queries),'queries',number,'screens')
