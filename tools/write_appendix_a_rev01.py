"""REV01 · 부록 A 설치 상세와 문제 해결. 1장 REV01에서 옮긴 화면 순서와 확인 절차."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/REV01'
EX=ROOT/'examples/rev01/appendix-a'
COMMIT='63d4180b1d6866de986ef263a3bd831d6082b5d5'
pages=[];commands=[]

def p(t): return {'type':'p','text':t}
def h(t): return {'type':'h','text':t}
def ol(*items): return {'type':'list','style':'number','items':list(items)}
def tab(head,rows,widths=None): return {'type':'table','head':head,'rows':rows,'widths':widths}
def img(path,caption,width=127): return {'type':'image','path':path,'caption':caption,'width_mm':width}
def shot(title,text): return {'type':'capture_slot','title':title,'text':text}
def link(text,url): return {'type':'link','text':text,'url':url}
def c(text,purpose,syntax,result,where='kt66 VM · 터미널'):
    b={'type':'command','id':f'CA-{len(commands)+1:02d}','where':where,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    commands.append(b);return b
def page(title,*blocks,brk=True,level='page'):
    pg={'title':title,'kind':'body','blocks':list(blocks)}
    if not brk:pg['break']=False
    if level!='page':pg['level']=level
    pages.append(pg)
def section(title,*blocks):page(title,*blocks,brk=False,level='section')

page('부록 A  설치 상세와 문제 해결',
    p('1장에서 값만 제시한 설치 단계를 화면 순서대로 설명한다. 결과가 기대와 다를 때는 증상에 맞는 절을 찾아 확인 순서를 따른다.'),
    tab(['절','내용','관련 절'],[
        ['A.1','VMware 가상머신 만들기','1.3'],
        ['A.2','Ubuntu 설치하기','1.3'],
        ['A.3','공격자 VM 설치하기','1.9'],
        ['A.4','설치가 멈췄을 때','1.3~1.5'],
        ['A.5','화면이 열리지 않을 때','1.6'],
        ['A.6','수집기가 연결되지 않을 때','1.7']],[16,76,35]))

section('A.1  VMware 가상머신 만들기',
    p('실행 위치는 Windows PC이다. 인터넷 연결과 VM에 할당할 메모리·디스크를 확보한다.'),
    ol('Broadcom 공식 다운로드 안내에서 Windows용 VMware Workstation Pro를 받는다. 설치 파일을 관리자 권한으로 실행하고 화면의 안내에 따라 설치한다. 재시작을 요구하면 Windows를 재시작한다. [A1]',
       'Ubuntu 배포 페이지에서 ubuntu-22.04.5-desktop-amd64.iso를 받는다. ISO는 운영체제 설치 디스크를 파일로 담은 형식이다. [A2]',
       'VMware에서 **File → New Virtual Machine → Typical**을 선택한다. **I will install the operating system later**를 선택해 자동 설치를 건너뛴다.',
       '**Linux → Ubuntu 64-bit**를 선택한다. VM 이름은 kt66-book으로 정한다. 가상 디스크를 200GB 이상으로 만들고 마친다.',
       '**Edit virtual machine settings**에서 **Memory**를 16384MB 이상으로 지정한다. **CD/DVD → Use ISO image file**에서 받은 ISO를 연결한다.',
       '**Network Adapter → Bridged**를 선택하고 **Connect at power on**을 켠다. 설정을 저장한 뒤 메모리·디스크·ISO·네트워크 값을 다시 확인한다.'),
    shot('저자 촬영 1 · VMware 설정','Memory 16384MB, Hard Disk 200GB, ISO 파일명, Network Adapter의 Bridged 선택을 각 영역으로 나누어 촬영한다. 계정·개인 경로는 제외한다.'),
    h('VM이 켜지지 않거나 주소가 없을 때'),
    p('VM이 켜지지 않으면 오류 문구, Windows의 가상화 활성 상태, VMware 호스트 요구사항 순서로 확인한다. 설치 전에 설정을 잘못 지정했으면 VM을 끄고 해당 항목을 고친다.'),
    p('Ubuntu에서 IPv4 주소가 없으면 VMware의 Network Adapter가 Bridged이고 Connected인지 확인한다. PC에 네트워크 어댑터가 여러 개라면 **Edit → Virtual Network Editor**에서 VMnet0의 연결 대상을 실제로 쓰는 어댑터로 지정한다.'))

section('A.2  Ubuntu 설치하기',
    ol('**Power on this virtual machine**을 누른다. 부팅 메뉴에서 **Try or Install Ubuntu**, 설치 화면에서 **Install Ubuntu**를 선택한다.',
       '언어와 키보드를 선택한다. 설치 방식은 일반 설치(**Normal installation**)를 선택한다.',
       '**Erase disk and install Ubuntu**를 선택한다. 대상이 방금 만든 VM의 200GB 가상 디스크인지 확인한 뒤 **Install Now**를 누른다.',
       '시간대는 Seoul, 컴퓨터 이름은 kt66-book, 사용자 이름은 ccc로 정한다. 암호는 직접 정한다.',
       '설치가 끝나면 **Restart Now**를 누른다. 설치 매체를 제거하라는 안내가 나오면 VM의 CD/DVD에서 ISO 연결을 해제하고 Enter를 누른다.',
       'ccc로 로그인해 바탕화면을 확인한다. Ctrl+Alt+T를 눌러 터미널을 연다.'),
    shot('저자 촬영 2 · Ubuntu 설치','가상 디스크 확인 화면과 ccc 계정 설정을 나누어 촬영한다. 암호는 보이지 않게 한다. 설치 후 바탕화면·터미널도 따로 촬영한다.'),
    p('설치를 마치면 1.3의 ‘설치 전 상태 보존’에 따라 ubuntu-clean 스냅샷을 만든다.'))

section('A.3  공격자 VM 설치하기',
    p('실행 위치는 Windows PC이다. 1.9의 표에 있는 값으로 만든다.'),
    ol('A.1의 순서에서 VM 이름·ISO·자원을 1.9의 표로 바꾸어 VM을 만든다. ISO는 Ubuntu 배포 페이지의 ubuntu-22.04.5-live-server-amd64.iso이다. [A2]',
       'VM을 켜고 **Try or Install Ubuntu Server**를 선택한다.',
       '언어와 키보드를 선택하고 Ubuntu Server로 진행한다. **Network connections**에서 DHCP로 받은 IPv4 주소를 확인한다. 프록시는 쓰는 경우에만 입력하고 기본 미러 주소로 진행한다. [A3]',
       '저장 장치에서 새 VM의 가상 디스크를 선택한다. 설치를 확인한 뒤 서버 이름은 attacker, 사용자 이름은 ccc로 정하고 암호는 직접 정한다. 추가 패키지 선택은 건너뛰고 설치를 마친다.',
       'ISO 연결을 해제하고 재부팅한다. VMware 콘솔에서 ccc로 로그인하면 바로 터미널이 표시된다.'),
    c('cat /etc/os-release\nip -4 -br address',
      '설치한 Ubuntu 버전과 공격자 VM의 주소를 확인한다.',
      '1장의 C01-01·C01-03과 같은 명령이다.',
      'VERSION_ID="22.04"이고, kt66과 같은 대역의 서로 다른 IPv4 주소가 있다. 주소가 없으면 Bridged·Connected 설정과 DHCP 연결을 확인한다.',
      where='공격자 VM · 터미널'),
    p('확인을 마치면 VM을 끄고 VMware에서 attacker-clean 스냅샷을 만든다. 도구 설치는 1.9로 돌아가 진행한다. 도구 목록은 강의 자료의 공격자 VM 준비 절차를 따른다. [A4]'))

section('A.4  설치가 멈췄을 때',
    tab(['증상','확인 순서'],[
        ['다운로드 실패','실패한 주소·오류 문구, VM 네트워크, DNS, 저장소 연결 순서로 확인한다. Docker만 실패하면 daemon.json의 dns를 확인한다.'],
        ['no space left','df -h /의 Avail, VM 디스크 용량, 보관한 데이터 순서로 확인한다.'],
        ['docker 권한 거부','로그아웃·재로그인, 현재 그룹, Docker 접근 순서로 확인한다.'],
        ['Compose 없음','install 출력의 Docker 설치 오류와 Compose 설치 상태를 확인한다.']],[35,92]),
    c('getent hosts github.com\ncurl -I --max-time 15 https://github.com',
      '이름 해석과 외부 HTTPS 연결을 나누어 확인한다.',
      'getent hosts 이름은 시스템의 이름 해석 결과를 조회한다. curl -I는 응답 헤더만 요청하고 --max-time 15는 최대 15초까지만 기다린다.',
      '첫 줄이 IP를 출력하면 이름 해석은 정상이다. 둘째 줄에 HTTP 응답 코드가 나오면 서버 연결도 정상이다. 오류 문구로 이름 해석·연결·인증서 가운데 어디가 문제인지 나눈다.'),
    c('id -nG',
      '현재 계정이 docker 그룹에 속하는지 확인한다.',
      'id는 사용자 정보를 출력한다. -G는 소속 그룹 목록을, -n은 번호 대신 이름을 표시한다.',
      'docker가 목록에 있으면 그룹은 정상이다. 없으면 CA-04를 실행한다.'),
    c('sudo usermod -aG docker "$USER"',
      '현재 계정을 docker 그룹에 추가한다.',
      'usermod는 계정 설정을 바꾼다. -aG는 기존 그룹을 유지하면서 지정한 그룹을 추가한다. $USER는 현재 계정 이름이며 큰따옴표로 하나의 인자로 묶는다.',
      '로그아웃·재로그인 후 CA-03과 docker ps를 다시 실행해 확인한다.'))

section('A.5  화면이 열리지 않을 때',
    img('assets/figures/chapter01/troubleshooting.png','도식 A-1. 접속 문제 확인 순서.'),
    p('VM 주소와 .env의 주소, VMware 브리지 연결, 웹은 HTTP·Wazuh는 HTTPS:5601인지, 컨테이너 상태 순서로 확인한다. 컨테이너가 실행 중인데 화면이 열리지 않으면 해당 서비스의 로그를 읽는다.'),
    c('docker compose logs --tail 50 wazuh-dashboard\ndocker compose logs --tail 50 wazuh-indexer',
      '검색 화면과 저장·검색 서비스의 최근 로그를 읽는다.',
      'logs 서비스는 그 서비스의 로그를 출력하며 --tail 50은 마지막 50줄로 제한한다.',
      '연결·인증·초기화 오류를 찾는다. vm.max_map_count 오류는 1.5, 메모리·디스크 오류는 1.3의 값과 대조한다. server is not ready yet가 계속 표시되면 인덱서 로그에서 초기화 오류를 확인한다.',
      where='kt66 VM · ~/kt66'),
    h('VM 주소가 바뀐 경우'),
    p('C01-03과 C01-19로 현재 VM 주소와 .env의 주소를 비교한다. 다르면 nano .env에서 WEB_HOST_IP·INT_HOST_IP를 현재 VM 주소로 고치고 저장한다. C01-19로 다시 읽은 뒤 ./kt66.sh up으로 적용하고 브라우저도 새 주소로 접속한다.'),
    p('기존 주소가 .env에 남아 있으면 up은 새 DHCP 주소로 자동 교체하지 않는다. 고치기 전의 두 값을 적어 두면 잘못 입력했을 때 되돌릴 수 있다.'))

section('A.6  수집기가 연결되지 않을 때',
    c('sudo systemctl status wazuh-agent --no-pager\nsudo journalctl -u wazuh-agent -n 50 --no-pager',
      '수집기 서비스의 상세 상태와 최근 기록을 읽는다.',
      'systemctl status는 서비스의 상세 상태를 출력하며 --no-pager는 별도 페이지 뷰어 없이 바로 출력한다. journalctl은 시스템 저널을 읽으며 -u는 서비스, -n 50은 마지막 50개 항목이다.',
      'Active 줄과 최근 오류를 읽고 매니저 연결·등록·버전 관련 메시지를 찾는다. 서비스가 정지 상태면 첫 줄의 종료 코드가 0이 아닐 수 있다.'),
    c('docker compose logs --tail 50 siem',
      '수집기가 기록을 보내는 Wazuh Manager의 상태를 읽는다.',
      'siem은 kt66의 Wazuh Manager 서비스 이름이다.',
      '매니저가 시작되었는지, 등록 오류가 있는지 확인한다.',
      where='kt66 VM · ~/kt66'),
    p('wazuh-agent나 osqueryd가 없으면 1.6의 up 출력에서 host-sensors 실패 지점을 찾는다. 패키지 다운로드 오류를 해결한 뒤 현재 센서 상태를 적어 두고 다음 명령을 실행한다.'),
    c('sudo ./deployment/host-sensors.sh',
      '호스트 센서를 다시 설치하고 설정한다.',
      '/var/ossec/etc/ossec.conf, auditd·Sysmon·osquery 설정과 관련 서비스를 바꾼다.',
      'C01-22와 Wazuh의 에이전트 목록을 다시 확인한다. 전체 변경을 취소하려면 ubuntu-clean 스냅샷으로 돌아간다.',
      where='kt66 VM · ~/kt66'))

section('부록 A 참고 자료',
    h('[A1] VMware Workstation 설치'),
    p('Broadcom, Installing VMware Workstation Pro. 설치 파일 다운로드와 Windows 설치 순서.'),
    link('공식 설치 안내','https://knowledge.broadcom.com/external/article/387947/installing-vmware-workstation-pro.html'),
    h('[A2] Ubuntu 22.04.5 LTS'),
    link('Ubuntu 공식 ISO 배포','https://releases.ubuntu.com/22.04/'),
    h('[A3] Ubuntu Server 설치'),
    link('Ubuntu Server 공식 설치 안내','https://ubuntu.com/server/docs/tutorial/basic-installation/'),
    h('[A4] 공격자 VM 도구 구성'),
    link('강의 자료 · 강사 준비 · 공격자 VM','https://github.com/mrgrit/hack_ir_with_wazuh/blob/main/docs/강사_준비.md'))

if __name__=='__main__':
    data={'title':'시스템 침투와 SIEM 분석','series':'해킹·침해대응 실무 with Wazuh','baseline':COMMIT,'revision':'REV01',
          'comments':'REV01 부록 A. 1장 원고에서 옮긴 설치 화면 순서와 문제 해결 절차.','pages':pages}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'volume01-appendix-a.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    EX.mkdir(parents=True,exist_ok=True)
    for old in EX.glob('CA-*.txt'):old.unlink()
    for cmd in commands:(EX/(cmd['id']+'.txt')).write_text(cmd['text']+'\n')
    (EX/'manifest.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
    print(len(pages),'pages',len(commands),'commands')
