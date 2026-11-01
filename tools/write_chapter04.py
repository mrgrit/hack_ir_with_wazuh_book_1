"""4장: 확인 로그 수집 → 규칙 시험 → 사용자 규칙 적용과 원상복구."""
import json
from pathlib import Path
from write_chapter01 import p,h,tab,img,code
ROOT=Path(__file__).resolve().parents[1]
pages=[];commands=[];queries=[]
def page(title,*blocks):pages.append({'title':title,'kind':'body','blocks':list(blocks)})
def c(text,why,result,where='kt66-bastion 컨테이너 안'):
 b={'type':'command','id':f'C04-{len(commands)+1:02d}','text':text,'why':why,'result':result,'where':where};commands.append(b);return b
def q(text,why,result):
 b={'type':'query','id':f'Q04-{len(queries)+1:02d}','text':text,'why':why,'result':result,'where':'Windows · Discover 검색창'};queries.append(b);return b
def sc(name,caption,width=127):return img(f'assets/screens/chapter04/{name}.png',caption,width)
def fig(name,caption):return img(f'assets/figures/chapter04/{name}.png',caption)
B='kt66-bastion 컨테이너 안';S='kt66-siem 컨테이너 안';H='kt66 VM · 호스트 터미널'
marker="logger -p authpriv.notice -t book04 \\\n  'book04-collection-01'"
findlog="grep -F 'book04: book04-collection-01' \\\n  /var/log/auth.log"
rule='book04_rules.xml'
page('4장  로그 수집과 탐지 규칙',
 h('4.1  확인 로그를 경보로 만들기'),
 p('bastion에 확인 문구를 기록하고 Wazuh에서 찾는다. 처음에는 수집 기록을 확인하고, 사용자 규칙을 추가한 뒤 같은 문구로 경보를 만든다.'),
 tab(['항목','준비·확인'],[['실행 위치','kt66 VM 터미널, Windows 브라우저'],['선행 조건','1장 설치 완료, bastion 연결, 3장 Discover 검색'],['수집 확인','원문과 location이 일치하는 기록을 찾는다.'],['규칙 확인','Ruleset Test의 결과를 읽고 새 경보 100410을 찾는다.'],['오류 확인','4.11의 순서로 원문·수집·규칙·저장을 확인한다.'],['원상복구','4.10에서 실습 규칙을 삭제하고 Manager를 재시작한다.']],[30,97]),
 fig('collection-path','도식 4-1. bastion 로그의 수집·검색 경로.'),
 p('Filebeat는 Manager가 저장한 로그 파일을 Indexer로 전송하는 프로그램이다. kt66이 Manager 컨테이너에 함께 구성한다. [1]'))
page('4.2  수집 파일 확인',
 p('bastion의 SSH 인증 기록은 /var/log/auth.log에 남는다. Wazuh 에이전트는 ossec.conf의 localfile 설정에 따라 이 파일을 읽는다. 이 설정은 kt66이 추가한다.'),
 c('docker exec -it kt66-bastion /bin/bash','실행 중인 kt66-bastion에 Bash로 접속한다. -i는 입력을 유지하고 -t는 터미널을 할당한다.','프롬프트가 컨테이너 안으로 바뀐다.',H),
 c('hostname','hostname은 현재 시스템의 호스트 이름을 출력한다.','bastion이 나온다.'),
 c("grep -F -B 1 -A 1 '/var/log/auth.log' \\\n  /var/ossec/etc/ossec.conf",'grep의 기본 구문은 grep 옵션 찾을문자열 파일이다. -F는 문자열 그대로 찾고, -B 1과 -A 1은 앞뒤 한 줄을 함께 출력한다. 줄 끝의 역슬래시는 명령을 다음 줄로 잇는다.','log_format, location, 닫는 localfile 태그를 확인한다.'),
 code('<log_format>syslog</log_format>\n<location>/var/log/auth.log</location>\n</localfile>'),
 p('log_format은 해석할 로그 형식, location은 읽을 파일이다. XML은 <이름>과 </이름> 사이에 값을 적는다. localfile은 수집 대상 하나를 묶는 항목이다. [2]'))
page('4.3  확인 문구 기록',
 p('logger는 문장을 시스템 로그로 보내는 명령이다. rsyslog는 시스템 로그를 받아 파일에 저장하는 프로그램이다. kt66은 둘을 bastion에 준비하고 인증 관련 메시지를 auth.log에 저장하도록 설정한다.'),
 c(findlog,'기록하기 전에 같은 확인 문구가 있는지 찾는다. 작은따옴표는 공백을 포함한 문자열을 하나의 인자로 묶는다.','처음 실행하면 출력이 없다. 이미 기록이 있으면 마지막 시각을 적는다.'),
 c(marker,'기본 구문은 logger [옵션] 메시지이다. 아래 옵션으로 인증 로그에 확인 문구를 보낸다. [9]','보통 화면 출력 없이 끝난다. 4.3의 다음 페이지에서 auth.log에 저장된 행을 확인한다.'),
 tab(['옵션·구문','뜻'],[
 ['-p authpriv.notice','-p는 로그 분류와 중요도를 지정한다. authpriv는 인증·보안 분류, notice는 정상 동작 중 주목할 기록의 중요도이다. 점(.)으로 두 값을 잇는다.'],
 ['-t book04','-t는 로그에 붙일 태그를 지정한다. 원문의 프로그램 이름 자리에 book04가 들어간다.'],
 ["'book04-collection-01'",'기록할 메시지이다. 작은따옴표 안의 문자를 그대로 전달한다.'],
 ['역슬래시(\\)','줄 끝의 역슬래시는 다음 줄까지 하나의 명령으로 잇는다. 두 줄을 함께 입력한다.']],[43,84]),
 )
