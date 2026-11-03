"""REV02의 기술 해석·사례 경계·찾아보기를 보완하는 두 번째 편집 단계."""
from pathlib import Path
from copy import deepcopy
import json,re,csv
from revise_volume01_rev02 import ROOT,OUT,ED,P,H,L,BOX,page,write,strings

def findpage(d,prefix):return next(p for p in d['pages'] if p['title'].startswith(prefix))
def replace_all(d,a,b):return strings(d,lambda s:s.replace(a,b))
def replace_p(d,needle,text):
    found=0
    for p in d['pages']:
        for b in p['blocks']:
            if b['type']=='p' and needle in b['text']:b['text']=text;found+=1
    assert found==1,(needle,found)
def command(cid,where,purpose,text,syntax,result):return dict(type='command',id=cid,where=where,purpose=purpose,text=text,syntax=syntax,result=result)

PREDICT={
4:('4.3','같은 확인 문구를 남겨도 아카이브와 경보에 모두 나타날까? 수집 파일·프로그램 이름·규칙의 역할을 근거로 예상하고 규칙 적용 전후를 비교한다.'),
5:('5.5','정상 조회의 200과 공격 입력의 응답이 어떻게 달라질지 적는다. 403이면 어느 기록에서 차단 주체를 확인할지도 함께 정한다.'),
6:('6.4','틀린 암호와 맞는 암호를 입력하면 응답 코드만으로 구분할 수 있을까? 일반 로그인과 Brute Force 메뉴의 결과를 각각 예상한다.'),
7:('7.2','파일 추가 경보가 있으면 웹 요청과 명령 실행도 확인된 것일까? 각 단계에서 필요한 기록을 먼저 적고 제시한 사례와 대조한다.'),
8:('8.4','실패 뒤의 성공 로그에서 계정·출발지 IP가 같으면 같은 접속이라고 볼 수 있을까? 접속을 구분할 필드를 정한 뒤 원문을 읽는다.'),
9:('9.3','공개 키 파일의 변경과 공개 키 인증 성공은 어디에 각각 남을까? 변경 알림으로 확인할 수 있는 범위부터 적는다.'),
10:('10.3','현재 리스너 조회와 다음 예약 조회가 서로 다른 결과를 보일 수 있는 이유를 적는다. 실행 호스트와 조회 시각을 근거로 삼는다.'),
11:('11.4','실행 일지를 덮고 사례 A의 로그만 읽는다. 확정할 수 있는 사실과 설명이 필요한 공백을 나누어 적은 뒤 일지와 대조한다.')}
BLIND={
4:('4.8','Ruleset Test는 입력한 문장에 대한 디코더와 규칙의 결과이다. 에이전트가 실제 파일을 읽고 Indexer까지 전달했는지는 새 확인 로그와 Discover에서 별도로 확인한다.'),
5:('5.9','접속 로그의 URL과 응답 코드는 SQL 실행 결과나 브라우저의 스크립트 실행을 모두 담지 않는다. 응답 본문과 애플리케이션·WAF 기록에서 빠진 근거를 보충한다.'),
6:('6.4','일반 로그인 POST 본문과 응답 Location은 이 접속 로그 형식에 포함되지 않는다. 인증 결과를 판단하려면 브라우저 응답 또는 애플리케이션의 인증 기록이 필요하다.'),
7:('7.5','웹 프록시의 접속 로그에 없는 POST 본문과 애플리케이션 컨테이너의 명령 실행은 별도 자료로 확인한다. 수집하지 않은 값을 탐지 규칙만으로 복원할 수는 없다.'),
8:('8.8','Active Response의 add 기록은 대응 명령이 요청되거나 처리된 흔적이다. 실제 차단 효과는 적용된 방화벽 규칙과 차단 중 새 연결의 결과를 확인해야 판단할 수 있다.'),
9:('9.9','파일 변경 경보가 없는 것이 파일 불변을 보장하지는 않는다. 감시 경로·검사 방식·주기·에이전트 상태를 확인하고 변경 전후 파일과 실행 기록을 대조한다.'),
10:('10.6','현재 상태의 한 번 조회로는 조회 사이에 생겼다가 사라진 리스너를 찾을 수 없다. 예약 조회도 간격과 선택한 열에 따라 관찰할 수 있는 변화가 달라진다.'),
11:('11.8','발췌 자료에는 선택하지 않은 시간과 기록이 빠져 있다. 발췌본에 없는 행동을 발생하지 않은 일로 쓰지 말고 원자료의 검색 범위와 보존 상태를 확인한다.')}

