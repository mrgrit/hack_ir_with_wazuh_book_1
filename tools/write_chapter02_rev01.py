"""REV01 · 2장 공격과 보안관제의 기초. 저자용이며 실습 명령을 실행하지 않는다.

2026-11-02 개정 기준
- 조사 질문: 경보 한 건에서 무엇을 읽는가. 사례는 기존 kt66의 bastion SSH 인증 실패 경보 한 건이다.
- 1장 REV01과 같은 흐름 조판·명령 블록(목적 → 입력 → 구문 → 확인)·상자 4종을 쓴다.
- 2.2에서 독자가 같은 형식의 기록을 직접 남기고 bastion의 auth.log에서 찾는다.
- 디코더·규칙 설명은 Wazuh v4.10.0 ruleset(0310-ssh_decoders.xml, 0095-sshd_rules.xml)과 대조했다.
- kt66 사실(bastion 10.20.30.201, 호스트 .254 주소, 컨테이너 시간대, 아카이브 인덱스)은 기준 커밋 소스와 대조했다.
"""
import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/REV01'
EX=ROOT/'examples/rev01/chapter02'
COMMIT='63d4180b1d6866de986ef263a3bd831d6082b5d5'
KT66='https://github.com/mrgrit/kt66/blob/'+COMMIT
WAZUH='https://github.com/wazuh/wazuh/blob/v4.10.0/ruleset'
pages=[];commands=[]

def p(t): return {'type':'p','text':t}
def h(t): return {'type':'h','text':t}
def ul(*items): return {'type':'list','items':list(items)}
def ol(*items): return {'type':'list','style':'number','items':list(items)}
def tab(head,rows,widths=None,keep=False):
    b={'type':'table','head':head,'rows':rows,'widths':widths}
    if keep:b['keep']=True
    return b
def img(path,caption,width=127): return {'type':'image','path':path,'caption':caption,'width_mm':width}
def box(kind,*text,items=None):
    b={'type':'box','kind':kind,'text':list(text)}
    if items:b['items']=items
    return b
def code(t): return {'type':'code','text':t}
def link(text,url): return {'type':'link','text':text,'url':url}
def c(text,purpose,syntax,result,where='kt66 VM · 터미널'):
    b={'type':'command','id':f'C02-{len(commands)+1:02d}','where':where,'purpose':purpose,'text':text,'syntax':syntax,'result':result}
    commands.append(b);return b
def page(title,*blocks,brk=True,level='page'):
    pg={'title':title,'kind':'body','blocks':list(blocks)}
    if not brk:pg['break']=False
    if level!='page':pg['level']=level
    pages.append(pg)
def section(title,*blocks):page(title,*blocks,brk=False,level='section')
FIG='assets/figures/chapter02/'
RAW='Nov  1 14:22:35 bastion sshd[7249]:\nFailed password for invalid user book03_probe\nfrom 10.20.30.254 port 50964 ssh2'

# ── 장 도입 ───────────────────────────────────────────────────
page('2장  공격과 보안관제의 기초',
    p('Wazuh 경보 목록에 sshd: Attempt to login using a non-existent user라는 경보가 있다. 누군가 서버에 들어온 것일까? 이 경보 한 건으로 말할 수 있는 것은 “없는 계정으로 로그인을 시도했고 실패했다”까지이다. 성공 여부, 접속한 사람, 시도 횟수는 다른 기록에서 확인해야 한다. 경보에서 확인한 사실과 아직 판단할 수 없는 부분을 나누는 것이 보안관제의 첫 작업이다.'),
    h('학습 목표'),
    ul('SSH 인증 기록 한 줄에서 계정·출발지·결과를 읽고, 같은 형식의 기록을 직접 남겨 확인한다.',
       '로그가 디코더와 탐지 규칙을 거쳐 경보가 되는 과정을 설명하고, 경보 필드가 원문·수집기·규칙 중 어디에서 왔는지 구분한다.',
       '공격 시도와 침입 결과, 확인한 사실과 판단을 구분해 조사 기록을 쓴다.'),
    img(FIG+'rev01-roadmap.png','도식 2-1. 2장 학습 순서.',120),
    h('준비와 완료 기준'),
    tab(['항목','내용'],[
        ['실행 위치','kt66 VM의 터미널, kt66-bastion 컨테이너의 셸'],
        ['선행 조건','1장 완료, kt66 기동(1.6)'],
        ['사례 자료','examples/rev01/chapter02/case-ssh.json · case-ssh.log'],
        ['완료 기준','2.2에서 남긴 기록을 auth.log에서 찾고, 2.7의 조사 기록을 채운다.'],
        ['원상복구','서비스 설정은 바뀌지 않는다. known_hosts에 추가된 bastion 키는 C02-05로 지운다.']],[32,95],keep=True))