page('4.3  기록 결과 확인',
 c(findlog,'같은 문자열을 다시 찾아 새로 추가된 행을 읽는다.','현재 시각, bastion, book04 태그, 확인 문구가 한 행에 나온다.'),
 code('Nov  1 19:20:01 bastion book04:\nbook04-collection-01'),
 p('위 예시의 시각은 검증 때의 값이다. 자신의 출력 시각을 기록한다. 직접 남긴 수집 확인용 메시지이다. notice는 시스템 로그의 중요도이며, Wazuh 규칙의 level은 별도로 정한다.'),
 c('exit','현재 Bash 세션을 끝낸다.','kt66 VM의 호스트 터미널로 돌아온다.'),
 {'type':'image','path':'assets/illustrations/chapter04/field-check.png','caption':'삽화. 현장 장비의 로그 수집 점검.','width_mm':62,'align':'right'})
page('4.4  아카이브에서 찾기',
 p('아카이브는 Manager가 받은 전체 로그를 저장하는 기록이다. 경보는 그중 규칙과 경보 저장 조건을 만족한 기록이다. kt66은 기본적으로 JSON 아카이브 저장과 전송을 켠다. [1][3]'),
 fig('storage','도식 4-2. 아카이브와 경보 저장.'),
 p('Windows의 Discover에서 인덱스 패턴을 wazuh-archives-*로 선택한다. 기간은 Last 24 hours로 정한다.'),
 q('agent.name: "bastion"\nAND predecoder.program_name: "book04"',
 'predecoder.program_name은 로그 앞부분에서 읽은 프로그램 이름이다. 여기서는 logger의 태그 book04가 들어간다. 두 줄을 함께 입력한다.',
 '결과 한 행을 펼쳐 full_log에 자신이 남긴 시각과 확인 문구가 있는지 읽는다.'),
 p('목록에 패턴이 없거나 결과가 없으면 4.11에서 아카이브 설정과 전송 상태를 확인한다.'))
page('4.4  원문과 수집 위치 대조',
 sc('archive-record','화면 4-1. 확인 문구의 아카이브 기록.'),
 tab(['필드','확인할 값'],[['agent.name','bastion'],['location','/var/log/auth.log'],['predecoder.program_name','book04'],['full_log','터미널에서 확인한 시각과 확인 문구'],['id','Manager가 붙인 이벤트 식별자'],['input.type: log','로그 입력임을 나타내는 분류']],[57,70]),
 p('agent.name, location, program_name과 원문이 일치하면 auth.log에 쓴 문장이 Wazuh까지 전달된 것이다. 문자열만 검색하면 명령 실행을 기록한 audit 로그나 sudo 로그도 나올 수 있다. 수집 위치와 원문을 함께 읽는다.'),
 p('같은 검색식을 유지하고 패턴을 wazuh-alerts-*로 바꾼다. 사용자 규칙을 추가하기 전의 이 확인 문구는 검증 환경에서 경보가 없었다. 다시 wazuh-archives-*로 바꿔 원문을 확인한다.'))
page('4.5  SSH 원문으로 규칙 시험',
 p('Ruleset Test는 입력한 원문에 적용되는 디코더와 규칙을 확인하는 도구이다. Wazuh Manager에 포함된 wazuh-logtest를 화면에서 사용한다. [4]'),
 p('선행 조건은 Wazuh 로그인과 Manager 기동이다. 왼쪽 메뉴에서 Server management → Ruleset Test를 연다.'),
 p('집필 저장소의 examples/chapter04/ssh-failed.log를 열어 한 줄 전체를 입력하고 Test를 누른다. kt66-bastion의 /var/log/auth.log에서 수집한 2장의 SSH 실패 사례이다.'),
 sc('logtest-input','화면 4-2. Ruleset Test에 SSH 원문 입력.',115),
 p('결과는 Phase 1, 2, 3 순서로 나온다. 먼저 프로그램 이름과 추출한 필드를 읽고, 마지막에 규칙 번호와 수준을 확인한다.'))
