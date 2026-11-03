"""REV02의 설치 분리, 부록 연결, 마지막 문체 교정. refine 뒤 한 번 실행한다."""
import json,re,csv
from copy import deepcopy
from revise_volume01_rev02 import ROOT,OUT,ED,P,H,L,BOX,page,write,strings
from refine_volume01_rev02 import findpage,replace_p

def main():
    one=OUT/'volume01-chapter01.json';d=json.loads(one.read_text('utf8'))
    ap=OUT/'volume01-appendix-a.json';a=json.loads(ap.read_text('utf8'))
    for number,label in [(3,'VM과 Ubuntu 준비'),(4,'kt66 코드와 환경 설정'),(5,'Docker와 메모리 매핑 설정'),(9,'공격자 VM 도구 설치')]:
        p=findpage(d,f'1.{number} ');copy=deepcopy(p);newnum={3:12,4:13,5:14,9:15}[number]
        copy['title']=f'A.{newnum}  {label}';copy['break']=False
        a['pages'].append(copy)
        if number==3:
            p['blocks']=[P('Windows의 VMware Workstation Pro에서 Ubuntu Desktop 22.04 LTS x86_64 VM을 준비한다. kt66 VM에는 메모리 16GB 이상과 가상 디스크 200GB 이상을 할당하고 네트워크를 Bridged로 정한다. Windows와 공격자 VM이 사용할 자원은 별도로 남긴다.'),P('Ubuntu 사용자 이름은 ccc로 정한다. 기준 kt66의 호스트 감시 설정이 /home/ccc/.ssh를 사용하기 때문이다. 설치 화면 순서는 부록 A.1·A.2, 터미널에서 운영체제·자원·주소를 확인하고 기본 도구를 설치하는 순서는 A.12에 있다.'),P('설치 직후 전원을 끄고 ubuntu-clean 스냅샷을 남긴다. VM을 다시 켜서 C01-01~03으로 운영체제·자원·IPv4 주소를 확인하고 사건 노트에 적는다. 이후 브라우저와 hosts에는 이 주소를 사용한다.'),BOX('caution','DHCP 주소가 바뀌면 접속 대상도 달라진다. 재기동 뒤에는 C01-03으로 주소를 확인하고 .env·hosts의 값과 대조한다. 설치를 마친 기준 상태는 1.8에서 별도로 보존한다.')]
        elif number==4:
            p['blocks']=[P('부록 A.13의 C01-07~13을 순서대로 수행한다. Git으로 kt66을 받은 뒤 커밋 63d4180b1d6866de986ef263a3bd831d6082b5d5에 맞추고 .env를 준비한다. 커밋은 코드의 특정 시점이며 이 책의 구성과 결과를 대조하는 기준이다.'),P('.env는 kt66 설치 도구가 읽는 설정 파일이다. API_KEY는 관리 기능의 키, SSH_USER·SSH_PASS는 실습 컨테이너의 계정이다. Ubuntu 계정과 Wazuh 로그인은 별개이다. 예시 파일을 복사하기 전에 기존 .env 유무를 확인하고, 공개 자료에 키와 암호를 남기지 않는다.'),P('설정은 이후 ~/kt66에서 사용한다. A.13의 확인 명령으로 기준 커밋과 필요한 항목을 대조한 뒤 1.5로 진행한다. WEB_HOST_IP·INT_HOST_IP는 설치 도구가 실제 주소를 확인해 기록하므로 빈 값의 처리와 기존 값의 재사용도 함께 확인한다.')]
        elif number==5:
            p['blocks']=[P('부록 A.14의 C01-14~19를 수행한다. kt66.sh install은 Docker 등 설치 준비를 처리하고, up은 서비스와 호스트 센서를 구성한다. Docker는 VM 안에서 서비스를 컨테이너로 실행한다.'),P('Docker 그룹을 새로 적용했다면 로그아웃 후 다시 로그인해야 일반 계정의 권한이 갱신된다. docker info로 사용 가능 여부를 확인하고 Indexer에 필요한 vm.max_map_count 값도 검사한다. 이 값은 프로세스가 사용할 메모리 매핑 영역 수의 상한이다.'),P('C01-19에서 VM 주소·LAB_DOMAIN·.env 주소를 다시 읽는다. install에서 기록한 주소는 up이 재사용하며, 아직 주소가 없으면 up이 감지한 값을 확인받아 .env에 기록한다. 준비 결과가 맞으면 다음 절에서 서비스를 기동한다.')]
        else:
            p['blocks']=[P('공격자 VM은 kt66과 별개의 Ubuntu 22.04 Live Server VM이다. 5장의 선택 curl 실습과 6장 이후의 터미널 실습에서 사용한다. kt66 내부의 attacker 컨테이너와 구분한다.'),P('kt66과 같은 실습망에 Bridged로 연결하되 다른 IP를 사용한다. CPU 2개·메모리 2GB·디스크 25GB는 도구 실행을 위한 시작 예시이며 검증된 최소 사양을 뜻하지 않는다. 설치 순서는 부록 A.3, 도구별 역할과 일괄 설치·접속 확인은 A.15의 C01-24~26을 따른다.'),P('도구 설치 전 attacker-clean, 설치와 kt66 접속 확인 후 attacker-ready 스냅샷을 남긴다. Windows 브라우저만 사용하는 5장 본 실습을 먼저 진행해도 된다. 웹 이름 등록은 5.2, 공격자 VM의 이름·시각 확인은 5.13에서 수행한다.')]
    for p in d['pages']:
        p['blocks']=[b for b in p['blocks'] if not(b['type']=='p' and re.match(r'^2026년 11월\s+전두용',b['text']))]
    pref=findpage(d,'머리말');pref['blocks'][1]['text']='경보를 해석하는 기준'
    pref['blocks'][2]['text']=pref['blocks'][2]['text'].replace('첫째, ','')
    write(one,d);write(ap,a)
    # 기술적 보완: bastion이 실제 사용하는 영구 호스트 키 경로를 대조한다.
    p2=OUT/'volume01-chapter02.json';d=json.loads(p2.read_text('utf8'))
    for p in d['pages']:
        for b in p['blocks']:
            if b.get('id')=='C02-P3':
                b['text']="sshd -T | grep '^hostkey '\nssh-keygen -lf \\\n  /var/lib/bastion/ssh-host-keys/ssh_host_ed25519_key.pub"
                b['syntax']='sshd -T는 SSH 서버의 유효 설정을 출력한다. 셸의 파이프(|)는 이를 grep의 입력으로 전달한다. 작은따옴표 안의 ^hostkey 는 hostkey와 공백으로 시작하는 줄을 고른다. 첫 줄의 Ed25519 키 경로에 .pub를 붙인 공개 키를 둘째 명령에 지정한다. ssh-keygen의 -l은 지문 출력, -f는 키 파일 지정이다.'
                b['result']='기준 bastion의 유효 키 경로가 예시와 일치하는지 확인한 뒤 지문을 읽는다. 경로가 다르면 유효 설정의 Ed25519 키에 맞춘다. SHA256 지문을 적고 C02-01의 서버 지문과 대조한다.'
    write(p2,d)
    # 자료 제작 이력은 저자 기록에 남기고 본문은 관찰 대상과 필요한 차이로 쓴다.
    moved=[]
    for f in OUT.glob('*.json'):
        d=json.loads(f.read_text('utf8'));cm=re.search(r'chapter(\d+)',f.name);c=int(cm[1]) if cm else None
        for p in d['pages']:
            for b in p['blocks']:
                if b['type']=='p':
                    original=b['text'];s=original
                    s=s.replace('촬영한 실습 환경의 값','사례 환경의 값').replace('촬영 환경의','사례 환경의').replace('촬영 구간의','사례 구간의').replace('촬영 범위는','사례 조회 범위는').replace('촬영 경보에는','제시한 경보에는').replace('촬영 기록의','사례 기록의').replace('촬영한 Wazuh 4.10 환경의','제시한 Wazuh 4.10 기록의').replace('촬영한 파일의','사례 파일의').replace('각각 촬영 환경의 주소','각각 사례 환경의 주소').replace('검증 환경의 결과','사례의 관찰 결과').replace('슬라이드 변형 요청','변형 요청 사례')
                    if '촬영 준비 때 호스트 에이전트' in s:s='호스트 에이전트가 설치돼 있어도 서비스가 멈췄거나 등록 키가 없으면 새 기록을 받을 수 없다. 1.7과 부록 A.6에서 서비스·Manager 주소·등록 상태를 확인한다. 기존 키를 지우기 전에 어느 단계가 준비되지 않았는지 먼저 구분한다.'
                    if '슬라이드의 nc -lk' in s:s='nc -lk 31337 뒤에 앰퍼샌드(&)를 붙이면 백그라운드에서 실행된다. 여기서는 터미널에 전경으로 실행해 종료할 프로세스를 확인하고 Ctrl+C로 끝낸다. 백그라운드로 실행했다면 PID와 명령줄을 확인해 해당 프로세스를 종료해야 한다.'
                    if '7장의 검색식은 슬라이드' in s:s='명령 번호는 각 장의 조건과 결과 해석으로 돌아가는 안내이다. 자신의 기간·주소·에이전트 이름을 먼저 지정하고, 사례 기록은 제시된 날짜와 대상으로 조회한다.'
                    if 'Module 01의 나머지 실습' in s:s='11장에서는 위 실습의 저장 자료로 사건 재구성과 대응 판단을 연습한다. 이 표는 원자료와 책의 학습 범위를 연결하며, 각 사례의 성공 여부와 탐지 범위는 해당 장의 근거로 판단한다.'
                    if s!=original:moved.append({'file':f.name,'section':p['title'],'original':original,'revision':s})
                    b['text']=s
                if c and b['type'] in ['command','query']:
                    for key in ['why','purpose','syntax','result']:
                        if key in b:b[key]=re.sub(r'\[(\d+)\]',lambda m:f'[{c}-{m[1]}]',b[key])
        write(f,d)
    write(ED/'wording-corrections.json',moved)
    # ATT&CK는 학습 주제와의 대응이다. 모든 사례에 악성 기법을 강제로 붙이지 않는다.
    fp=OUT/'volume01-appendix-f.json';f=json.loads(fp.read_text('utf8'))
    mapping=[
      ['암호 추측 · 6.4, 8.2~8.4','T1110.001','실패·성공·반복 패턴. 한 번의 실패만으로 악성 여부를 확정하지 않는다.','Password Guessing','T1110/001/'],
      ['SSH 접속 · 8장','T1021.004','계정·시각·접속과 후속 동작. 승인된 원격 관리도 같은 프로토콜을 쓴다.','SSH','T1021/004/'],
      ['웹셸 파일 · 7.2','T1505.003','파일 추가와 요청. 실제 웹셸 실행은 응답·프로세스 증거가 더 필요하다.','Web Shell','T1505/003/'],
      ['공개 키 · 9.3, 10.7','T1098.004','키 등록과 사용을 구분한다. 10장의 키 조회는 인증 성공을 시험한 결과가 아니다.','SSH Authorized Keys','T1098/004/'],
      ['cron · 9.4','T1053.003','작업 등록·실행 기록. 예약식만으로 실행 성공을 판정하지 않는다.','Cron','T1053/003/'],
      ['sudo · 8.6, 9.2','T1548.003','권한 설정과 사용. 기존 허용 정책과 승인된 작업을 대조한다.','Sudo and Sudo Caching','T1548/003/'],
      ['포트 탐색 · 10.4','T1046','요청·응답·DROP과 서비스 상태. 스캔 관찰은 침투 성공과 구분한다.','Network Service Discovery','T1046/']]
    f['pages'].append(page('F.4  ATT&CK 기법과 조사 근거',[P('MITRE ATT&CK의 기법 설명과 이 책의 학습 주제를 대응시킨 표이다. 저자의 학습 분류이며 Wazuh 경보의 rule.mitre.id와 항상 같지는 않다. 정상 점검과 관리 작업도 같은 동작을 하므로 기법 번호만으로 공격이나 탐지 성공을 판정하지 않는다.'),{'type':'table','head':['학습 주제','기법 ID','확인 범위'],'rows':[r[:3] for r in mapping],'widths':[37,28,62]},P('이 표는 탐지율이나 전체 공격 기법의 검증 범위를 나타내지 않는다. SQL 인젝션·XSS 같은 웹 취약점 이름은 실제 사용 목적과 결과가 확인되지 않으면 하나의 ATT&CK 기법으로 고정하지 않는다.')]))
    f['pages'].append(page('F.5  ATT&CK 자료',[{'type':'link','text':'MITRE ATT&CK · '+r[1]+' '+r[3],'url':'https://attack.mitre.org/techniques/'+r[4]} for r in mapping]))
    write(fp,f)
    # 최종 위치로 입력 목록과 장별 manifest를 다시 만든다.
    index=[]
    for f in sorted(OUT.glob('*.json')):
        d=json.loads(f.read_text('utf8'))
        for p in d['pages']:
            for b in p['blocks']:
                if b['type'] not in ['command','query']:continue
                folder='appendix-a' if b['id'].startswith('CA-') else f'chapter{b["id"][1:3]}'
                target=ROOT/'examples/rev02'/folder/(b['id']+'.txt');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(b['text']+'\n','utf8')
                index.append({'document':f.name,'section':p['title'],'id':b['id'],'where':b['where'],'file':target.relative_to(ROOT).as_posix(),'text':b['text']})
    write(ROOT/'examples/rev02/input-index.json',index)
    with (ROOT/'examples/rev02/input-index.csv').open('w',encoding='utf-8-sig',newline='') as h:
        w=csv.DictWriter(h,fieldnames=['document','section','id','where','file']);w.writeheader();w.writerows({k:x[k] for k in w.fieldnames} for x in index)
    for folder in set(Path(r['file']).parent for r in index):
        write(ROOT/folder/'rev02-inputs.json',[r for r in index if Path(r['file']).parent==folder])
    print('Final input index',len(index))

if __name__=='__main__':
    from pathlib import Path
    main()