# ── 2.1 ──────────────────────────────────────────────────────
section('2.1  경보 한 건 읽기',
    p('kt66의 bastion은 SSH 접속을 받는 서버 컨테이너이다. SSH는 네트워크로 다른 컴퓨터에 로그인해 명령을 실행하는 프로토콜이고, sshd는 SSH 접속을 받는 서버 프로그램이다. sshd는 접속과 인증 결과를 /var/log/auth.log에 기록한다. 다음은 기존 kt66의 bastion에서 수집한 기록 한 줄이다.'),
    code(RAW),
    box('predict','아래 표를 보기 전에 이 줄에서 로그인에 쓴 계정, 접속한 쪽의 주소, 인증 결과를 찾아 적는다.'),
    p('접속 요청을 보내는 쪽을 클라이언트라고 한다. 원문은 앞에서부터 기록 시각, 서버 이름, 프로그램, 메시지 순서로 읽는다.'),
    tab(['원문','읽는 내용'],[
        ['Nov  1 14:22:35','sshd가 기록한 시각. 연도와 시간대는 적혀 있지 않다(2.4).'],
        ['bastion','기록을 남긴 서버의 호스트 이름'],
        ['sshd[7249]','기록한 프로그램 sshd와 프로세스 번호 7249'],
        ['invalid user','서버에 없는 계정'],
        ['book03_probe','로그인에 사용한 계정명'],
        ['from 10.20.30.254','sshd가 기록한 접속 출발지 IP'],
        ['port 50964','클라이언트의 출발지 포트'],
        ['Failed password','암호 인증 실패'],
        ['ssh2','SSH 프로토콜 버전 2']],[42,85]),
    p('이 줄에서 확인한 사실은 “10.20.30.254에서 존재하지 않는 계정 book03_probe로 접속했고 암호 인증이 실패했다”이다.'),
    box('blind','sshd는 입력된 암호를 기록하지 않는다. 그래서 이 줄로는 어떤 암호를 시도했는지 알 수 없다. 접속한 사람이 누구인지, 시도가 몇 번이었는지, 이후 다른 계정으로 성공했는지도 이 줄에는 없다. 그 사실은 같은 출발지와 계정의 다른 기록에서 찾는다.'),
    p('원본 경보는 examples/rev01/chapter02/case-ssh.json에, 원문 한 줄은 case-ssh.log에 있다.'))