page('4.5  로그에서 필드 추출',
 sc('logtest-decode','화면 4-3. SSH 로그의 사전 분석과 디코딩.'),
 p('full event는 시험에 넣은 로그 전체이다. 먼저 예제 파일의 한 줄과 같은지 확인한다. Phase 1은 앞부분에서 시각·호스트·프로그램 이름을 읽은 결과이다.'),
 tab(['원문의 부분','Phase 1 필드·뜻'],[
 ['Nov  1 14:22:35','timestamp · 원문에 적힌 시각'],
 ['bastion','hostname · 로그에 적힌 호스트 이름'],
 ['sshd[7249]','program_name: sshd · 로그를 남긴 프로그램 이름']],[45,82]),
 p('sshd는 SSH 서버 프로그램이다. 대괄호의 7249는 해당 프로세스 번호이며 program_name에는 포함되지 않는다.'),
 p('이 timestamp에는 연도와 시간대가 없다. 3장에서 본 경보의 timestamp는 Manager가 경보를 만든 시각이므로 원문 시각과 구분한다.'))
page('4.5  디코더 결과 해석',
 p('Phase 2는 선택된 디코더와 본문에서 추출한 값을 보여 준다. 부모 디코더 sshd는 프로그램 이름으로 SSH 로그를 분류한다. 여기에 연결된 하위 디코더는 본문 형식을 확인하고 계정과 출발지 주소를 읽는다.'),
 tab(['표시','뜻·읽을 값'],[
 ['name: sshd','결과에 표시하는 디코더 이름'],
 ['parent: sshd','하위 디코더가 연결된 상위 디코더 이름'],
 ['srcuser: book03_probe','로그인에 사용한 계정명'],
 ['srcip: 10.20.30.254','로그가 기록한 접속 출발지 IP']],[51,76]),
 fig('decoder-fields','도식 4-3. 원문에서 추출한 계정과 출발지.'),
 p('Phase 1의 program_name은 로그 속 프로그램 이름이다. Phase 2의 name은 분석에 사용한 디코더의 표시 이름이다. 이 사례에서는 두 값이 모두 sshd이다.'),
 p('계정과 주소를 실제로 추출하는 하위 정의는 ssh-invfailed이다. 이 정의는 부모 이름을 결과에 사용하므로 name과 parent가 모두 sshd로 나온다. 다음 파일에서 연결 관계를 확인한다. [8]'))
page('4.5  원문·예제·디코더의 위치',
 h('bastion의 원본 로그'),
 p('kt66-bastion 컨테이너 안에서 SSH 서버의 인증 활동을 기록한다. 에이전트는 4.2에서 확인한 설정으로 이 파일을 수집한다.'),
 code('/var/log/auth.log'),
 h('독자가 여는 예제 파일'),
 p('집필 저장소의 아래 파일에는 기존 SSH 실패 로그 한 줄을 보존했다. Windows에서 저장소의 파일을 열어 Ruleset Test 입력란에 복사한다.'),
 code('examples/chapter04/ssh-failed.log'),
 h('Manager의 디코더 정의'),
 p('kt66-siem 컨테이너 안의 기본 디코더 파일이다. Wazuh Manager 설치 시 제공된다. 사전 분석 후 어떤 문장에서 어떤 값을 추출할지 정의한다.'),
 code('/var/ossec/ruleset/decoders/0310-ssh_decoders.xml'),
 h('Manager의 SSH 탐지 규칙'),
 p('같은 컨테이너의 아래 파일에는 분석한 로그를 경보로 분류하는 규칙이 있다. 4.6에서 규칙 5710을 확인한다.'),
 code('/var/ossec/ruleset/rules/0095-sshd_rules.xml'))
page('4.5  디코더 정의 직접 확인',
 p('선행 조건은 kt66-siem 실행 상태이다. 파일을 읽어 부모 디코더와 하위 디코더를 찾고, 시험 결과의 이름과 대조한다.'),
 c('docker exec -it kt66-siem /bin/bash','Manager 컨테이너에 접속한다.','이 페이지의 나머지 명령은 kt66-siem 안에서 실행한다.',H),
 c('cd /var/ossec/ruleset/decoders','cd 경로는 작업 디렉터리를 옮긴다. SSH 디코더 파일이 있는 곳으로 이동한다.','다음 명령에서 0310-ssh_decoders.xml을 파일명으로 지정할 수 있다.',S),
 c("grep -n -A 2 '<decoder name=\"sshd\">' \\\n  0310-ssh_decoders.xml",'정의의 시작 행과 다음 두 줄을 출력한다. -n은 줄 번호, -A 2는 뒤의 두 줄이다.','program_name 조건이 ^sshd인지 읽는다. ^는 이름의 시작을 뜻한다.',S),
 c("grep -n -A 5 '<decoder name=\"ssh-invfailed\">' \\\n  0310-ssh_decoders.xml",'-n으로 줄 번호를 붙이고 -A 5로 일치한 행 뒤의 다섯 줄까지 출력한다. 작은따옴표 안의 XML 시작 태그를 찾는다.','parent, prematch, regex, order를 확인한다. 아래 설명과 각 값을 대조한다.',S),
 p('파일이 없으면 접속한 컨테이너와 디렉터리를 확인한다. 추출 결과가 다르면 예제 원문과 설치 버전의 정의부터 대조한다.'))