def main():
    moved=[];all_inputs=[]
    for c in range(1,12):
        path=OUT/f'volume01-chapter{c:02}.json';d=json.loads(path.read_text('utf8'))
        if c==1:
            d=replace_all(d,'공격 일지','실행 일지')
            findpage(d,'목차')['title']='1권의 구성'
            findpage(d,'1권의 구성')['blocks'].insert(0,P('장과 부록은 각각의 문서로 제공한다. 아래 표에서 조사 질문을 찾고 해당 장의 절 제목과 명령 번호를 따라 읽는다.'))
            replace_p(d,'1권을 마치면 독자는 다음을 할 수 있다.','Linux 터미널과 보안 도구를 처음 다루는 대학 1~2학년 수준을 기준으로 한다. 낯선 도구는 처음 쓸 때 역할과 기본 구문을 설명하고, 뒤에서는 해당 실습에 필요한 옵션과 판정 근거에 집중한다. 반복되는 기본 구문은 부록 B에서 다시 찾는다. 1권을 마치면 다음을 할 수 있다.')
            # 오래된 도식의 탐지=조사 일치라는 문구를 재사용하지 않는다.
            for p in d['pages']:
                p['blocks']=[b for b in p['blocks'] if not(b['type']=='image' and 'rev01-casebook' in b['path'])]
            p=findpage(d,'1.8');i=next(i for i,b in enumerate(p['blocks']) if b['type']=='p' and b['text'].startswith('두 기록을 대조할 때'))
            p['blocks'].insert(i,{'type':'table','head':['실행 일지의 동작','조사 기록에서 대조할 근거'],'rows':[['어디서 무엇을 입력했는가','대상·출발지·시각·입력값'],['무슨 응답과 변화가 있었는가','원본 로그·응답·파일·계정·프로세스'],['어느 단계까지 관찰했는가','수집·경보 생성·검색·해석을 각각 기록']],'widths':[49,78]})
        if c==2:
            p=findpage(d,'2.2');insert=next(i for i,b in enumerate(p['blocks']) if b.get('id')=='C02-01')
            prep=[H('접속 전 계정과 서버 키 확인'),P('실습 계정이 없다는 전제와 접속할 서버의 키를 먼저 확인한다. 컨테이너 안에서 확인한 뒤 VM 터미널로 돌아와 접속한다.'),
                command('C02-P1','kt66 VM · 터미널','bastion 안에서 사전 조건을 확인할 셸을 연다.','docker exec -it kt66-bastion /bin/bash','docker exec는 실행 중인 컨테이너에서 프로그램을 시작한다. -i는 입력 연결, -t는 터미널 할당이다. /bin/bash는 사용할 셸이다.','프롬프트가 bastion의 셸로 바뀌었는지 확인한다.'),
                command('C02-P2','kt66-bastion 컨테이너 안','시험에 쓸 계정이 존재하는지 확인한다.','getent passwd book02_probe','getent는 시스템의 계정·그룹 등 이름 서비스 정보를 조회한다. passwd는 사용자 정보, 마지막 값은 찾을 계정명이다.','출력이 없으면 이 이름을 쓴다. 계정 행이 나오면 다른 미사용 이름을 정하고 본 절의 접속·검색에 동일하게 적용한다.'),
                command('C02-P3','kt66-bastion 컨테이너 안','접속할 SSH 서버의 Ed25519 공개 키 지문을 확인한다.','ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub','ssh-keygen은 SSH 키를 생성·관리한다. -l은 지문을 출력하고 -f는 읽을 키 파일을 지정한다. 공개 키 지문은 접속한 서버가 기대한 서버인지 대조하는 값이다.','SHA256: 뒤의 지문을 적는다. 파일이 없으면 SSH 서버 준비 상태부터 확인한다.'),
                command('C02-P4','kt66-bastion 컨테이너 안','SSH 클라이언트를 실행할 VM 터미널로 돌아간다.','exit','exit는 현재 셸을 끝낸다. 컨테이너는 계속 실행된다.','kt66 VM 계정의 프롬프트인지 확인한다.'),
                command('C02-P5','kt66 VM · 터미널','기존에 저장된 bastion 서버 키가 있는지 확인한다.','ssh-keygen -F 10.20.30.201','-F는 known_hosts에서 지정한 서버를 찾는다. known_hosts는 접속한 서버의 공개 키를 저장하는 파일이다.','출력 유무를 적는다. 기존 항목이 있으면 실습 뒤에도 보존한다. 처음 추가한 항목만 선택 원상복구 대상으로 삼는다.')]
            p['blocks'][insert:insert]=prep
            for b in p['blocks']:
                if b.get('id')=='C02-01':
                    b['text']='ssh -o HostKeyAlgorithms=ssh-ed25519 \\\n  book02_probe@10.20.30.201'
                    b['syntax']+=' -o는 SSH 설정 항목을 지정한다. HostKeyAlgorithms=ssh-ed25519는 서버 확인에 Ed25519 키를 사용하도록 정한다.'
                    b['result']='처음 접속하면 표시된 SHA256 지문을 C02-P3과 대조한다. 일치할 때 yes를 입력한다. password:에서 실습용 틀린 암호를 한 번 입력한다. Permission denied, please try again.이 나오면 Ctrl+C로 끝내고 시각을 기록한다. 키 변경 경고나 지문 불일치가 나오면 접속을 멈추고 대상 주소와 서버 키를 확인한다.'
            replace_p(d,'C02-01은 kt66 VM의 ~/.ssh/known_hosts에','처음 접속해 서버 키를 승인하면 ~/.ssh/known_hosts에 항목이 추가된다. C02-P5에서 기존 항목이 없었고 이번에 새로 추가한 경우에만 C02-05를 선택해 원상복구한다. 기존에 저장돼 있던 서버 키는 유지한다.')
            replace_p(d,'VM의 주소 192.168.0.189가 아니라','Invalid user 줄은 없는 계정의 접속 요청, Failed password for invalid user 줄은 해당 계정의 암호 인증 실패를 기록한다. 두 번째 줄이 2.1과 같은 형식이다. from 뒤를 읽어 실제 출발지 IP를 적는다. 기준 경로에서는 VM의 외부 주소 대신 ext망 주소 10.20.30.254가 예상된다.')
            d=replace_all(d,'이 번호는 규칙 5710에 일치하면 항상 붙는다.','이 번호는 이 버전의 규칙 5710에 미리 지정된 분류이다.')
            # 줄바꿈으로 생략한 정의를 완전한 조건으로 표시한다.
            d=replace_all(d,'^Failed \\S+ for invalid user|…','^Failed \\S+ for invalid user|^Failed \\S+ for illegal user')
        if c==3:
            replace_p(d,'화면의 시각은 브라우저가', '화면 시각은 Dashboard의 시간대 설정에 따른다. 기본 Browser 설정이면 Windows 브라우저의 시간대를 사용한다. timestamp에 +0000 또는 Z가 붙어 있으면 UTC이므로 KST와 대조할 때 9시간을 더한다. 표시 시간대와 원문의 시간대를 2.4의 방법으로 함께 기록한다.') if any(b['type']=='p' and '화면의 시각은 브라우저가' in b.get('text','') for p in d['pages'] for b in p['blocks']) else None
            for p in d['pages']:
                for b in p['blocks']:
                    if b['type']=='box' and '화면의 시각은 브라우저가' in str(b.get('text')):b['text']=['화면 시각은 Dashboard의 시간대 설정에 따른다. 기본 Browser 설정이면 Windows 브라우저의 시간대를 사용한다. timestamp에 +0000 또는 Z가 붙어 있으면 UTC이므로 KST와 대조할 때 9시간을 더한다(2.4).']
        if c==7:
            replace_p(d,'본문의 결과 화면은','각 사례에서 입력·응답·로그를 대조한 뒤 확인한 사실, 더 필요한 증거, 대응 조치를 적는다. 직접 남긴 기록은 자신의 실행 시각과 주소로 찾고, 제시한 사례의 기록은 표시된 날짜와 대상을 기준으로 읽는다.')
            replace_p(d,'슬라이드의 실습은 관리자가','이 사례는 관리자가 kt66-web 안에 PHP 파일을 만들어 파일이 놓인 상태를 재현한다. HTTP 업로드 과정을 시험한 결과와 구분한다. FIM은 지정한 경로에서 파일 추가·변경·삭제를 관찰한다.')
            replace_p(d,'원본 슬라이드에는 VirusTotal','VirusTotal 연동 경보 87105는 외부 조회 결과를 분류한다. FIM의 파일 추가 경보 554와는 근거가 다르다. 악성 엔진의 탐지 수는 실제 연동 결과를 확인한 경우에만 기록한다. 해당 연동은 이 권의 실습 범위 밖이다.')
            replace_p(d,'슬라이드에는 외부 LDAP','이 사례의 목표는 요청 문자열과 응답·로그를 대응시키는 것이다. DVWA는 PHP 애플리케이션이므로 접속 로그의 문자열만으로 Log4j 실행을 입증할 수 없다. 외부 LDAP 조회와 Java 코드 실행을 판단하려면 해당 시스템의 통신·프로세스 기록이 더 필요하다.')
            p=findpage(d,'7.2');p['blocks'].insert(1,P('사례 화면의 파일명은 shell.php이고 직접 만드는 파일명은 book07-shell.php이다. 기존 파일을 덮어쓰지 않도록 실습 이름을 분리했다. 검색할 때는 전체 경로와 시각으로 두 파일을 구분한다.'))
            # 자료 제작 행위 대신 관찰 대상/범위를 표현한다.
            for p in d['pages']:
                for b in p['blocks']:
                    if b['type'] in ['p','table','box']:
                        if '슬라이드' in str(b):moved.append({'chapter':c,'section':p['title'],'original':deepcopy(b)})
                        b.update(strings(b,lambda s:s.replace('같은 슬라이드의','같은 사례의').replace('원본 슬라이드','사례 자료').replace('슬라이드의','사례의').replace('슬라이드에는','사례 기록에는').replace('슬라이드는','사례 기록은').replace('슬라이드 응답','사례 응답').replace('슬라이드 명령','단순 상태 출력 명령')))
        # 주소는 직접 입력 예시와 관찰한 사례값을 섞지 않는다. 각 장에서 관계를 설명한다.
        if c in [5,6,8,9,10]:
            d['pages'][0]['blocks'].append(P('입력의 주소와 사이트 이름은 자신의 환경에 맞춘다. 화면의 시각·주소·에이전트 번호·경보 건수는 사례값이다. 자신의 결과는 실행 일지의 시각과 실제 수집 필드로 연결하며 사례의 건수를 완료 조건으로 쓰지 않는다.'))
        if c in PREDICT:
            prefix,text=PREDICT[c];findpage(d,prefix)['blocks'].insert(0,BOX('predict',text))
            prefix,text=BLIND[c];findpage(d,prefix)['blocks'].append(BOX('blind',text))
        # 반복되는 컨테이너 접속 구문은 처음 설명으로 연결한다. 목적과 도구 역할은 남긴다.
        if c>=4:
            for p in d['pages']:
                for b in p['blocks']:
                    if b['type']=='command' and b['text'].startswith('docker exec -it'):
                        dest=b['text'].split()[3]
                        b.pop('why',None);b['purpose']=f'{dest} 컨테이너 안에서 다음 작업을 수행할 셸을 연다.'
                        b['syntax']='docker exec -it와 /bin/bash의 역할은 C02-P1에서 설명했다. 컨테이너 이름을 대조한 뒤 입력한다.'
                    elif b['type']=='command' and b['text']=='exit':
                        b.pop('why',None);b['purpose']='현재 셸을 끝내고 바깥 실행 위치로 돌아간다.';b['syntax']='종료 뒤 프롬프트로 실행 위치를 확인한다(C02-P4).'
        # 기본 도구의 설명을 지우는 대신 구문과 목적이 이미 분명한 문장을 분리한다.
        for p in d['pages']:
            for b in p['blocks']:
                if b['type'] in ['command','query'] and 'why' in b:
                    first,sep,rest=b['why'].partition('. ')
                    if sep and re.search(r'(확인한다|찾는다|읽는다|기록한다|대조한다|출력한다|옮긴다|접속한다|복원한다|제거한다|검색한다|정한다|저장한다)$',first) and not re.match(r'(grep|cat|ls|cd|pwd|exit|rm|curl|sudo|ssh|chmod|chown|tail|sed|awk|systemctl|echo|printf|mkdir|rmdir|getent|find|ps|ss|dpkg|apt)',first):
                        b['purpose']=first+'.';b['syntax']=rest;b.pop('why')
                if b['type'] in ['command','query']:
                    target=ROOT/f'examples/rev02/chapter{c:02}'/(b['id']+'.txt');target.write_text(b['text']+'\n','utf8')
                    all_inputs.append({'chapter':c,'section':p['title'],'id':b['id'],'where':b['where'],'file':target.relative_to(ROOT).as_posix(),'text':b['text']})
        write(path,d)
    write(ED/'moved-editorial-notes.json',moved)
    write(ROOT/'examples/rev02/input-index.json',all_inputs)
    with (ROOT/'examples/rev02/input-index.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['chapter','section','id','where','file']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in all_inputs)
    # 절차를 줄이는 대신 장말의 안내 없는 조사 과제로 난도를 올린다.
    notes='''사례 번호:
장·절 / 실행 회차:
대상 호스트·컨테이너 / 주소 / 버전:
시작·종료 시각 / 시간대:
예측과 근거:
입력과 실행 위치:
응답·현재 상태:
원문 생성 확인 / 파일·원문:
수집 확인 / location·agent:
경보 생성 확인 / rule.id·저장 기준:
검색 확인 / 인덱스·기간·DQL·필터:
기록 식별 / _index·_id 또는 증거 파일·해시:
확인한 사실:
해석 / 추가로 필요한 근거:
정상 행위로 설명할 가능성과 대조 자료:
변경 전 상태 / 원상복구 / 재확인:
'''
    for target in [ROOT/'examples/rev02/casebook.txt',ROOT/'examples/rev02/chapter01/casebook.txt']:target.write_text(notes,'utf8')
    # 부록 B에서 처음 도구가 설명된 명령 번호를 찾도록 연결한다.
    bpath=OUT/'volume01-appendix-b.json';b=json.loads(bpath.read_text('utf8'))
    wanted=['docker','grep','logger','ssh','ssh-keygen','curl','systemctl','getent','chmod','chown','sed','awk','ss','ps','osqueryi','nmap','hydra','gobuster']
    rows=[]
    for tool in wanted:
        hit=next((r for r in all_inputs if re.search(r'(?m)^(?:sudo )?'+re.escape(tool)+r'\b',r['text'])),None)
        if hit:rows.append([tool,hit['id'],hit['section']])
    b['pages'].append(page('B.7  도구 설명과 입력 찾아보기',[P('아래 명령 번호에서 역할과 기본 구문을 확인한다. 해당 장의 예제 디렉터리에 같은 번호의 텍스트 파일이 있다. 전체 입력 목록은 examples/rev02/input-index.csv이다.'),{'type':'table','head':['도구','입력 번호','위치'],'rows':rows,'widths':[32,25,70]}]))
    write(bpath,b)
    # 부록 E의 공통 조사 양식과 파일 경로를 최신화한다.
    ep=OUT/'volume01-appendix-e.json';e=json.loads(ep.read_text('utf8'))
    e['pages'].insert(1,page('E.0  사례를 나누어 기록하기',[P('장·절·실행 회차를 사례 번호로 정하고 실행 일지와 조사 기록에 같은 번호를 붙인다. 서로 다른 실습은 별도로 기록한다. 사례 번호만 같게 붙이는 것으로 인과관계가 생기지는 않는다.'),P('공통 양식은 examples/rev02/casebook.txt이다. 수집·경보 생성·검색·해석의 확인 여부를 각각 남기며, 미확인에는 다음에 확보할 자료를 적는다.')]))
    write(ep,e)
    print('Refined chapters and indexed inputs:',len(all_inputs))

if __name__=='__main__':main()