# ── 2.2 ──────────────────────────────────────────────────────
section('2.2  같은 기록 직접 남기기',
    p('같은 형식의 기록을 직접 만들면 기록의 각 값이 어떤 행동에서 나왔는지 알고 읽을 수 있다. 존재하지 않는 계정 book02_probe로 bastion에 로그인을 한 번 시도하고, bastion의 auth.log에서 그 기록을 찾는다.'),
    p('bastion은 kt66 내부의 ext망(10.20.30.0/24)에서 10.20.30.201 주소를 쓴다. kt66 VM도 이 망에 10.20.30.254 주소로 연결되어 있으므로 VM 터미널에서 bastion의 내부 주소로 바로 접속할 수 있다. kt66은 각 내부망의 .254 주소를 VM에 둔다. [1]'),
    c('ssh book02_probe@10.20.30.201',
      '존재하지 않는 계정으로 bastion에 SSH 로그인을 한 번 시도해 실패 기록을 남긴다.',
      'ssh는 1장에서 설치한 OpenSSH 클라이언트로, 원격 서버에 SSH로 로그인한다. @ 앞은 로그인 계정, 뒤는 접속할 주소이다. 포트를 지정하지 않으면 SSH 기본 포트 22로 접속한다.',
      '처음 접속하면 Are you sure you want to continue connecting (yes/no/[fingerprint])?가 나온다. yes를 입력하면 Warning: Permanently added …가 나오고 bastion의 키가 ~/.ssh/known_hosts에 저장된다. password:에서 아무 암호나 입력한다. 입력한 글자는 화면에 표시되지 않는다. Permission denied, please try again.이 나오면 **Ctrl+C**를 눌러 끝낸다. 실행한 시각을 사건 노트에 적는다.'),
    p('auth.log는 bastion 컨테이너 안의 파일이다. 컨테이너 셸로 들어가서 읽는다.'),
    c('docker exec -it kt66-bastion /bin/bash',
      'bastion 컨테이너의 셸로 들어간다.',
      'docker exec는 실행 중인 컨테이너 안에서 프로그램을 실행한다. -i는 키보드 입력을 연결하고 -t는 터미널을 할당한다. kt66-bastion은 컨테이너 이름, /bin/bash는 실행할 셸이다.',
      '프롬프트가 root@bastion:/# 형태로 바뀐다. 이후 명령은 컨테이너 안에서 실행된다.'),
    box('predict','auth.log에는 출발지가 어떤 주소로 기록되었을까? kt66 VM의 주소 192.168.0.189일까? 예측을 적은 뒤 다음 명령을 실행한다.'),
    c('grep "book02_probe" /var/log/auth.log',
      'C02-01에서 남긴 로그인 실패 기록을 찾는다.',
      'grep은 파일에서 지정한 문자열이 들어간 줄을 출력한다. 큰따옴표 안의 book02_probe가 찾을 문자열이고, 마지막 인자가 읽을 파일이다.',
      'Invalid user book02_probe from … 줄과 Failed password for invalid user book02_probe from … 줄이 나온다. 아무것도 나오지 않으면 C02-01의 계정 이름과 실행 여부를 확인한다.',
      where='kt66-bastion 컨테이너 · 셸'),
    p('Invalid user 줄은 없는 계정으로 로그인을 시작한 기록이고, Failed password for invalid user 줄은 그 계정의 암호 인증이 실패한 기록이다. 두 번째 줄이 2.1의 사례와 같은 형식이다. 이제 from 뒤의 출발지를 확인한다. VM의 주소 192.168.0.189가 아니라 10.20.30.254가 기록되어 있다.'),
    img(FIG+'rev01-ssh-path.png','도식 2-2. kt66 VM에서 접속한 기록의 출발지.'),
    p('kt66 VM은 bastion과 같은 ext망에 연결된 주소 10.20.30.254에서 접속을 보냈다. sshd는 직접 연결된 상대의 주소를 기록하므로 출발지는 10.20.30.254이다. 같은 VM이라도 어느 망을 거쳐 접속했는지에 따라 기록되는 주소가 달라진다. 공격자 VM처럼 다른 장비에서 접속했을 때 기록되는 주소는 8장에서 확인한다. [1]'),
    p('2.1의 사례도 출발지가 10.20.30.254이므로 kt66 VM을 거쳐 들어온 접속이다. 실제 사용자를 찾으려면 kt66 VM에서 그 시각에 실행된 접속을 이어서 조사한다. 출발지 IP는 접속자를 가리키는 증거가 아니라 접속 경로를 찾는 단서이다.'),
    c('exit',
      '컨테이너 셸에서 나와 kt66 VM 터미널로 돌아간다.',
      'exit는 현재 셸을 끝낸다. 셸을 끝내도 컨테이너는 계속 실행된다.',
      '프롬프트가 kt66 VM 계정의 프롬프트로 돌아온다.',
      where='kt66-bastion 컨테이너 · 셸'),
    h('기록과 원상복구'),
    p('실행한 시각, 계정 book02_probe, 기록된 출발지 10.20.30.254를 사건 노트의 조사 기록에 한 줄로 적는다. 3장에서 이 기록을 Wazuh에서 찾는다.'),
    p('C02-01은 kt66 VM의 ~/.ssh/known_hosts에 bastion의 키를 추가했다. known_hosts는 접속했던 SSH 서버의 키를 저장하는 파일이다. 지울 때는 다음 명령을 쓴다.'),
    c('ssh-keygen -F 10.20.30.201\nssh-keygen -R 10.20.30.201\nssh-keygen -F 10.20.30.201',
      '(선택) known_hosts에 추가된 bastion의 키를 확인하고 지운 뒤 다시 확인한다.',
      'ssh-keygen은 SSH 키를 만들고 관리한다. -F는 known_hosts에서 지정한 서버의 키를 찾아 출력하고, -R은 그 키를 지운다.',
      '첫 -F는 # Host 10.20.30.201 found로 시작하는 줄을 출력한다. -R은 known_hosts updated와 원래 내용을 known_hosts.old로 남겼다는 메시지를 출력한다. 마지막 -F는 아무것도 출력하지 않는다.'))