page('4.5  추출 조건 읽기',
 p('ssh-invfailed 정의는 다음 순서로 읽는다. [8]'),
 tab(['항목','역할'],[
 ['parent','sshd 부모 디코더에 일치한 로그를 대상으로 한다.'],
 ['prematch','본문이 존재하지 않는 계정의 암호 인증 실패 형식인지 확인한다.'],
 ['regex','본문에서 계정과 IP에 해당하는 문자열을 추출한다.'],
 ['order','추출한 값을 넣을 필드를 괄호 순서대로 지정한다.']],[30,97]),
 h('prematch의 문장 조건'),
 code(r'^Failed \S+ for invalid user|'+ '\n' + r'^Failed \S+ for illegal user'),
 p('캐럿(^)은 본문 시작을 뜻한다. 이 정규표현식에서 파이프(|)는 또는(OR)을 의미한다. 양쪽 조건 중 하나에 일치하면 통과한다. 이 원문의 Failed password for invalid user는 첫 조건에 일치한다.'),
 h('regex와 order'),
 code(r'(\S+) from (\S+)'+'\n'+'srcuser,srcip'),
 p(r'\S는 공백이 아닌 문자이다. 수량자 +는 앞의 문자 조건을 한 번 이상 반복한다. 소괄호( )는 추출할 부분을 묶는다. 첫 괄호는 book03_probe, 둘째는 10.20.30.254를 얻는다. order에 따라 각각 srcuser와 srcip에 넣는다.'),
 p('regex의 offset="after_prematch"는 prematch가 읽은 부분 다음부터 추출한다는 뜻이다. 이 정의에는 포트를 추출하는 괄호가 없어 원문에 50964가 있어도 srcport는 나오지 않는다.'))
page('4.5  추출 결과와 경보 대조',
 p('집필 저장소의 examples/chapter02/case-ssh.json을 연다. 같은 SSH 원문의 기존 경보이다. _source 아래에서 다음 항목을 찾는다.'),
 tab(['Ruleset Test','경보에서 확인할 항목'],[
 ['full event','full_log · 입력한 원문 전체'],
 ['Phase 1 · timestamp','predecoder.timestamp · 원문 시각'],
 ['hostname','predecoder.hostname · bastion'],
 ['program_name','predecoder.program_name · sshd'],
 ['Phase 2 · name','decoder.name · sshd'],
 ['srcuser','data.srcuser · book03_probe'],
 ['srcip','data.srcip · 10.20.30.254']],[47,80]),
 p('원문의 invalid user는 없는 계정, Failed password는 암호 인증 실패를 뜻한다. 추출한 값과 합쳐 “10.20.30.254에서 book03_probe 계정으로 로그인하려 했으며 암호 인증이 실패했다”로 읽는다.'),
 p('full_log와 추출된 계정·IP가 예제 원문과 일치하는지 확인한다. 값이 다르면 원문 → 사전 분석 → 디코더 조건과 order 순서로 대조한다.'),
 c('exit','디코더 확인을 마치고 Manager 컨테이너에서 나온다.','호스트 터미널로 돌아온다. 파일은 조회만 했으므로 원상복구할 변경이 없다.',S))
page('4.6  규칙의 조건 읽기',
 sc('logtest-rule','화면 4-4. 규칙 5710의 시험 결과.'),
 p('Phase 3의 id는 규칙 번호, level은 규칙의 경보 수준, description은 탐지 내용의 설명이다. groups는 규칙의 분류 목록이고 firedtimes는 현재 시험 세션에서 해당 규칙에 일치한 횟수이다. 이 원문은 5710, 수준 5에 일치한다.'),
 h('규칙 5710의 핵심 조건 [5]'),
 code('<rule id="5710" level="5">\n  <if_sid>5700</if_sid>\n  <match>illegal user|invalid user</match>'),
 p('if_sid는 같은 로그가 앞서 지정한 규칙에 일치해야 한다는 조건이다. 5700은 sshd 디코더의 로그를 묶는다. match의 파이프(|)는 또는(OR)을 의미한다. illegal user와 invalid user 중 하나라도 들어 있으면 일치한다.'),
 p('이 원문에는 invalid user가 있으므로 존재하지 않는 계정의 로그인 시도로 분류된다.'),
 h('시험 결과와 저장된 경보'),
 p('Alert to be generated는 입력한 원문이 경보 규칙에 일치했다는 시험 결과이다. Ruleset Test 입력은 실제 로그 파일에 기록되지 않는다. 수집·전송 결과는 Discover에서 새 기록을 찾아 확인한다.'))
