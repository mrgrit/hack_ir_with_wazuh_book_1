"""머리말·미리 안내·1장 신규 원고. 저자용이며 실습 명령을 실행하지 않는다."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COMMIT='63d4180b1d6866de986ef263a3bd831d6082b5d5'
pages=[]
commands=[]
def p(t): return {'type':'p','text':t}
def h(t): return {'type':'h','text':t}
def tab(head,rows,widths=None): return {'type':'table','head':head,'rows':rows,'widths':widths}
def img(path,caption,width=127): return {'type':'image','path':path,'caption':caption,'width_mm':width}
def spot(name,caption): return {'type':'image','path':f'assets/illustrations/chapter01/{name}.png','caption':caption,'width_mm':45,'align':'right'}
def shot(title,text): return {'type':'capture_slot','title':title,'text':text}
def code(t): return {'type':'code','text':t}
def c(text,why,result,where='kt66 VM · 터미널'):
    cid=f'C01-{len(commands)+1:02d}'
    b={'type':'command','id':cid,'text':text,'why':why,'result':result,'where':where}
    commands.append(b)
    return b

def page(title,*blocks,kind='body'):
    pages.append({'title':title,'kind':kind,'blocks':list(blocks)})

page('시스템 침투와\nSIEM 분석',p('해킹·침해대응 실무 with Wazuh · 1권'),p('머리말 · 미리 안내 · 1장'),p('2026.11.01'),kind='cover')
page('머리말',
    p('이 책은 공격을 실행하고, Wazuh에서 그 흔적을 찾는 실습서이다. 웹 요청, 로그인, 파일 변경을 직접 발생시킨 뒤 원본 기록과 경보를 대조한다.'),
    p('경보가 발생했다는 사실과 침투가 성공했다는 판단은 다르다. 무엇을 시도했고, 어디까지 실행되었으며, 어떤 증거가 남았는지를 확인한다.'),
    p('kt66은 공격 대상과 보안 도구를 함께 준비하는 실습 환경이다. 설치를 마치면 Wazuh와 각 서버를 따로 구축하지 않고 공격과 분석을 시작할 수 있다.'),
    img('assets/illustrations/overview.png','삽화. 공격 실습과 로그 분석.'),
    p('1권에서는 웹 공격과 Linux 시스템 침투를 다룬다. 독자는 명령을 입력하고, 결과를 읽고, 다음 확인 대상을 정한다.'))
page('미리 안내',
    p('Ubuntu·kt66·Wazuh를 처음 사용하는 독자를 기준으로 한다. 1권의 범위는 kt66·Wazuh 기본 운용과 Module 01 실습 01~30, 62이다.'),
    tab(['항목','기준'],[
        ['PC','Windows PC + VMware Workstation Pro'],
        ['가상머신','Ubuntu 22.04 LTS · x86_64'],
        ['할당 자원','메모리 16GB 이상 · 가상 디스크 200GB 이상'],
        ['네트워크','Bridged · Windows에서 VM 주소로 접속'],
        ['kt66','기준 커밋 63d4180'],
        ['Wazuh','기준 설정의 Manager·Indexer·Dashboard 4.10.0']],[32,95]),
    p('메모리와 디스크는 가상머신에 할당할 값이다. Windows가 사용할 자원과 스냅샷 저장 공간은 별도로 남긴다. 공격자 VM을 함께 실행할 때는 해당 VM의 자원도 확보한다.'),
    h('이미 설치된 환경이라면'),
    p('kt66이 준비된 VM을 받았다면 1.7의 실행 상태 확인부터 시작한다. 새로 설치할 때는 1.1부터 진행한다.'),
    h('입력과 확인'),
    p('명령 위에는 실행 위치와 번호를 적었다. 복사용 파일은 저장소의 examples/chapter01/에 있다. 실행 후에는 ‘확인’에 적힌 결과와 대조한다.'),
    p('주소 예시 192.168.0.189는 자신의 VM 주소로 바꾼다. 화면의 IP와 경보 건수는 실습 환경에 따라 다르다.'))
page('목차',
    tab(['장','내용'],[
        ['1','kt66 실습 환경 준비'],['2','공격과 보안관제의 기초'],['3','Wazuh 기본 운용'],['4','로그 수집과 탐지 규칙'],
        ['5','웹 공격의 시작과 입력값 검증 · 실습 01~03'],['6','웹 탐색과 인증 공격 · 04~06, 13~15'],['7','웹 서버 침투와 실행 흔적 · 07~12'],
        ['8','SSH 인증 공격과 계정·권한 조사 · 16~21'],['9','지속성 확보와 시스템 변경 탐지 · 22~28'],
        ['10','네트워크 흔적과 현재 상태 조사 · 29~30, 62'],['11','사건 재구성과 대응 판단'],['부록','명령·용어 · 환경 점검표 · 증거 기록 양식']],[14,113]),
    p('1권은 환경 준비 → 공격 실습 → 기록 분석 → 침해대응 순서로 진행한다.'))
page('1장의 진행 순서',
    img('assets/figures/chapter01/chapter-roadmap.png','도식 1-1. 1장 학습 순서.'))
page('1장  kt66 실습 환경 준비',
    h('1.1  무엇을 설치하는가'),
    p('조사할 대상은 웹 서버와 Ubuntu 시스템이다. kt66은 이 대상과 방화벽·침입방지·Wazuh를 함께 구성한다. SIEM(Security Information and Event Management)은 여러 시스템의 보안 기록을 모아 분석하는 시스템이다. Wazuh는 이 기록을 수집·분석하고 검색 화면을 제공한다.'),
    p('가상머신(VM)은 소프트웨어로 구성한 컴퓨터이다. VMware가 Windows 안에서 Ubuntu VM을 실행한다. kt66 VM에서는 Docker가 서비스를 컨테이너로 실행한다. 컨테이너는 운영체제의 핵심 부분인 커널을 호스트와 공유하면서 실행 중인 프로그램과 파일 환경을 분리한다.'),
    p('독자는 VM과 Ubuntu를 설치한다. kt66 설치 도구는 Docker·웹 서비스·Wazuh·호스트 센서를 준비한다. 호스트 센서는 Ubuntu의 활동을 기록하고 Wazuh에 전달하는 도구이다.'),
    img('assets/figures/chapter01/wazuh-flow.png','도식 1-2. Ubuntu 기록의 수집과 조회.'),
    p('설치 후에는 웹 접속, Wazuh 로그인, kt66-host의 연결 상태를 확인한다.'))
page('kt66과 공격자 VM의 네트워크',
    p('kt66 VM은 공격 대상과 Wazuh를 실행한다. 공격자 VM은 kt66으로 요청을 보내는 별도 Ubuntu 시스템이다. 두 VM의 네트워크 어댑터를 Bridged로 설정해 같은 실습망에 연결한다.'),
    img('assets/figures/chapter01/environment.png','도식 1-3. kt66과 공격자 VM의 브리지 연결.'),
    p('그림의 주소는 예시이다. 두 VM에는 서로 다른 IP를 사용한다. Windows 브라우저에서는 kt66의 웹과 Wazuh에 접속한다.'),
    p('공격자 VM은 5장의 첫 공격 실습에서 사용한다. 지금은 kt66 설치를 진행한다. 미리 준비하려면 1.12를 따른다.'))
page('1.2  VMware 가상머신 만들기',
    p('실행 위치는 Windows PC이다. 인터넷 연결과 VM용 메모리·디스크를 확보한다. 브리지는 VM을 PC와 같은 물리 네트워크에 연결한다. 취약 서비스가 노출되므로 실습용 네트워크에서 진행한다.'),
    p('① Broadcom 공식 다운로드 안내에서 Windows용 VMware Workstation Pro를 받는다. 설치 파일을 관리자 권한으로 실행하고 화면의 안내에 따라 설치한다. 재시작을 요구하면 Windows를 재시작한다. [1]'),
    p('② Ubuntu 배포 페이지에서 ubuntu-22.04.5-desktop-amd64.iso를 받는다. ISO는 운영체제 설치 디스크를 파일로 담은 형식이다. [2]'),
    p('③ VMware에서 File → New Virtual Machine → Typical을 선택한다. I will install the operating system later를 선택해 자동 설치를 건너뛴다.'),
    p('④ Linux → Ubuntu 64-bit를 선택한다. VM 이름은 kt66-book으로 정한다. 가상 디스크를 200GB 이상으로 만들고 마친다.'),
    p('⑤ Edit virtual machine settings에서 Memory를 16384MB 이상으로 지정한다. CD/DVD → Use ISO image file에서 받은 ISO를 연결한다.'),
    p('⑥ Network Adapter → Bridged를 선택하고 Connect at power on을 켠다. 설정을 저장한 뒤 메모리·디스크·ISO·네트워크 값을 다시 확인한다.'),
    shot('저자 촬영 1 · VMware 설정','Memory 16384MB, Hard Disk 200GB, ISO 파일명, Network Adapter의 Bridged 선택을 각 영역으로 나누어 촬영한다. 계정·개인 경로는 제외한다.'),
    p('VM이 켜지지 않으면 오류 문구 → Windows의 가상화 활성 상태 → VMware 호스트 요구사항 순서로 확인한다. 설치 전 설정을 잘못 지정했으면 VM을 끄고 해당 항목을 수정한다.'))
page('Ubuntu 설치하기',
    p('① Power on this virtual machine을 누른다. 부팅 메뉴에서 Try or Install Ubuntu, 설치 화면에서 Install Ubuntu를 선택한다.'),
    p('② 언어와 키보드를 선택한다. 이 원고는 Ubuntu Desktop 22.04의 설치 흐름을 기준으로 한다. 일반 설치(Normal installation)를 선택한다.'),
    p('③ Erase disk and install Ubuntu를 선택한다. 대상이 방금 만든 VM의 200GB 가상 디스크인지 확인한 뒤 Install Now를 누른다.'),
    p('④ 시간대는 Seoul, 컴퓨터 이름은 kt66-book, 사용자 이름은 ccc로 정한다. 암호는 직접 정한다. kt66의 호스트 감시 설정에 /home/ccc/.ssh가 들어 있으므로 이 책은 ccc 계정으로 맞춘다.'),
    p('⑤ 설치가 끝나면 Restart Now를 누른다. 설치 매체 제거 안내가 나오면 VM의 CD/DVD에서 ISO 연결을 해제하고 Enter를 누른다.'),
    p('⑥ ccc로 로그인해 바탕화면을 확인한다. Ctrl+Alt+T를 눌러 터미널을 연다. 여기서 입력하는 명령은 Ubuntu VM에서 실행된다.'),
    shot('저자 촬영 2 · Ubuntu 설치','가상 디스크 확인 화면과 ccc 계정 설정을 분할 촬영한다. 암호는 보이지 않게 한다. 설치 후 바탕화면·터미널도 별도 촬영한다.'),
    h('설치 전 상태 보존'),
    p('Ubuntu 메뉴에서 전원을 끈다. VMware의 VM → Snapshot → Take Snapshot을 선택하고 ubuntu-clean으로 저장한다. 스냅샷은 VM을 저장 시점으로 되돌리는 기능이다. 이후 kt66 설치 전체를 원복할 때 사용한다. 다시 VM을 켠다.'),
    spot('install-v2','삽화. 설치 준비.'))
page('1.3  운영체제·자원 확인',
    c('cat /etc/os-release','cat 파일은 파일 내용을 출력한다. /etc/os-release는 운영체제 정보를 담는다.','VERSION_ID="22.04"를 확인한다.'),
    c('uname -m','uname은 시스템 정보를 출력한다. -m은 하드웨어 아키텍처를 고른다.','x86_64가 출력되어야 한다.'),
    c('free -h','free는 메모리 사용량을 출력한다. -h는 GiB 등 읽기 쉬운 단위를 쓴다.','Mem 행의 total을 VMware 할당값과 대조한다. 16GB 할당은 예약 영역 때문에 조금 작게 보일 수 있다.'),
    c('df -h /','df 경로는 해당 경로가 속한 파일시스템의 용량을 출력한다. /는 루트 파일시스템이다. -h는 읽기 쉬운 단위이다.','Size와 Avail을 확인한다. 가상 디스크 200GB와 설치 후 남은 공간은 다른 값이다.'),
    p('값이 다르면 VM을 종료한 뒤 VMware 설정부터 확인한다. 운영체제나 아키텍처가 다르면 해당 ISO로 새 VM을 만든다.'))
page('VM 주소 확인하기',
    c('ip -4 -br address','ip address는 네트워크 인터페이스의 주소를 출력한다. -4는 IPv4만, -br은 요약 형식으로 표시한다.','ens33 등 실제 연결 인터페이스의 주소를 기록한다. lo의 127.0.0.1은 제외한다.'),
    p('출력이 192.168.0.189/24라면 브라우저에 쓸 주소는 192.168.0.189이다. /24는 네트워크 범위를 나타내는 접두 길이이며 주소창에는 넣지 않는다.'),
    c('ip route','ip route는 목적지별 통신 경로를 출력한다.','default 행의 dev 뒤에 있는 인터페이스를 확인한다. 더 구체적인 경로가 없는 목적지에는 이 경로를 사용한다.'),
    p('IPv4 주소가 없으면 VMware의 Bridged·Connected 설정을 확인한다. 네트워크가 여러 개라면 Edit → Virtual Network Editor에서 VMnet0의 연결 대상을 실제 사용 중인 어댑터로 지정한다.'),
    p('kt66은 10.20.30.0/24, 10.20.31.0/24, 10.20.32.0/24, 10.20.40.0/24, 10.20.50.0/24, 10.20.60.0/24, 10.20.70.0/24를 사용한다. 이 대역과 실습망·VPN 경로가 겹치면 설치 전에 네트워크를 조정한다.'),
    h('주소 유지'),
    p('DHCP는 주소를 자동 배정한다. 가능하면 실습망에서 VM의 DHCP 예약을 설정한다. DHCP 예약은 공유기나 DHCP 서버에서 설정한다. 주소가 바뀐 경우는 1.11에서 다룬다.'))
page('설치 도구 준비하기',
    p('Git은 kt66 코드를 받는 도구이다. curl·인증서·OpenSSL은 다운로드와 인증서 처리에, OpenSSH 클라이언트는 SSH 키 생성에, Python·PyYAML·jq는 설치 설정 처리에, GnuPG는 패키지 서명키 처리에, nano는 텍스트 편집에 쓴다. 다음 패키지는 독자가 Ubuntu에 설치한다.'),
    c('dpkg -s git curl openssl jq nano python3 \\\n  python3-yaml gnupg ca-certificates openssh-client','dpkg -s 패키지는 패키지의 설치 상태를 조회한다. -s는 상태 정보 출력 옵션이다. 줄 끝의 역슬래시(\\)는 다음 줄까지 한 명령으로 잇는다.','각 패키지의 Status: install ok installed를 확인한다. 미설치 패키지는 is not installed로 표시된다.'),
    c('sudo apt-get update','sudo 명령은 관리자 권한으로 실행한다. apt-get update는 패키지 목록을 갱신한다. sudo 암호 입력 중에는 글자가 표시되지 않는다.','저장소 목록 갱신이 끝나야 한다. 실패한 저장소가 있으면 설치보다 연결 문제를 먼저 해결한다.'),
    c('sudo apt-get install git curl ca-certificates openssl jq \\\n  nano python3 python3-yaml gnupg openssh-client','apt-get install 뒤에 설치할 패키지를 적는다. 줄 끝의 역슬래시(\\)는 다음 줄까지 한 명령으로 잇는다. 설치 목록을 읽고 Y로 진행한다.','오류 없이 마친 뒤 C01-07을 다시 실행해 각 패키지의 Status: install ok installed를 확인한다.'),
    p('apt-get은 시스템 패키지를 변경한다. 설치 전체를 취소하려면 1.10의 ubuntu-clean 스냅샷으로 돌아간다.'))
page('1.4  kt66 저장소 받기',
    c('cd ~','cd 경로는 작업 폴더를 바꾼다. ~는 현재 사용자의 홈이다.','이후 상대 경로는 홈 폴더를 기준으로 해석된다.'),
    c('pwd','pwd는 현재 폴더의 절대 경로를 출력한다.','ccc 계정이면 /home/ccc이다.'),
    c('ls -ld kt66','ls는 파일 목록을 출력한다. -l은 상세 정보, -d는 폴더 자체의 정보이다. 새 저장 위치가 비어 있는지 확인한다.','새 설치라면 No such file or directory가 나온다. 이미 있다면 기존 설치 여부부터 확인한다.'),
    c('git clone https://github.com/mrgrit/kt66.git','git clone 주소는 저장소와 변경 이력을 내려받는다. 홈에 kt66 폴더를 새로 만든다.','다운로드가 오류 없이 끝나야 한다.'),
    c('cd kt66','방금 받은 kt66 폴더로 이동한다.','pwd를 다시 실행하면 /home/ccc/kt66이어야 한다.'))
page('책의 코드 버전으로 맞추기',
    p('커밋은 Git이 기록한 코드의 한 시점이다. 이 책은 63d4180을 기준으로 한다. 이후 변경된 설치 절차가 섞이지 않게 받은 코드를 이 시점으로 맞춘다.'),
    c('git status --short','git status는 작업 파일의 변경 상태를 보여 준다. --short는 요약 표시이다.','새로 받은 저장소에서는 출력이 없어야 한다. 변경이 있으면 다음 명령 전에 원인을 확인한다.','kt66 VM · ~/kt66'),
    c('git checkout --detach 63d4180','git checkout 대상은 작업 파일을 해당 시점으로 바꾼다. --detach는 브랜치 대신 지정한 커밋을 직접 선택한다.','HEAD is now at 63d4180과 같은 안내가 나온다.','kt66 VM · ~/kt66'),
    c('git rev-parse --short=7 HEAD','rev-parse HEAD는 현재 커밋을 출력한다. --short=7은 앞 7자리로 표시한다.','63d4180인지 확인하고 git status --short도 다시 실행한다.','kt66 VM · ~/kt66'),
    p('이후 kt66 명령은 ~/kt66에서 실행한다.'),
    h('설정 파일'),
    p('.env는 kt66이 읽는 설정 파일이다. .env.example은 배포용 예시이다. 파일명 앞의 점은 Linux에서 숨김 파일로 다룬다는 뜻이다.'),
    img('assets/figures/chapter01/env-flow.png','도식 1-4. 설정 파일의 생성과 사용.'))
page('설정 파일 만들기',
    c('ls -l .env.example .env','복사할 원본과 대상의 존재 여부를 확인한다.','새 설치에서는 .env.example만 있고 .env는 없다. .env가 이미 있으면 복사하지 않는다.','kt66 VM · ~/kt66'),
    c('cp .env.example .env','cp 원본 대상은 파일을 복사한다. 여기서는 .env를 새로 만든다.','ls -l .env를 실행해 생성된 파일을 확인한다.','kt66 VM · ~/kt66'),
    c('chmod 600 .env','chmod 권한 파일은 접근 권한을 바꾼다. 600은 소유자에게 읽기·쓰기를 허용하고 나머지 사용자에게는 허용하지 않는다.','ls -l .env의 맨 앞이 -rw-------인지 확인한다.','kt66 VM · ~/kt66'),
    c('openssl rand -hex 32','openssl rand는 난수를 생성한다. -hex는 16진수 표시, 32는 난수의 바이트 수이다.','64자리 문자열을 다음 단계의 API_KEY 값으로 사용한다.','kt66 VM · ~/kt66'),
    p('API_KEY는 kt66 관리 기능의 제어 키이다. Wazuh 로그인 암호와는 별개이다. 출력값은 공개 저장소나 설치 기록표에 올리지 않는다.'))
page('필요한 설정만 바꾸기',
    c('nano .env','nano 파일은 텍스트 편집기를 연다. 기존 값을 읽은 뒤 아래 항목만 수정한다.','Ctrl+O → Enter로 저장하고 Ctrl+X로 닫는다.','kt66 VM · ~/kt66'),
    tab(['항목','입력'],[
        ['API_KEY','앞에서 생성한 64자리 문자열'],['SSH_USER','ccc'],['SSH_PASS','실습 컨테이너용 암호를 직접 지정'],['TZ','Asia/Seoul'],
        ['WEB_HOST_IP\nINT_HOST_IP','설치 도구가 VM 주소를 확인해 기록한다.']],[39,88]),
    p('SSH는 원격 시스템의 터미널에 접속하는 방식이다. SSH_USER·SSH_PASS는 실습 컨테이너의 계정이며 Ubuntu 로그인과 Wazuh 로그인은 별도이다.'),
    c("grep -E '^(SSH_USER|TZ)=' .env","grep 패턴 파일은 조건에 맞는 줄을 출력한다. 정규표현식은 문자열을 찾는 규칙이다. -E는 확장 정규표현식, ^는 줄 시작, (A|B)는 A 또는 B, =는 등호 문자이다. 작은따옴표는 규칙을 셸의 해석으로부터 보호한다.",'SSH_USER=ccc와 TZ=Asia/Seoul을 확인한다. 암호는 nano로 다시 열어 확인한다.','kt66 VM · ~/kt66'),
    p('WEB_HOST_IP가 미설정이면 ./kt66.sh up도 VM 주소를 감지해 .env에 기록한다. 이 책의 순서에서는 먼저 실행하는 install에서 주소를 확인하며, up은 그 값을 재사용한다.'))
page('1.5  인덱서의 메모리 매핑 한도',
    p('Wazuh Indexer는 분석 결과를 저장하고 검색한다. 메모리 매핑은 파일 등을 프로그램의 메모리 주소에 연결하는 기능이다. vm.max_map_count는 프로그램 하나가 사용할 매핑 영역 수의 상한이다. Wazuh는 262144 이상을 요구한다. [4]'),
    c('sysctl vm.max_map_count','sysctl 항목은 현재 커널 설정값을 조회한다.','262144 이상이면 이 절의 나머지 명령은 건너뛴다. 작으면 현재 값을 기록한다.'),
    c('ls -l /etc/sysctl.d/99-wazuh-book.conf','새 설정 파일이 이미 있는지 확인한다.','No such file or directory면 새로 만든다. 이미 있다면 nano에서 기존 내용을 먼저 읽고 보존한다.'),
    c('sudo nano /etc/sysctl.d/99-wazuh-book.conf','재부팅 후에도 사용할 설정을 관리자 권한으로 편집한다. 아래 한 줄을 입력하고 저장한다.','Ctrl+O → Enter → Ctrl+X로 마친다. cat /etc/sysctl.d/99-wazuh-book.conf로 다시 읽어 아래 한 줄과 대조한다.'),
    code('vm.max_map_count=262144'),
    c('sudo sysctl -p /etc/sysctl.d/99-wazuh-book.conf','-p 파일은 해당 파일의 커널 설정을 현재 시스템에 적용한다.','vm.max_map_count = 262144가 출력된다. C01-24를 다시 실행해 확인한다.'))
page('1.6  Docker 설치하기',
    p('Docker Engine은 컨테이너를 실행하고, Compose는 여러 컨테이너를 하나의 설정으로 관리한다. kt66의 install이 Docker를 설치하고 /etc/docker/daemon.json을 바꾼 뒤 Docker를 재시작한다. 새 실습 VM에서 실행한다.'),
    c('ls -l /etc/docker/daemon.json','설치 도구가 변경할 Docker 설정 파일을 먼저 확인한다.','새 VM에서는 파일이 없을 수 있다. 있으면 아래 명령으로 내용을 먼저 읽는다.'),
    c('sudo cat /etc/docker/daemon.json','기존 파일이 있을 때만 내용을 조회한다.','다른 용도의 Docker 설정이 있으면 새 전용 VM을 준비한다.'),
    c('./kt66.sh install','./는 현재 폴더, kt66.sh는 설치·운영 도구, install은 Docker 준비 단계이다. 필요할 때 sudo 암호를 요구한다.','아래 질문에 답하고 install 완료 문구를 확인한다.','kt66 VM · ~/kt66'),
    p('도메인은 IP 주소 대신 사용할 이름이다. netplan은 Ubuntu 네트워크 설정 도구이며 static은 고정 IP 설정을 뜻한다.'),
    tab(['질문','선택'],[
        ['웹 진입 IP','앞에서 기록한 VM 주소. 제안값이 맞을 때만 Enter'],['내부 실습 도메인','kt66.lab 입력 또는 기본값 수락'],['Windows 추가 설치','1권에서는 사용하지 않으므로 N을 선택한다.'],['netplan static 적용','N을 선택해 현재 DHCP 설정을 유지한다.']],[48,79]),
    p('설치 도구는 선택한 주소·도메인·Windows 설치 여부를 .env에 저장한다.'))
page('Docker와 저장된 주소 확인',
    c('sudo cat /etc/docker/daemon.json','설치 도구가 변경한 내용을 확인한다.','userland-proxy가 false인지, dns에 8.8.8.8·1.1.1.1이 있는지 읽는다. 실습망에서 외부 DNS가 차단되면 1.11을 확인한다.'),
    c('docker --version','Docker 프로그램의 버전을 확인한다. --version은 버전 출력 옵션이다.','Docker version과 버전 번호가 나온다.'),
    c('docker compose version','Compose 플러그인의 버전을 확인한다.','Docker Compose version과 버전 번호가 나온다.'),
    c('docker ps','docker ps는 실행 중인 컨테이너를 출력한다. Docker 데몬에 접근할 수 있는지도 확인한다.','아직 컨테이너가 없어도 표 머리글이 나오면 된다. permission denied면 아래 순서로 확인한다.'),
    p('Docker 그룹을 새로 부여받았다면 Ubuntu에서 로그아웃하고 다시 로그인한다. 터미널만 다시 여는 것으로는 그룹이 반영되지 않을 수 있다. 터미널에서 cd ~/kt66 후 docker ps를 다시 실행한다.'),
    p('다음 쪽에서 설치 도구가 저장한 값을 확인한다.'))
page('설정값을 골라 읽기',
    c("grep -E \\\n'^(WEB_HOST_IP|INT_HOST_IP|LAB_DOMAIN|WINDOWS_ENABLED)=' \\\n  .env",'grep 패턴 파일은 조건에 맞는 줄 전체를 출력한다. 이 명령은 .env에서 네 설정값을 읽는다.','아래 예시와 대조한다. 두 IP는 자신의 kt66 VM 주소이며, LAB_DOMAIN은 설치 중 선택한 이름이다.','kt66 VM · ~/kt66'),
    tab(['표기','뜻'],[
        ['-E','확장 정규표현식을 사용한다.'],
        ['작은따옴표','안의 내용을 하나의 패턴으로 전달한다.'],
        ['^','줄의 시작 위치이다.'],
        ['( )','네 설정 이름을 한 묶음으로 만든다.'],
        ['|','나열한 이름 중 하나와 일치한다.'],
        ['=','설정 이름 바로 뒤의 등호와 일치한다.'],
        ['.env','검색할 파일이다.']],[30,97]),
    p('줄 맨 앞에 네 이름 중 하나가 나오고 바로 뒤에 =가 있는 줄을 찾는다. #으로 시작하는 주석 줄은 제외된다.'),
    code('WEB_HOST_IP=192.168.0.189\nINT_HOST_IP=192.168.0.189\nLAB_DOMAIN=kt66.lab\nWINDOWS_ENABLED=no'),
    p('WEB_HOST_IP는 웹 접속 주소, INT_HOST_IP는 내부 서비스가 사용할 호스트 주소이다. 이 책에서는 둘 다 kt66 VM 주소를 쓴다. WINDOWS_ENABLED=no는 Windows VM 설치를 선택하지 않았다는 뜻이다.'))
page('1.7  kt66 기동하기',
    p('선행 조건은 Docker 접근 가능, .env 확인, 메모리 매핑 한도 충족이다. kt66 up은 이미지를 만들고 컨테이너를 실행한다. 이미지에는 프로그램과 실행에 필요한 파일이 담긴다.'),
    tab(['변경 대상','up이 수행하는 일'],[
        ['저장소 내부','인증서·키·서비스별 설정 파일 생성'],['Ubuntu','호스트 이름 매핑·실습 네트워크·시스템 서비스 구성'],['호스트 센서','Wazuh Agent·auditd·Sysmon·osquery 설치·설정']],[33,94]),
    p('Wazuh Agent는 Ubuntu의 기록을 보내는 수집기이다. 매니저는 받은 기록을 분석한다. auditd·Sysmon은 실행 등 시스템 활동을 기록하고, osquery는 시스템 정보를 SQL로 조회한다. 각 도구의 사용법은 해당 실습에서 다룬다.'),
    c('./kt66.sh up','일반 계정으로 시작하면 필요한 관리자 작업을 위해 sudo로 다시 실행한다. 최초 실행은 이미지 다운로드·빌드 시간이 필요하다.','up 완료 문구와 앞쪽 WARN·ERROR를 함께 읽는다. 센서 설치 실패는 경고만 남기고 계속될 수 있다.','kt66 VM · ~/kt66'),
    c('docker compose ps -a','Compose는 현재 폴더의 docker-compose.yaml을 읽는다. ps는 상태, -a는 종료된 컨테이너까지 표시한다.','fw·ips·web·siem·wazuh-indexer·wazuh-dashboard가 실행 중인지 확인한다.','kt66 VM · ~/kt66'),
    p('netglue·agent-observer-setup은 초기 작업 후 Exited (0)으로 끝날 수 있다. 0은 정상 종료 코드이다. 계속 실행되어야 할 서비스의 종료·재시작 반복은 로그를 확인한다.'))
page('1.8  웹과 Wazuh 접속',
    p('실행 위치는 Windows의 브라우저이다. 주소창에 자신의 VM 주소를 직접 입력한다. 콜론 뒤 숫자는 같은 시스템 안의 서비스를 구분하는 포트 번호이다.'),
    tab(['대상','주소 예시'],[['kt66 웹','http://192.168.0.189/'],['Wazuh','https://192.168.0.189:5601/']],[25,102]),
    img('assets/figures/chapter01/ports.png','도식 1-5. IP 주소와 서비스 포트.'),
    p('HTTP의 기본 포트 80은 주소에서 생략할 수 있다. Wazuh는 HTTPS의 기본 포트 443 대신 5601을 사용하므로 주소 끝에 :5601을 붙인다.'),
    p('Windows에서 localhost나 127.0.0.1을 입력하면 Windows 자신을 가리킨다. VM 접속에는 Ubuntu에서 확인한 주소를 쓴다.'),
    spot('notes-v2','삽화. 접속 주소 확인.'))
page('웹 첫 화면 열기',
    p('① 웹 주소를 연다. kt66 실습 환경이라는 제목이 표시되는지 확인한다.'),
    img('assets/screens/chapter01/web.png','화면 1-1. kt66 웹 첫 화면.'),
    p('② Wazuh 주소를 연다. 5601은 HTTPS이다. kt66의 일부 안내 문구에 HTTP로 표시되어 있어도 HTTPS로 접속한다.'),
    p('③ 인증서 경고가 나오면 주소가 자신의 VM인지 확인한다. 고급 또는 상세 항목을 열어 해당 사이트로 계속 진행한다. 이 실습은 브라우저가 기본 신뢰하지 않는 자체 인증서를 사용한다.'),
    p('로그인 화면이 표시되면 다음 쪽의 계정을 입력한다.'))
page('Wazuh 로그인',
    p('로그인 화면에서 다음 데모 계정을 입력하고 Log in을 누른다. 기존 환경에서 암호를 변경했다면 변경된 값을 쓴다.'),
    tab(['항목','데모 기본값'],[['Username','admin'],['Password','SecretPassword']],[32,95]),
    img('assets/screens/chapter01/login.png','화면 1-2. Wazuh 로그인 화면.',110),
    p('Overview가 열리면 1.9에서 에이전트 연결 상태를 확인한다.'))
page('1.9  호스트 센서 확인',
    p('선행 조건은 kt66 기동과 Wazuh 로그인이다. 먼저 Ubuntu에서 수집 서비스가 실행 중인지 확인한다.'),
    c('systemctl is-active wazuh-agent','systemctl은 Linux 서비스를 관리한다. is-active 이름은 서비스의 현재 실행 상태를 출력한다.','active이면 실행 중이다. inactive·failed·unknown이면 1.11의 센서 점검으로 이동한다.'),
    c('systemctl is-active osqueryd','osqueryd는 kt66이 설치하는 osquery의 상시 실행 서비스이다.','active인지 확인한다.'),
    p('Windows 브라우저로 돌아간다. Overview의 AGENTS SUMMARY에서 Active를 눌러 에이전트 목록을 연다.'),
    img('assets/screens/chapter01/home.png','화면 1-3. Wazuh 에이전트 연결 현황.'))
page('에이전트 연결 확인',
    p('목록에서 kt66-host를 찾아 이름을 클릭한다. 이 이름은 설치 도구가 등록하는 수집기 이름이며 Ubuntu 컴퓨터 이름 kt66-book과 다르다.'),
    img('assets/screens/chapter01/agents.png','화면 1-4. kt66-host 연결 상태.'),
    p('상세 화면의 Status 점에 마우스를 올려 active인지 확인한다. active는 매니저와 연결된 상태이다. 특정 로그가 실제로 수집되고 검색되는지는 3장에서 확인한다.'),
    tab(['완료 조건','직접 기록'],[
        ['kt66 커밋 63d4180',''],['VM 주소와 .env 주소 일치',''],['주요 컨테이너 실행 중',''],['웹 제목 표시',''],['Wazuh 로그인 성공',''],['wazuh-agent·osqueryd active',''],['목록의 kt66-host active','']],[83,44]),
    p('표의 항목을 모두 확인하면 설치가 끝난다. 실패한 항목은 1.11의 해결 절차를 따른다.'))
page('1.10  중지·재기동·원복',
    p('실습을 멈추기 전에 현재 컨테이너를 확인한다. Docker 볼륨은 컨테이너와 별도로 데이터를 보관하는 공간이다.'),
    c('docker compose ps -a','중지할 Compose 서비스 목록을 확인한다.','현재 kt66 서비스인지 이름과 상태를 읽는다.','kt66 VM · ~/kt66'),
    c('./kt66.sh down','kt66 컨테이너와 Compose 네트워크를 제거한다. 데이터 볼륨은 보존한다.','C01-40을 다시 실행해 남은 컨테이너가 없는지 확인한다.','kt66 VM · ~/kt66'),
    p('호스트 센서와 Ubuntu 네트워크 설정은 유지된다. VM을 끌 때는 Ubuntu 메뉴의 전원 끄기로 정상 종료한다.'),
    img('assets/figures/chapter01/lifecycle.png','도식 1-6. 컨테이너 중지와 재기동.'),
    h('다음 실습을 위한 보존'),
    p('설치를 마친 VM을 종료한 뒤 VMware에서 kt66-ready 스냅샷을 만든다. 다음에는 VM을 켜고 터미널에서 cd ~/kt66 → ./kt66.sh up을 한 명령씩 실행한다. 주소·컨테이너·로그인·센서 상태를 다시 확인한다.'),
    h('변경 전체 원복'),
    p('VM을 종료하고 VMware의 VM → Snapshot → Snapshot Manager를 연다. 설치 전으로 돌아가려면 ubuntu-clean, 정상 설치 상태로 돌아가려면 kt66-ready를 선택해 Go To를 누른다. 선택 시점 이후의 VM 변경은 사라진다.'),
    p('복원 후 VM을 켜고 1.3의 주소부터 확인한다. kt66-ready를 복원했다면 1.7~1.9를 다시 확인한다.'))
page('1.11  설치가 멈췄을 때',
    tab(['증상','확인 순서'],[
        ['다운로드 실패','실패한 주소·오류 문구 → VM 네트워크 → DNS → 저장소 연결. Docker만 실패하면 daemon.json의 dns 확인'],
        ['no space left','df -h /의 Avail → VM 디스크 용량 → 보관한 데이터'],
        ['docker 권한 거부','로그아웃·재로그인 → 현재 그룹 → Docker 접근'],
        ['Compose 없음','install의 Docker 설치 오류 → Compose 설치 상태']],[38,89]),
    c('getent hosts github.com','getent hosts 이름은 시스템의 이름 해석 결과를 조회한다.','IP가 나오면 이름 해석 결과를 얻은 것이다. 나오지 않으면 DNS부터 확인한다.'),
    c('curl -I --max-time 15 https://github.com','curl 주소는 서버에 요청한다. -I는 응답 헤더만 받고 --max-time 15는 최대 15초로 제한한다.','HTTP 응답 코드가 나오면 서버 응답을 받은 것이다. 오류 문구로 이름 해석·연결·인증서 문제를 나눈다.'),
    c('id -nG','id는 사용자 정보를 출력한다. -G는 소속 그룹 목록, -n은 번호 대신 이름이다.','docker 그룹이 있는지 확인한다. 없다면 다음 명령을 실행한다.'),
    c('sudo usermod -aG docker "$USER"','usermod는 계정 설정을 바꾼다. -aG는 기존 그룹을 유지하며 docker 그룹을 추가한다. $USER는 현재 계정이며 큰따옴표로 하나의 인자로 묶는다.','로그아웃·재로그인 후 id -nG와 docker ps를 다시 확인한다.'))
page('화면이 열리지 않을 때',
    p('① VM 주소와 .env 주소를 비교한다. ② VMware 브리지 연결을 확인한다. ③ 웹은 HTTP, Wazuh는 HTTPS:5601인지 확인한다. ④ 컨테이너 상태를 보고 해당 로그를 읽는다.'),
    c('docker compose logs --tail 50 wazuh-dashboard','logs 서비스는 해당 서비스 로그를 읽는다. --tail 50은 마지막 50줄로 제한한다.','로그의 연결·인증·초기화 오류를 확인한다.','kt66 VM · ~/kt66'),
    c('docker compose logs --tail 50 wazuh-indexer','저장·검색 서비스의 최근 로그를 읽는다.','vm.max_map_count 오류는 1.5, 메모리·디스크 오류는 1.3의 값과 대조한다.','kt66 VM · ~/kt66'),
    p('server is not ready yet가 계속 표시되면 인덱서 로그에서 초기화 오류를 확인한다.'),
    h('VM 주소가 바뀐 경우'),
    p('ip -4 -br address와 C01-35로 두 주소를 비교한다. nano .env에서 WEB_HOST_IP·INT_HOST_IP를 현재 VM 주소로 수정하고 저장한다. C01-35로 다시 읽은 뒤 ./kt66.sh up으로 적용한다. 브라우저도 새 주소로 접속한다.'),
    p('기존 주소가 .env에 남아 있으면 up이 새 DHCP 주소로 자동 교체하지 않는다. 수정 전 두 값을 기록해 두면 잘못 입력했을 때 되돌릴 수 있다.'),
    img('assets/figures/chapter01/troubleshooting.png','도식 1-7. 접속 문제 확인 순서.'))
page('센서가 연결되지 않을 때',
    c('sudo systemctl status wazuh-agent --no-pager','status는 서비스 상세 상태를 출력한다. --no-pager는 별도 페이지 뷰어를 열지 않는다.','Active 줄과 최근 오류를 확인한다. 서비스가 정지 상태면 명령 종료 코드가 0이 아닐 수 있다.'),
    c('sudo journalctl -u wazuh-agent -n 50 --no-pager','journalctl은 시스템 저널을 읽는다. -u는 서비스, -n 50은 마지막 50개 항목이다.','매니저 연결·등록·버전 관련 메시지를 확인한다.'),
    c('docker compose logs --tail 50 siem','siem은 kt66의 Wazuh Manager 서비스이다. 에이전트가 보내는 기록을 분석한다.','매니저가 시작되었는지, 등록 오류가 있는지 확인한다.','kt66 VM · ~/kt66'),
    p('wazuh-agent나 osqueryd가 없으면 up 출력의 host-sensors 실패 지점을 확인한다. 패키지 다운로드 오류를 해결한 뒤 기존 센서 상태를 기록하고 아래 명령을 실행한다.'),
    c('sudo ./deployment/host-sensors.sh','호스트 센서를 설치·재설정한다. /var/ossec/etc/ossec.conf, auditd·Sysmon·osquery 설정과 관련 서비스를 변경한다.','C01-38·39와 Wazuh 목록을 다시 확인한다. 전체 변경을 취소하려면 ubuntu-clean 스냅샷을 복원한다.','kt66 VM · ~/kt66'))
page('1.12  공격자 VM 사전 준비',
    p('공격자 VM은 5장부터 필요하다. 저자가 테스트한 Ubuntu 22.04 Live Server를 사용한다. kt66과 같은 PC의 VMware에 별도 VM을 만든다.'),
    tab(['항목','설정'],[
        ['이름','attacker'],['설치 ISO','ubuntu-22.04.5-live-server-amd64.iso'],
        ['자원 예시','CPU 2개 · 메모리 2GB · 디스크 25GB'],
        ['네트워크','Bridged · kt66과 같은 어댑터 연결']],[30,97]),
    p('공격 도구만 실행하므로 kt66보다 적은 자원으로 구성한다. 위 자원은 시작 예시이며 도구 실행량에 따라 조정한다.'),
    p('① 1.2의 VMware 생성 순서에서 이름·ISO·자원을 위 표로 바꾼다. VM을 켜고 Try or Install Ubuntu Server를 선택한다.'),
    p('② 언어·키보드를 선택하고 Ubuntu Server로 진행한다. Network connections에서 DHCP로 받은 IPv4 주소를 확인한다. 프록시는 사용 중인 경우만 입력하고 기본 미러 주소로 진행한다.'),
    p('③ 저장 장치에서 새 VM의 가상 디스크를 선택한다. 설치 확인 후 서버 이름은 attacker, 사용자 이름은 ccc로 정한다. 암호는 직접 정한다. 추가 패키지 선택은 건너뛰고 설치를 마친다.'),
    p('④ ISO 연결을 해제하고 재부팅한다. VMware 콘솔에서 ccc로 로그인한다. Server는 로그인 후 터미널을 바로 표시한다.'),
    p('⑤ cat /etc/os-release로 22.04를, ip -4 -br address로 주소를 확인한다. kt66과 같은 대역의 서로 다른 IP여야 한다. 주소가 없으면 Bridged·Connected와 DHCP 연결을 확인한다.'),
    p('VM을 종료하고 VMware에서 attacker-clean 스냅샷을 만든다. 다시 켜서 다음 쪽의 도구를 설치한다. 설치를 취소하려면 이 스냅샷을 복원한다.'))
page('공격 도구 일괄 설치',
    p('실행 위치는 공격자 VM이다. 인터넷 연결을 확인한 뒤 아래 도구를 한 번에 설치한다. 각 도구의 옵션과 사용법은 해당 공격 실습에서 설명한다. 설치 전 상태는 다음 쪽의 C01-53으로 확인할 수 있다.'),
    tab(['도구','역할'],[
        ['nmap','호스트·포트 탐색'],['hydra · sshpass','인증 시도·SSH 암호 전달'],
        ['sqlmap','SQL 삽입 점검'],['nikto','웹 서버 취약점 점검'],
        ['dirb · gobuster','웹 경로 탐색'],['curl · netcat-openbsd','HTTP 요청·TCP/UDP 통신'],
        ['python3 · python3-requests','Python 실행·HTTP 요청 코드']],[53,74]),
    c('sudo apt update && sudo apt install -y \\\n  nmap hydra sqlmap nikto dirb gobuster curl \\\n  netcat-openbsd python3 python3-requests sshpass',
      'apt update는 패키지 목록을 갱신한다. &&는 앞 명령이 성공한 경우에만 뒤 명령을 실행한다. apt install은 패키지를 설치하며 -y는 설치 확인에 자동으로 동의한다. 줄 끝의 역슬래시는 다음 줄을 잇는다.',
      '오류 없이 끝나면 다음 쪽에서 패키지 상태와 kt66 연결을 확인한다.','공격자 VM · 터미널'))
page('공격자 VM 준비 확인',
    c('dpkg -s nmap hydra sqlmap nikto dirb gobuster curl \\\n  netcat-openbsd python3 python3-requests sshpass',
      '앞에서 설치한 패키지의 상태를 조회한다.',
      '각 패키지에 Status: install ok installed가 있어야 한다.','공격자 VM · 터미널'),
    c('curl -I --max-time 15 http://192.168.0.189/',
      '주소를 자신의 kt66 VM 주소로 바꾼다. -I는 HTTP 응답 헤더를 요청하고 --max-time 15는 실행 시간을 15초로 제한한다.',
      'HTTP 응답 코드가 표시되면 kt66 웹 서버에 연결된 것이다.','공격자 VM · 터미널'),
    p('패키지 설치가 실패하면 오류 문구 → 인터넷 연결 → 패키지 미러 순서로 확인한다. kt66 연결이 실패하면 두 VM의 IP → VMware 브리지 연결 → kt66 기동 상태 순서로 확인한다.'),
    p('확인을 마치면 VM을 종료하고 attacker-ready 스냅샷을 만든다. 이후 실습 변경을 되돌릴 때 이 스냅샷을 사용한다.'),
    p('공격에 사용할 계정 목록·암호 목록, 웹 이름 설정과 시각 동기화는 5장에서 준비한다.'),
    spot('network-v2','삽화. 연결 점검.'))
page('1장 참고 자료',
    p('kt66 코드 기준: 63d4180. 설치·기동은 kt66.sh, 서비스·포트·버전은 docker-compose.yaml, HTTPS는 wazuh-config/opensearch_dashboards.yml, 호스트 센서는 deployment/host-sensors.sh와 대조했다.'),
    h('[1] VMware Workstation 설치'),
    p('Broadcom, Installing VMware Workstation Pro. 설치 파일 다운로드와 Windows 설치 순서.'),
    {'type':'link','text':'공식 설치 안내','url':'https://knowledge.broadcom.com/external/article/387947/installing-vmware-workstation-pro.html'},
    h('[2] Ubuntu 22.04.5 LTS'),
    {'type':'link','text':'Ubuntu 공식 ISO 배포','url':'https://releases.ubuntu.com/22.04/'},
    h('[3] kt66 기준 소스'),
    {'type':'link','text':'kt66 · 기준 커밋 63d4180','url':'https://github.com/mrgrit/kt66/tree/'+COMMIT},
    p('설치 코드의 기준 버전은 63d4180이다.'))
page('1장 참고 자료 · 계속',
    h('[4] Wazuh Docker 요구사항'),
    {'type':'link','text':'Wazuh Docker deployment · 메모리 매핑 한도','url':'https://documentation.wazuh.com/current/deployment-options/docker/wazuh-container.html'},
    h('[5] 공격자 VM 도구 구성'),
    {'type':'link','text':'강의 자료 · 강사 준비 · 공격자 VM','url':'https://github.com/mrgrit/hack_ir_with_wazuh/blob/main/docs/강사_준비.md'},
    {'type':'link','text':'Ubuntu Server 공식 설치 안내','url':'https://ubuntu.com/server/docs/tutorial/basic-installation/'} )

if __name__=='__main__':
    data={'title':'시스템 침투와 SIEM 분석','series':'해킹·침해대응 실무 with Wazuh','baseline':COMMIT,'pages':pages}
    (ROOT/'manuscript/volume01-chapter01.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    out=ROOT/'examples/chapter01'; out.mkdir(parents=True,exist_ok=True)
    for cmd in commands:
        (out/(cmd['id']+'.txt')).write_text(cmd['text']+'\n')
    (out/'manifest.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
    print(len(pages),'pages',len(commands),'commands')