# ── 2.3 ──────────────────────────────────────────────────────
section('2.3  로그가 경보가 되는 과정',
    p('로그는 시스템이 남긴 활동 기록이다. bastion에서 실행되는 Wazuh 에이전트가 auth.log에 새로 기록된 줄을 읽어 Wazuh 매니저로 보낸다. 매니저는 디코더로 로그를 해석하고 탐지 규칙에 대조한다. 경보는 규칙이 일치한 결과를 조사할 수 있도록 저장한 기록이다.'),
    img(FIG+'detection.png','도식 2-3. 로그 분석과 경보 생성.'),
    h('디코더: 원문에서 값을 꺼낸다'),
    p('디코더는 로그 형식을 알아보고 필요한 값을 필드로 꺼내는 정의이다. Wazuh 4.10.0의 SSH 디코더는 두 단계이다. 부모 디코더 sshd는 프로그램 이름이 sshd로 시작하는 기록을 고른다. 하위 디코더 ssh-invfailed는 없는 계정의 인증 실패 메시지에서 계정과 주소를 꺼낸다. 다음은 하위 디코더의 정의이다. [2]'),
    code('<decoder name="ssh-invfailed">\n  <parent>sshd</parent>\n  <prematch>^Failed \\S+ for invalid user|…</prematch>\n  <regex offset="after_prematch">(\\S+) from (\\S+)</regex>\n  <order>srcuser,srcip</order>\n</decoder>'),
    p('prematch는 메시지 앞부분이 만족해야 하는 조건이다. 이 정규표현식에서 ^는 메시지의 시작, \\S+는 공백이 아닌 문자 1개 이상, 파이프(|)는 또는(OR)을 뜻한다. Failed 뒤의 \\S+에는 password 같은 인증 방식이 들어가고, | 뒤에는 옛 표기 illegal user에 대한 같은 조건이 이어진다.'),
    p('regex는 prematch에 일치한 부분 뒤에서 값을 꺼낸다(offset="after_prematch"). 괄호로 묶은 두 \\S+가 차례로 book03_probe와 10.20.30.254에 해당하고, order가 각각 srcuser와 srcip라는 이름을 붙인다. 경보에서는 data.srcuser와 data.srcip로 나타난다.'),
    img(FIG+'rev01-fields.png','도식 2-4. 원문에서 경보 필드로.'),
    p('경보의 decoder.name과 decoder.parent에는 모두 부모 이름 sshd가 표시되고, 하위 디코더 이름 ssh-invfailed는 나타나지 않는다. 원문의 sshd[7249]는 기록을 남긴 프로그램 이름이고, decoder.name의 sshd는 Wazuh가 이 기록을 해석한 디코더 이름이다. 값은 같아도 가리키는 대상이 다르다.'),
    h('탐지 규칙: 조건이 맞으면 번호를 붙인다'),
    p('탐지 규칙은 디코딩된 기록이 만족해야 할 조건과, 일치했을 때 붙일 번호·수준·설명을 정의한다. SSH 규칙도 부모와 하위로 이어진다. 다음은 두 규칙의 조건 부분이다. 규칙 5710에는 이 밖에 설명(description), MITRE ATT&CK 기법 번호, 그룹이 정의되어 있다. [3]'),
    code('<rule id="5700" level="0" noalert="1">\n  <decoded_as>sshd</decoded_as>\n</rule>\n\n<rule id="5710" level="5">\n  <if_sid>5700</if_sid>\n  <match>illegal user|invalid user</match>\n</rule>'),
    p('규칙 5700은 sshd 디코더로 해석한 기록(decoded_as)을 모두 묶는다. level="0"과 noalert="1"은 이 규칙만으로는 경보를 만들지 않는다는 뜻이다. 규칙 5710은 5700에 해당한 기록 중(if_sid) 메시지에 illegal user 또는 invalid user가 있는(match) 기록에 수준 5를 붙인다. 이 match에서도 파이프(|)는 또는(OR)이다.'),
    p('경보의 필드는 출처가 셋으로 나뉜다. 원문에서 디코더가 꺼낸 값, 기록을 보낸 수집기의 정보, 규칙에 미리 정해 둔 분류이다.'),
    tab(['필드','사례 값','출처'],[
        ['agent.name','bastion','수집기 · 에이전트 등록 이름'],
        ['agent.ip','10.20.30.201','수집기 · 에이전트 주소'],
        ['location','/var/log/auth.log','수집기 · 읽은 파일'],
        ['data.srcuser','book03_probe','원문 → 디코더'],
        ['data.srcip','10.20.30.254','원문 → 디코더'],
        ['full_log','원문 한 줄','원문'],
        ['rule.id · level','5710 · 5','규칙'],
        ['rule.description','sshd: Attempt to login using a non-existent user','규칙'],
        ['rule.groups','authentication_failed, invalid_login 등','규칙'],
        ['rule.mitre.id','T1110.001, T1021.004','규칙']],[32,55,40]),
    p('agent.ip는 기록을 보낸 bastion의 주소이고, data.srcip는 bastion에 접속한 쪽의 주소이다. 같은 경보 안의 두 IP가 서로 다른 장비를 가리킨다.'),
    p('rule.mitre.id의 T1110.001은 MITRE ATT&CK에서 암호 추측(Password Guessing) 기법의 번호이다. 이 번호는 규칙 5710에 일치하면 항상 붙는다. 실제 암호 추측 공격이었는지는 시도 횟수와 계정 목록을 확인한 뒤 판단한다. Wazuh 4.10.0에는 같은 출발지에서 5710이 짧은 시간 안에 반복되면(frequency 8, timeframe 120초) 수준 10의 규칙 5712를 붙이는 규칙도 있다. 5710 한 건만으로 반복 공격을 판단하지 않는다. [3]'),
    box('blind','규칙이 없거나 수준이 낮은 기록은 경보 인덱스(wazuh-alerts-*)에 저장되지 않는다. Wazuh 기본 설정의 저장 기준은 수준 3 이상이다. kt66은 들어온 모든 기록을 규칙과 관계없이 아카이브 인덱스(wazuh-archives-*)에도 저장하도록 설정한다. 경보 검색 결과가 0건이면 아카이브에서 원본 기록을 다시 찾는다. 검색 방법은 3장과 4장에서 다룬다. [1][4]'))