page('4.6  규칙 파일 확인',
 p('앞 페이지의 규칙 번호로 Manager의 실제 정의를 찾는다. 디코더는 값 추출, 규칙은 분류와 경보 수준을 정한다.'),
 c('docker exec -it kt66-siem /bin/bash','SSH 규칙을 확인할 Manager 컨테이너에 접속한다.','kt66-siem 안에서 다음 명령을 입력한다.',H),
 c('cd /var/ossec/ruleset/rules','기본 탐지 규칙이 있는 디렉터리로 이동한다.','0095-sshd_rules.xml을 파일명으로 조회한다.',S),
 c("grep -n -A 3 '<rule id=\"5700\"' \\\n  0095-sshd_rules.xml",'-n은 줄 번호, -A 3은 일치한 행 뒤의 세 줄을 함께 출력한다. 작은따옴표로 묶은 rule 태그와 번호를 찾는다.','decoded_as가 sshd이면 sshd 디코더의 로그를 대상으로 한다. 5700은 level="0", noalert="1"인 분류용 규칙으로 자체 경보는 만들지 않는다.',S),
 c("grep -n -A 3 '<rule id=\"5710\"' \\\n  0095-sshd_rules.xml",'5710의 정의와 뒤의 세 줄을 읽는다.','if_sid의 5700, match의 두 문구, description을 화면 4-4와 대조한다.',S),
 c('exit','규칙 파일 확인을 마친다.','호스트 터미널로 돌아온다. 규칙 파일의 변경은 없다.',S))
page('4.6  문구를 바꾸어 비교',
 p('Clear session을 누르고 Confirm을 누른다. 이전 입력의 누적 상태를 비우고 새 시험을 시작한다.'),
 p('examples/chapter04/ssh-variant.log를 입력한다. 앞 원문에서 invalid user 두 단어만 제거한 시험용 문장이다. 실제 접속을 새로 수행한 기록과 구분한다.'),
 code('Nov  1 14:22:35 bastion sshd[7249]:\nFailed password for book03_probe\nfrom 10.20.30.254 port 50964 ssh2'),
 p('Test를 누르고 Phase 3을 비교한다.'),
 sc('logtest-variant','화면 4-5. 변경한 SSH 문장의 규칙 결과.'),
 tab(['원문','규칙·결과'],[['invalid user 포함','5710 · 존재하지 않는 계정의 접속 시도'],['invalid user 제거','5760 · 인증 실패']],[48,79]),
 p('변경한 문장은 같은 디코더 파일의 ssh-failed 정의에 일치한다. 이 정의의 order는 user, srcip, srcport이다. user는 시험 결과에서 dstuser로 표시되며 출발지 포트 50964도 추출된다. 앞 문장의 ssh-invfailed는 srcuser, srcip만 지정한다. 계정 필드와 포트의 차이는 두 정의의 order에서 확인한다.'),
 p('시험을 마치면 Clear session → Confirm을 누른다. 이 작업은 시험의 입력 이력을 초기화한다.'))
page('4.7  확인 문구용 규칙 준비',
 p('이제 book04 태그와 확인 문구에 일치하는 규칙을 만든다. 규칙 번호는 사용자 정의 범위인 100000~120000 중 100410을 사용한다. [6]'),
 fig('rule-conditions','도식 4-4. 확인 문구를 찾는 두 조건.'),
 c('docker exec -it kt66-siem /bin/bash','Manager가 실행 중인 kt66-siem에 접속한다.','이후 명령은 kt66-siem 안에서 실행한다.',H),
 c('ls -l /var/ossec/etc/rules/book04_rules.xml','새 파일을 만들기 전에 같은 이름의 파일이 있는지 확인한다. ls -l은 소유자·권한 등 상세 정보를 출력한다.','첫 실습이면 No such file or directory가 나온다. 이미 있으면 새 파일명을 정하고 이후 명령의 파일명도 모두 바꾼다.',S),
 c("grep -R -n '100410' /var/ossec/etc/rules \\\n  /var/ossec/ruleset/rules",'규칙 번호가 이미 쓰이는지 찾는다. -R은 하위 디렉터리까지, -n은 일치한 줄 번호를 출력한다.','사용하지 않는 번호이면 출력이 없다. 기존 규칙이 나오면 해당 규칙을 보존하고 실습용 번호를 변경한다.',S))
page('4.7  규칙 파일 작성',
 p('설치된 기본 규칙은 /var/ossec/ruleset/rules에 있다. 사용자 규칙은 /var/ossec/etc/rules에 별도 XML 파일로 둔다.'),
 c('nano /var/ossec/etc/rules/book04_rules.xml','nano 파일명으로 편집기를 연다. 아래 내용을 입력한다.','Ctrl+O, Enter로 저장하고 Ctrl+X로 닫는다.',S),
 code((ROOT/'examples/chapter04/book04_rules.xml').read_text().strip()),
 tab(['항목','뜻'],[['group name="book04,"','규칙 분류 이름. 쉼표로 그룹을 구분한다.'],['id="100410" · level="5"','고유 규칙 번호와 경보 수준'],['program_name','^는 시작, $는 끝이다. ^book04$는 이름 전체가 book04인 경우에 일치한다.'],['match','로그에 book04-collection-01이 포함되는지 찾는다.'],['description','경보에 표시할 설명']],[47,80]),
 p('복사용 파일은 examples/chapter04/book04_rules.xml이다. 규칙 번호를 바꿨다면 이후 검색식의 번호도 함께 바꾼다.'))