# ── 2.4 ──────────────────────────────────────────────────────
section('2.4  시각 맞추기',
    p('여러 서버의 기록을 연결하려면 시각을 같은 기준으로 맞춘다. UTC는 국제 표준 시각이고, 한국 표준시(KST)는 UTC보다 9시간 빠르다. 시각 뒤의 +0000·+00:00은 UTC, +0900·+09:00은 KST를 나타낸다.'),
    tab(['기록 위치','이 사례의 값'],[
        ['원문 시각 (auth.log)','Nov  1 14:22:35'],
        ['경보 timestamp','2026-11-01T05:22:36.778+0000'],
        ['timestamp를 KST로','2026-11-01 14:22:36.778']],[48,79]),
    box('caution','syslog 형식의 원문 시각에는 연도와 시간대가 없다. 기록한 서버의 시간대로 읽는다. kt66의 컨테이너는 VM의 시간대와 관계없이 Asia/Seoul로 설정되므로 bastion의 원문 시각은 KST이다. [1]'),
    p('원문 시각은 sshd가 기록한 시점이고 timestamp는 매니저가 처리한 시점이다. 이 사례에서는 약 2초 차이가 난다. 차이는 수집과 처리 상황에 따라 달라지므로 검색 범위는 앞뒤 몇 분으로 잡는다.'),
    p('kt66 VM의 시간대도 확인한다. VM의 시간대는 Ubuntu 설치 때 고른 지역을 따른다.'),
    c('timedatectl',
      'kt66 VM의 현재 시각과 시간대 설정을 확인한다.',
      'timedatectl은 시스템의 시각·시간대 설정을 조회하거나 바꾼다. 옵션 없이 실행하면 설정을 바꾸지 않고 현재 상태만 출력한다.',
      'Local time, Universal time, Time zone 줄을 읽는다. 설치 때 서울을 골랐다면 Time zone: Asia/Seoul (KST, +0900)이 나온다.'),
    c('date -Is\ndate -u -Is',
      '같은 순간을 KST와 UTC로 출력해 9시간 차이를 확인한다.',
      'date는 현재 시각을 출력한다. -I는 ISO 8601 형식이며 바로 뒤의 s는 초 단위까지 표시한다. -u는 UTC로 출력한다.',
      '첫 줄은 +09:00, 둘째 줄은 +00:00으로 끝나고 시각이 9시간 차이 난다.'),
    p('세 명령은 시각을 조회만 한다. 원상복구할 변경은 없다.'))

# ── 2.5 ──────────────────────────────────────────────────────
section('2.5  시도와 결과 구분',
    p('공격 시도는 권한 없는 접근이나 조작을 목표로 보낸 요청이다. 취약점은 공격에 악용될 수 있는 약점이고, 침입은 권한 없는 사용자가 실제로 시스템에 접근한 결과이다. 규칙 5710처럼 많은 경보는 시도를 기록한다. 시도가 성공했는지는 결과를 보여 주는 기록에서 따로 확인한다.'),
    tab(['구분','SSH 사례에서 확인할 기록'],[
        ['공격 시도','여러 계정·암호로 반복한 인증 실패 기록'],
        ['취약점','추측하기 쉬운 암호, 암호 로그인을 허용하는 설정'],
        ['침입 결과','권한 없는 사용자의 로그인 성공 기록']],[30,97]),
    img(FIG+'authentication.png','도식 2-5. 인증 결과와 추가 조사.'),
    p('Wazuh 4.10.0에서 sshd의 암호 인증 실패는 계정이 없으면 5710, 계정이 있으면 5760(sshd: authentication failed)으로 분류된다. 로그인 성공(Accepted …)은 5715(sshd: authentication success)이다. [3]'),
    box('blind','rule.id 5710만 검색하면 실제 계정으로 시도한 실패(5760)와 로그인 성공(5715)이 빠진다. 침입 여부를 확인할 때는 같은 출발지의 성공 기록을 함께 찾는다.'),
    h('웹 요청의 결과'),
    p('웹 서버는 HTTP 상태 코드로 요청 처리 결과를 알린다. 1장에서 설치한 curl로 kt66 웹 서버의 응답 헤더를 읽는다. 주소는 자신의 kt66 VM 주소로 바꾼다.'),
    c('curl -I --max-time 15 http://192.168.0.189/',
      'kt66 웹 서버 첫 화면의 상태 코드를 확인한다.',
      'curl은 HTTP 요청을 보내고 응답을 출력한다. -I는 본문 없이 응답 헤더만 요청하는 HEAD 방식이다. --max-time 15는 최대 실행 시간을 15초로 제한한다.',
      '첫 줄에서 HTTP 버전과 상태 코드를 읽는다. 기존 kt66의 첫 화면은 HTTP/1.1 200 OK를 반환했다.'),
    box('predict','다음 명령은 웹 서버에 없는 경로를 요청한다. 실행하기 전에 상태 코드를 예측한다.'),
    c('curl -I --max-time 15 http://192.168.0.189/book02-none',
      '없는 경로를 요청해 응답 코드가 어떻게 달라지는지 확인한다.',
      '주소 뒤의 /book02-none이 요청할 경로이다. 나머지 옵션은 C02-08과 같다.',
      '첫 줄의 상태 코드를 읽고 아래 표에서 뜻을 찾는다. 없는 자원을 요청하면 일반적으로 404 Not Found가 나온다.'),
    tab(['코드','뜻 · 다음 확인'],[
        ['200','요청을 처리했다. 공격이 목표를 달성했는지는 응답 본문과 서버 기록으로 확인한다.'],
        ['302','다른 주소로 이동시켰다. Location 헤더의 이동 주소를 확인한다. 로그인 실패 후 로그인 화면으로 되돌리는 경우도 있다.'],
        ['403','요청 수행을 거부했다. 웹 서버·접근 제어·WAF 중 어디에서 거부했는지 같은 시각의 기록을 대조한다.'],
        ['404','대상 자원을 찾지 못했다. 요청 경로와 서버 기록을 확인한다.']],[19,108]),
    p('WAF는 HTTP 요청을 검사해 공격으로 보이는 요청을 차단하는 웹 애플리케이션 방화벽이다. kt66은 ModSecurity를 WAF로 사용한다. 상태 코드는 서버가 요청을 어떻게 처리했는지 알려 줄 뿐, 공격의 성공 여부를 알려 주지 않는다. 로그인에 실패한 화면도 200으로 응답할 수 있다. [5]'),
    p('연결 오류가 나면 VM 주소 → kt66 기동 상태(1.6) 순서로 확인한다. 두 요청은 서버 설정을 바꾸지 않는다.'))

# ── 2.6 ──────────────────────────────────────────────────────
section('2.6  관제에서 대응까지',
    p('보안관제는 기록과 경보를 확인해 조사할 대상을 찾고 영향을 판단하는 업무이다. 침해대응은 확인한 피해의 확산을 막고 시스템을 복구하는 활동이다. 두 업무는 다음 순서로 이어진다.'),
    img(FIG+'response.png','도식 2-6. 조사와 대응 순서.'),
    tab(['단계','SSH 사례의 확인 행동'],[
        ['기록 확인','계정·출발지·시각·인증 결과를 읽는다.'],
        ['범위 조사','같은 출발지의 다른 계정 시도, 로그인 성공, 이후의 명령 실행과 파일 변경을 찾는다.'],
        ['대응 결정','계정 소유자와 승인된 작업을 확인한다. 침해가 확인되면 해당 계정과 접속 경로를 통제한다.'],
        ['복구·재확인','변경된 설정을 복구하고 정상 접속과 로그 수집을 다시 확인한다.']],[30,97]),
    p('로그인 실패 기록은 정상 사용자의 입력 실수로도 생긴다. 계정 소유자의 설명과 접속 이력이 일치하면 그 근거를 조사 기록에 남기고 사건 분류를 정정한다.'),
    box('field','경보 한 건마다 사실·판단·다음 확인을 나누어 적어 두면 담당자가 바뀌어도 기록만 보고 조사를 이어 갈 수 있다. 판단을 바꿀 때는 무엇을 새로 확인했는지도 함께 적는다.'),
    h('경보가 없을 때'),
    p('경보가 없다는 것은 공격이 없었다는 뜻이 아니다. 기록이 어디까지 전달되었는지 다음 순서로 확인한다.'),
    ol('에이전트 연결: 기록을 보내는 에이전트가 active인가(1.7)',
       '원본 로그: 서버에 기록 자체가 남았는가(2.2의 방법)',
       '수집 설정: 그 파일이 수집 대상인가(4장)',
       '탐지 규칙: 일치하는 규칙이 있고 수준이 저장 기준 이상인가(2.3)',
       '검색 범위: 인덱스·기간·검색 조건이 맞는가(3장)'))