page('4.7  저장 내용과 권한 확인',
 c('cat /var/ossec/etc/rules/book04_rules.xml','cat 파일명은 파일 내용을 출력한다. 저장된 XML을 앞쪽 예제와 대조한다.','여는 태그와 닫는 태그, 번호, 프로그램 이름, 확인 문구가 일치해야 한다.',S),
 c('chown root:wazuh \\\n  /var/ossec/etc/rules/book04_rules.xml','chown 소유자:그룹 파일 형식으로 소유권을 정한다. 이 파일은 root가 관리하고 wazuh 그룹이 읽는다.','다음 권한 설정 후 ls -l로 두 값을 함께 확인한다.',S),
 c('chmod 640 /var/ossec/etc/rules/book04_rules.xml','chmod 권한값 파일 형식이다. 6은 소유자의 읽기·쓰기, 4는 그룹의 읽기, 0은 그 밖의 사용자에게 권한을 주지 않는 값이다.','소유자만 수정하고 wazuh 그룹은 읽을 수 있다.',S),
 c('ls -l /var/ossec/etc/rules/book04_rules.xml','파일의 권한과 소유권을 다시 출력한다.','-rw-r-----와 root wazuh를 확인한다.',S))
page('4.8  규칙 검사',
 c('/var/ossec/bin/wazuh-analysisd -t','wazuh-analysisd는 로그 분석 프로그램이다. -t는 실행을 시작하는 대신 설정과 규칙을 검사한다.','오류가 없으면 별도 출력 없이 종료한다. ERROR가 나오면 재시작 전에 파일을 고친다.',S),
 c('echo $?','echo는 값을 출력한다. $?는 바로 앞 명령의 종료 상태이다. 검사 직후 입력한다.','0이면 검사 성공이다. 다른 값이면 오류 내용을 확인한다.',S),
 p('Windows의 Ruleset Test에서 Clear session → Confirm을 누른다. examples/chapter04/collection-test.log를 입력하고 Test를 누른다.'),
 sc('logtest-custom','화면 4-6. 사용자 규칙 100410 시험 결과.'),
 p('Phase 3에서 100410과 수준 5를 확인한다. Phase 2의 No decoder matched는 별도 디코더가 일치하지 않았다는 뜻이다. 이 규칙은 사전 분석의 program_name과 본문으로 판단하므로 동작한다. mail: false는 이 결과가 이메일 알림 대상으로 지정되지 않았다는 뜻이다.'))
page('4.9  적용하고 새 로그 발생',
 fig('apply','도식 4-5. 규칙 적용과 확인 순서.'),
 c('/var/ossec/bin/wazuh-control restart','wazuh-control은 Manager의 프로세스를 제어한다. restart는 중지 후 다시 시작해 저장한 규칙을 실제 수신 로그에 적용한다. [6]','Completed가 나올 때까지 기다린다. 재시작 중에는 분석과 API 응답이 잠시 멈춘다.',S),
 c('/var/ossec/bin/wazuh-control status','status는 각 프로세스의 실행 상태를 출력한다.','wazuh-analysisd와 wazuh-remoted가 is running인지 확인한다.',S),
 p('analysisd는 로그를 분석하고 remoted는 에이전트의 로그를 받는다. 메일 발송용 maild와 Manager 클러스터용 clusterd는 해당 기능을 쓰지 않으면 not running으로 나온다.'),
 c('exit','Manager 컨테이너의 Bash를 끝낸다.','kt66 VM 호스트 터미널로 돌아온다.',S))
page('4.9  새 경보 확인',
 c('docker exec -it kt66-bastion /bin/bash','확인 문구를 다시 남길 bastion에 접속한다.','이후 두 명령은 bastion 안에서 실행한다.',H),
 c(marker,'4.3과 같은 문구를 새로 기록한다. 기존 아카이브 기록은 새 규칙으로 다시 분석되지 않으므로 새 로그가 필요하다.','다음 명령으로 새 행의 시각을 확인한다.'),
 c(findlog,'추가된 행을 읽어 새 로그의 시각을 기록한다.','이전 행보다 늦은 시각의 확인 문구가 나온다.'),
 c('exit','bastion의 Bash를 끝낸다.','호스트 터미널로 돌아온다.'),
 p('Windows의 Discover에서 wazuh-alerts-*와 Last 24 hours를 선택한다. 다음 검색식을 입력한다.'),
 q('agent.name: "bastion" AND rule.id: "100410"','bastion에서 수집한 경보 중 새 규칙 100410에 일치한 기록을 찾는다.','결과를 펼쳐 새로 남긴 로그의 시각, 원문, 규칙 번호를 대조한다.'))
page('4.9  경보의 근거 읽기',
 sc('alert-record','화면 4-7. 사용자 규칙으로 생성된 경보.'),
 tab(['항목','검증 환경의 결과'],[['원문 시각','2026년 11월 1일 19:22:01 · KST'],['rule.id · rule.level','100410 · 5'],['rule.description','Book04 collection check'],['location','/var/log/auth.log'],['predecoder.program_name','book04']],[53,74]),
 p('이 경보는 직접 만든 확인 문구를 탐지한 결과이다. 수준 5는 실습 규칙에서 지정한 값이다. 사건의 위험도는 원문과 실제 활동을 조사해 판단한다.'),
 p('Manager의 log_alert_level은 경보 파일에 저장할 최소 수준이다. 검증 환경의 값은 3이다. 이 규칙의 수준 5는 저장 기준을 만족한다. [7]'),
 p('wazuh-archives-*에서는 규칙 추가 전후의 문구를 모두 볼 수 있다. wazuh-alerts-*에서는 규칙 적용 후 새로 발생한 경보를 찾는다.'))
page('4.10  실습 규칙 원상복구',
 p('실습에서 새로 만든 book04_rules.xml만 삭제한다. 앞서 같은 이름의 파일이 있어 다른 파일명을 사용했다면 그 파일명을 지정한다.'),
 c('docker exec -it kt66-siem /bin/bash','실습 규칙을 제거할 Manager 컨테이너에 접속한다.','kt66-siem 안에서 계속한다.',H),
 c('cat /var/ossec/etc/rules/book04_rules.xml','삭제할 파일의 내용을 먼저 확인한다.','이번에 작성한 100410 규칙과 확인 문구인지 대조한다.',S),
 c('rm /var/ossec/etc/rules/book04_rules.xml','rm 파일명은 지정한 파일을 삭제한다. 다른 규칙 파일을 지정하지 않도록 경로를 확인한다.','다음 명령으로 해당 파일이 없어졌는지 확인한다.',S),
 c('ls -l /var/ossec/etc/rules/book04_rules.xml','삭제한 경로를 다시 조회한다.','No such file or directory가 나온다.',S),
 p('이미 저장된 경보와 아카이브는 남아 있다. 실습 결과를 대조할 자료로 보관한다.'))
page('4.10  원상복구 후 실행 확인',
 c('/var/ossec/bin/wazuh-analysisd -t','남은 규칙과 설정의 구문을 검사한다.','오류 메시지가 없어야 한다.',S),
 c('echo $?','검사 직후 종료 상태를 읽는다.','0을 확인한다.',S),
 c('/var/ossec/bin/wazuh-control restart','삭제한 규칙이 적용 대상에서 빠지도록 Manager를 다시 시작한다.','Completed를 확인한다.',S),
 c('/var/ossec/bin/wazuh-control status','재시작한 프로세스의 상태를 확인한다.','wazuh-analysisd와 wazuh-remoted가 실행 중이어야 한다.',S),
 c('exit','Manager 컨테이너의 Bash를 끝낸다.','kt66 VM 호스트로 돌아온다.',S),
 p('브라우저에서는 Ruleset Test의 Clear session → Confirm을 누른다. Discover의 검색식과 필터를 비우고 wazuh-alerts-*, Last 24 hours로 되돌린다.'))
page('4.11  어느 단계에서 멈췄는가',
 tab(['증상','확인 순서'],[['auth.log에 문구가 없다','실행 위치가 bastion인지 확인한다. logger의 -p, -t와 문구를 대조하고 원본 파일을 다시 읽는다.'],['원문은 있으나 아카이브가 없다','bastion 연결 → localfile 경로 → 검색 기간·조건 → 아카이브 저장·전송 설정 순서로 확인한다.'],['Ruleset Test가 다른 규칙을 표시한다','입력 원문 → Clear session → 저장한 XML → 규칙 번호 중복 순서로 확인한다.'],['시험은 100410인데 새 경보가 없다','구문 검사 → Manager 재시작 → 새 로그 생성 → 경보 저장 기준 → Discover 기간·패턴 순서로 확인한다.'],['Manager가 시작되지 않는다','오류에 표시된 파일·줄을 확인한다. 실습 파일을 제거하고 구문 검사 후 재시작한다.']],[43,84]),
 p('설정에서 수집하는 파일과 검색 결과의 location을 대조한다. kt66 호스트의 기본 인증 기록 수집은 journald이고, 이 장의 bastion은 auth.log이다. 두 실행 위치를 구분한다.'),
 p('아카이브를 켜면 수신 기록 전체를 저장하므로 경보만 저장할 때보다 디스크 사용량이 늘어난다. 실습 후에도 VM의 남은 공간을 확인한다.'))
page('4.11  아카이브 설정 확인',
 p('검색에 문제가 있을 때 읽을 설정이다. 실행 중인 값을 확인하고 1.11의 서비스 점검과 연결한다.'),
 c('docker exec -it kt66-siem /bin/bash','아카이브 저장과 전송을 맡는 Manager 컨테이너에 접속한다.','kt66-siem 안에서 확인한다.',H),
 c("grep -E 'logall_json|log_alert_level' \\\n  /var/ossec/etc/ossec.conf",'-E는 확장 정규표현식으로 검색한다. 작은따옴표 안의 파이프(|)는 또는(OR)을 의미한다. logall_json과 log_alert_level 중 하나라도 포함한 행을 출력한다.','kt66 기본 설정은 logall_json이 yes, 경보 저장 기준 log_alert_level이 3이다.',S),
 c("grep -A 2 'archives:' /etc/filebeat/filebeat.yml",'-A 2는 archives: 행과 그 뒤 두 줄을 출력한다. Filebeat의 아카이브 전송 설정을 읽는다.','archives 아래 enabled: true인지 확인한다.',S),
 c('exit','설정 조회를 마치고 컨테이너에서 나온다.','호스트 터미널로 돌아온다.',S),
 p('kt66의 .env에 WAZUH_ARCHIVES=no가 지정되어 있으면 기본 활성화 단계가 생략된다. 원고의 기준 설정과 다르면 1장의 설정·기동 절차부터 대조한다. 설정을 고쳤다면 같은 확인 문구를 새로 남겨 결과를 확인한다.'))