# ── 2.7 ──────────────────────────────────────────────────────
section('2.7  조사 기록 쓰기',
    p('조사 기록에는 확인한 사실과 판단을 나누어 적는다. 사실은 기록에 있는 값과 그 출처이고, 판단은 사실을 근거로 내린 결론이다. 근거가 부족한 판단은 적지 않고 추가 조사 항목으로 남긴다. 2.1의 사례를 다음과 같이 정리한다.'),
    tab(['항목','사례 기록'],[
        ['대상·위치','bastion · /var/log/auth.log'],
        ['원문 시각','11월 1일 14:22:35 (KST)'],
        ['출발지·계정','10.20.30.254(kt66 VM의 ext망 주소) · book03_probe'],
        ['확인한 사실','존재하지 않는 계정으로 접속했고 암호 인증에 실패했다.'],
        ['탐지 근거','규칙 5710 · 수준 5'],
        ['기록 식별','wazuh-alerts-4.x-2026.11.01 · WfiPlaEBEYWT20nnUNlQ'],
        ['추가 조사','kt66 VM에서 같은 시각의 접속, 같은 출발지의 다른 계정 실패(5760)와 성공(5715)'],
        ['현재 판단','로그인 시도 1건 확인. 침입 여부는 미확인.']],[30,97],keep=True),
    p('기록 식별의 두 값은 경보 JSON의 _index와 _id이다. _index는 경보가 저장된 인덱스 이름이고, _id는 그 안에서 경보를 구분하는 식별자이다.'),
    h('사실과 판단 구분'),
    tab(['문장','구분 · 이유'],[
        ['10.20.30.254에서 book03_probe로 암호 인증이 실패했다.','사실 · 원문에 있다.'],
        ['공격자가 bastion에 무차별 대입 공격을 했다.','판단 · 반복 횟수의 근거가 없다.'],
        ['공격자의 IP는 10.20.30.254이다.','판단 · 이 주소는 kt66 VM이다(2.2).'],
        ['침입은 없었다.','판단 · 성공 기록을 아직 찾지 않았다.']],[70,57],keep=True),
    p('사건 노트의 조사 기록에는 1.8의 형식에 맞춰 한 줄로 요약한다.'),
    code('14:22:36 | bastion | 5710 | 10.20.30.254 |\n없는 계정 book03_probe 암호 인증 실패 |\nwazuh-alerts-4.x-2026.11.01 · WfiPlaEBEYWT20nnUNlQ'),
    p('빈 조사 기록 양식은 examples/rev01/chapter02/investigation.txt에 있다. 3장에서는 Wazuh 화면에서 이 경보와 2.2에서 직접 남긴 기록을 검색한다.'),
    {'type':'image','path':'assets/illustrations/chapter02/evidence.png','caption':'삽화. 기록 대조.','width_mm':45,'align':'right'})

# ── 장 끝 ─────────────────────────────────────────────────────
page('2장 정리',
    h('핵심 정리'),
    ul('경보 한 건은 규칙 조건이 기록과 일치했다는 사실을 알려 준다. 공격의 성공 여부, 접속자, 시도 횟수는 다른 기록에서 확인한다.',
       '디코더는 원문에서 계정·주소 같은 값을 꺼내고, 탐지 규칙은 조건에 맞는 기록에 번호와 수준을 붙인다. 경보 필드는 원문·수집기·규칙 중 어디에서 왔는지 구분해 읽는다.',
       '출발지 IP는 접속 경로의 단서이다. kt66 VM에서 bastion에 접속하면 VM의 ext망 주소 10.20.30.254가 기록된다.',
       '조사 기록에는 사실과 판단을 나누어 적고, 근거가 부족한 판단은 추가 조사 항목으로 남긴다.'),
    h('확인 문제'),
    ol('2.1의 기록만 보고 “bastion은 침입당하지 않았다”고 쓸 수 있는가?',
       'Failed password for invalid user admin from 10.20.30.254 port 41022 ssh2에서 data.srcuser와 data.srcip가 될 값은 무엇인가?',
       '경보의 rule.mitre.id에 T1110.001이 있다. 이 경보를 암호 추측 공격으로 확정할 수 있는가?',
       'bastion의 원문 시각 Nov  1 14:22:35를 UTC로 바꾸면 몇 시인가?',
       '웹 공격 요청에 200 OK가 돌아왔다. 공격이 성공했다고 볼 수 있는가?'),
    h('확인 문제 해설'),
    ol('쓸 수 없다. 이 줄은 실패 한 건만 보여 준다. 같은 출발지의 성공 기록(5715)과 다른 계정의 기록을 확인하기 전까지 침입 여부는 미확인이다.',
       'srcuser는 admin, srcip는 10.20.30.254이다. 하위 디코더의 regex (\\S+) from (\\S+)가 prematch 뒤에서 두 값을 꺼낸다.',
       '확정할 수 없다. 기법 번호는 규칙 5710에 미리 붙은 분류이다. 시도 횟수와 계정 목록을 확인한 뒤 판단한다.',
       'Nov  1 05:22:35(UTC)이다. kt66 컨테이너는 KST로 기록하므로 9시간을 뺀다.',
       '볼 수 없다. 200은 서버가 요청을 처리했다는 뜻이다. 응답 본문과 서버의 실행·변경 기록을 확인해야 한다.'),
    h('더 읽을거리'),
    p('Wazuh 4.10 공식 문서의 규칙 문법이다. 2.3에서 본 if_sid, match, frequency, timeframe, noalert의 정의를 확인한다.'),
    link('Wazuh 4.10 · Rules Syntax','https://documentation.wazuh.com/4.10/user-manual/ruleset/ruleset-xml-syntax/rules.html'),
    p('MITRE ATT&CK의 암호 추측 기법 설명이다. 탐지 방법(Detection) 항목에서 인증 기록을 어떻게 쓰는지 읽는다.'),
    link('MITRE ATT&CK · T1110.001 Password Guessing','https://attack.mitre.org/techniques/T1110/001/'))

section('2장 참고 자료',
    p('사례: 2026년 11월 1일 기존 kt66에서 조회한 SSH 인증 실패 경보. 원문과 필드는 examples/rev01/chapter02/case-ssh.json에 있다.'),
    h('[1] kt66 기준 소스'),
    p('bastion의 주소와 컨테이너 시간대는 docker-compose.yaml, 내부망 .254 주소는 kt66-net.sh, 아카이브 인덱스 설정은 siem/87-archives.sh에 있다.'),
    link('kt66 · docker-compose.yaml',KT66+'/docker-compose.yaml'),
    link('kt66 · kt66-net.sh',KT66+'/kt66-net.sh'),
    link('kt66 · siem/87-archives.sh',KT66+'/siem/87-archives.sh'),
    h('[2] Wazuh 4.10.0 SSH 디코더'),
    link('0310-ssh_decoders.xml · ssh-invfailed',WAZUH+'/decoders/0310-ssh_decoders.xml'),
    h('[3] Wazuh 4.10.0 SSH 규칙'),
    link('0095-sshd_rules.xml · 5700, 5710, 5712, 5715, 5760',WAZUH+'/rules/0095-sshd_rules.xml'),
    h('[4] Wazuh 경보 저장 기준'),
    link('Wazuh · ossec.conf alerts · log_alert_level','https://documentation.wazuh.com/current/user-manual/reference/ossec-conf/alerts.html'),
    h('[5] HTTP 상태 코드'),
    link('RFC 9110 · HTTP Semantics · Section 15','https://www.rfc-editor.org/rfc/rfc9110.html#section-15'))

INVESTIGATION='''조사 기록 · 경보 한 건

대상·위치            :
원문 시각·시간대     :
출발지·계정          :
확인한 사실          :
탐지 근거(rule.id·수준):
기록 식별(_index·_id):
추가 조사            :
현재 판단            :
'''
README='''2장 REV01 복사용 명령과 사례 자료

C02-01~09 : 명령 블록 번호와 같은 파일. 실행 위치는 manifest.json의 where를 따른다.
case-ssh.json : 기존 kt66에서 조회한 경보 원본(읽기 자료)
case-ssh.log  : 경보의 full_log 원문 한 줄(읽기 자료)
investigation.txt : 조사 기록 양식

사례 파일은 읽기 자료이며 셸 명령이 아니다.
'''

if __name__=='__main__':
    data={'title':'공격과 보안관제의 기초','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','baseline':COMMIT,'revision':'REV01',
          'comments':'REV01 원고. 디코더·규칙은 Wazuh v4.10.0 ruleset, kt66 사실은 63d4180 소스와 대조. 2.2 직접 실습은 새 VM에서 실행 검증 전.','pages':pages}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'volume01-chapter02.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    EX.mkdir(parents=True,exist_ok=True)
    for old in EX.glob('C02-*.txt'):old.unlink()
    for cmd in commands:(EX/(cmd['id']+'.txt')).write_text(cmd['text']+'\n')
    (EX/'manifest.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
    for name in ['case-ssh.json','case-ssh.log']:shutil.copyfile(ROOT/'examples/chapter02'/name,EX/name)
    (EX/'investigation.txt').write_text(INVESTIGATION)
    (EX/'README.txt').write_text(README)
    print(len(pages),'pages',len(commands),'commands')