page('4.12  확인 결과 정리',
 tab(['확인 대상','완료 근거'],[['원본 기록','bastion의 auth.log에 확인 문구가 있다.'],['수집·전송','아카이브의 full_log·location이 원본과 일치한다.'],['디코더·기본 규칙','SSH 원문은 sshd 디코더와 규칙 5710에 일치한다.'],['사용자 규칙','Ruleset Test에서 100410·수준 5를 확인했다.'],['새 경보','재시작 후 새로 남긴 문구가 100410 경보로 검색된다.'],['원상복구','실습 XML을 제거하고 Manager 실행 상태를 확인했다.']],[37,90]),
 p('examples/chapter04/investigation.txt에 확인 시각·원문·검색 조건·규칙 번호를 적는다. 문제가 있었다면 오류와 수정한 항목도 함께 남긴다.'),
 p('5장부터는 공격자 VM에서 웹 요청을 보내고, 같은 방식으로 원문과 경보를 대조한다. 1.12의 공격자 VM 준비 상태를 확인한다.'))
page('4장 참고 자료',
 h('[1] 로그 수집·전송'),
 {'type':'link','text':'Wazuh · Log data collection: How it works','url':'https://documentation.wazuh.com/current/user-manual/capabilities/log-data-collection/how-it-works.html'},
 h('[2] 수집 설정'),
 {'type':'link','text':'Wazuh · localfile','url':'https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/localfile.html'},
 h('[3] kt66 아카이브 활성화'),
 {'type':'link','text':'kt66 · siem/87-archives.sh · 63d4180','url':'https://github.com/mrgrit/kt66/blob/63d4180b1d6866de986ef263a3bd831d6082b5d5/siem/87-archives.sh'},
 h('[4] 규칙 시험'),
 {'type':'link','text':'Wazuh · Testing decoders and rules','url':'https://documentation.wazuh.com/current/user-manual/ruleset/testing.html'})
page('4장 참고 자료 · 계속',
 h('[5] 기본 SSH 규칙'),
 {'type':'link','text':'Wazuh 4.10.0 · 0095-sshd_rules.xml','url':'https://github.com/wazuh/wazuh/blob/v4.10.0/ruleset/rules/0095-sshd_rules.xml'},
 h('[6] 사용자 규칙과 구문'),
 {'type':'link','text':'Wazuh · Custom rules','url':'https://documentation.wazuh.com/current/user-manual/ruleset/rules/custom.html'},
 {'type':'link','text':'Wazuh · Rules syntax','url':'https://documentation.wazuh.com/current/user-manual/ruleset/ruleset-xml-syntax/rules.html'},
 h('[7] 경보 저장 기준'),
 {'type':'link','text':'Wazuh · alerts','url':'https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/alerts.html'})
page('4장 참고 자료 · 디코더',
 h('[8] SSH 디코더 정의와 구문'),
 {'type':'link','text':'Wazuh 4.10.0 · 0310-ssh_decoders.xml','url':'https://github.com/wazuh/wazuh/blob/v4.10.0/ruleset/decoders/0310-ssh_decoders.xml'},
 {'type':'link','text':'Wazuh · Decoders syntax','url':'https://documentation.wazuh.com/current/user-manual/ruleset/ruleset-xml-syntax/decoders.html'},
 {'type':'link','text':'Wazuh · Custom decoders','url':'https://documentation.wazuh.com/current/user-manual/ruleset/decoders/custom.html'},
 h('[9] logger 명령'),
 {'type':'link','text':'util-linux · logger(1)','url':'https://man7.org/linux/man-pages/man1/logger.1.html'})
if __name__=='__main__':
 data={'title':'로그 수집과 탐지 규칙','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','pages':pages}
 (ROOT/'manuscript/volume01-chapter04.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 out=ROOT/'examples/chapter04';out.mkdir(parents=True,exist_ok=True)
 for b in commands+queries:(out/(b['id']+'.txt')).write_text(b['text']+'\n')
 (out/'manifest.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
 (out/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2)+'\n')
 (out/'investigation.txt').write_text('원문 기록 시각과 시간대:\n원문:\nagent.name:\nlocation:\n아카이브 인덱스·문서 ID:\n시험 입력 파일:\n디코더·규칙·수준:\n사용자 규칙 파일·번호:\n적용 후 새 경보 시각:\n경보 인덱스·문서 ID:\n오류·수정 사항:\n규칙 삭제·재시작 확인:\n')
 print(len(pages),'pages',len(commands),'commands',len(queries),'queries')
