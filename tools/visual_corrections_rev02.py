"""전체 지면 대조에서 발견한 참조·문장·설명 순서를 교정한다."""
import json,re
from pathlib import Path
from revise_volume01_rev02 import ROOT, OUT, ED, write, strings

PURPOSE = {
    'C04-11': '존재하지 않는 계정의 로그인 실패를 분류하는 하위 디코더 정의를 읽는다.',
    'C04-15': 'SSH 규칙의 상위 정의인 5700의 조건을 읽는다.',
    'C04-45': '아카이브 저장과 경보 저장의 최소 수준 설정을 확인한다.',
    'C04-46': 'Filebeat가 아카이브 파일을 전송하도록 설정됐는지 확인한다.',
    'C05-09': 'Apache 접속 로그를 수집하는 localfile 설정을 확인한다.',
    'C05-14': '웹 공격을 분류하는 규칙 31104의 조건을 읽는다.',
    'C08-11': 'bastion의 ccc 계정으로 정상 로그인할 수 있는지 확인한다.',
    'C08-37': '원상복구한 뒤 임시 암호를 사용한 root 접속이 거부되는지 확인한다.',
    'C08-04': '실습 대상 서버의 이름과 유효 SSH 인증 설정을 확인한다.',
    'C09-03': 'bastion의 에이전트 실행 상태와 sudo 권한 파일의 문법을 확인한다.',
    'C09-15': '기존 SSH 키 파일의 권한과 백업 대상의 상태를 기록한다.',
    'C09-24': '예약 작업을 실행할 도구와 cron 서비스의 준비 상태를 확인한다.',
    'C09-32': '예약 시각과 실제 실행 결과를 대조한다.',
    'C09-47': '경보에 연결된 감사 이벤트의 원문을 읽는다.',
    'C09-48': '같은 시각·PID의 Sysmon 기록으로 프로그램과 부모 프로세스를 대조한다.',
    'C10-01': '조사할 호스트와 시각을 기록하고 필요한 도구·수집 서비스가 준비됐는지 확인한다.',
    'C10-14': 'kt66의 방화벽 규칙과 공격자 VM으로 향하는 경로를 확인한다.',
    'C10-15': '현재 방화벽 규칙을 보존한 뒤 누락된 실습용 체인을 준비한다.',
    'Q10-01': '리스닝 목록이 바뀐 경보를 조사 대상 호스트로 좁힌다.',
    'Q10-02': '현재·이전 출력에서 실습 포트의 등장과 사라짐을 비교한다.',
    'C10-42': '조회 서비스와 에이전트 로그에서 수집 실패 원인을 찾는다.',
    'C10-44': '패킷·리스닝 목록·예약 조회의 원문을 해석하는 디코더와 규칙을 확인한다.',
    'C11-01': '새 분석 디렉터리의 이름이 비어 있고 원본 사례 파일이 준비됐는지 확인한다.',
}
REPLACE = {
    'C01-07~13': 'C01-07~12', 'C01-14~19': 'C01-13~19',
    'A.7~A.11': 'A.7~11',
    '앞 페이지의 규칙 번호로': '화면 4-4의 규칙 번호로',
    '앞 페이지에서 접속한 kt66-web': 'C05-06으로 접속한 kt66-web',
    '앞 페이지의 응답 표시·시간 제한 옵션': 'C05-27의 응답 표시·시간 제한 옵션',
    '검증 환경의 Wazuh 결과': '사례 기록의 Wazuh 결과',
    '이 실습의 두 요청은 WAF에서 차단되었다.': '제시한 사례의 두 요청은 WAF에서 차단되었다.',
    '다음 지면의 방법으로 서버 키 지문을 대조한다.': '8.2의 서버 키 지문 확인 절차로 대조한다.',
    '각 장 참고자료에 수록': '권말 참고문헌에 수록',
    '슬라이드의 URL 검색 중': 'URL 검색에서는',
    '슬라이드 변형의 응답은': '제시한 변형 요청의 응답은',
    '슬라이드의 200과': '제시한 사례의 200과',
    '슬라이드의 이 요청은': '제시한 사례의 이 요청은',
    '검증 환경에서는': '제시한 사례에서는',
    '촬영 환경에서는': '제시한 사례에서는',
    '촬영 환경의': '제시한 사례의',
    '촬영 기록에서는': '제시한 사례에서는',
    '다음 지면에서 확인한다.': 'C08-31에서 확인한다.',
    '앞 지면에서 대상 이름·경로가 없는 것을 확인한 뒤': 'C08-45로 대상 이름·경로가 없는 것을 확인한 뒤',
    '8.2의 서버 키 지문 확인 절차로 대조한다.': 'C08-12의 서버 키 지문과 대조한다.',
    '촬영 환경에서 확인한 설정': '사례의 수집 설정',
    '본문 촬영 구간 전체에는': '사례의 전체 조회 구간에는',
    '촬영 구간': '사례 조회 구간',
    '촬영 환경은': '제시한 사례에서는',
    '촬영 준비 시 키는': '이 사례의 수집 준비 당시 키는',
    '촬영 경보의': '사례 경보의',
    '촬영한 파이프 실행의': '사례에 제시한 파이프 실행의',
    '촬영 컨테이너에는': '사례의 컨테이너에는',
    '촬영 값은': '사례의 값은',
    '촬영 기간의 결과': '사례 조회 기간의 결과',
    '등록 인증 정책이 다른 환경은 3장의 해당 설정을 따른다.': '등록 인증 정책이 다른 환경은 1.7과 A.6의 등록 설정을 확인한다.',
    '대괄호 [11-0]은 첫 요소': '대괄호 안의 0([0])은 첫 요소',
    'sshd[2-7249]': 'sshd[7249]',
    'sshd[4-7249]': 'sshd[7249]',
}
INTROS = {
    'b': '명령의 역할과 기본 구문을 다시 찾을 때 사용한다. 입력 번호로 본문의 실행 위치와 확인 절차를 찾아 함께 읽는다.',
    'c': '실습 전후의 상태를 대조하고 이번에 바꾼 항목만 원상복구한다. 결과가 다르면 증상에 맞는 확인 순서로 원인을 좁힌다.',
    'd': '로그와 경보에서 자주 쓰는 용어·필드를 찾아본다. 같은 값이라도 원본 로그와 수집 위치에 따라 뜻이 달라질 수 있으므로 사례의 문맥과 함께 읽는다.',
    'e': '실행한 행동, 기록에서 확인한 사실, 분석가의 판단을 나누어 적는다. 각 사례에 같은 번호를 붙여 실행 일지와 조사 기록을 대조한다.',
    'f': '본문의 실습을 원자료와 연결하고 ATT&CK의 행동 분류와 대조한다. 학습한 범위와 실제로 탐지를 확인한 범위는 구분한다.',
}

def main():
    edits=[]
    for src in sorted(OUT.glob('*.json')):
        d=json.loads(src.read_text('utf8'));before=json.dumps(d,ensure_ascii=False)
        for old,new in REPLACE.items(): d=strings(d,lambda s:s.replace(old,new))
        if src.stem.startswith('volume01-chapter'):
            d=strings(d,lambda s:s.replace('examples/chapter','examples/rev02/chapter').replace('examples\\chapter','examples\\rev02\\chapter'))
        if src.stem=='volume01-chapter08':
            for n,section in [(16,'8.2'),(17,'8.3'),(18,'8.4'),(19,'8.5'),(20,'8.6'),(21,'8.7')]:
                d=strings(d,lambda s:s.replace(f'실습 {n}은','이번에는').replace(f'실습 {n}는','이번에는').replace(f'실습 {n}과',section+'와').replace(f'실습 {n}와',section+'와').replace(f'실습 {n}의',section+'의'))
        if src.stem=='volume01-chapter09':
            for old,new in [('실습 22~24는','9.2~9.4에서는'),('실습 25·26 실행','9.5·9.6 실행'),('실습 22·23·24·28','9.2·9.3·9.4·9.8'),('실습 27 ·','9.7 ·')]:d=strings(d,lambda s:s.replace(old,new))
        if src.stem=='volume01-chapter10':
            for n in [29,30,62]:d=strings(d,lambda s:s.replace(f'실습 {n}는','이번에는').replace(f'실습 {n}은','이번에는'))
        for p in d['pages']:
            blocks=p['blocks']
            for b in blocks:
                if b.get('id') in PURPOSE and b.get('purpose')!=PURPOSE[b['id']]:
                    old=b.get('purpose','')
                    b['purpose']=PURPOSE[b['id']]
                    b['syntax']=(old+' '+b.get('syntax','')).strip()
                if b.get('id')=='CA-05':
                    b['result']=b['result'].replace('1.5','A.14')
                if b.get('id')=='C02-02':b['syntax']='docker exec -it의 역할은 C02-P1에서 설명했다. kt66-bastion의 /bin/bash를 연다.'
                if b.get('id')=='C02-04':b['syntax']='C02-P4와 같이 셸을 종료한다. 프롬프트로 실행 위치를 확인한다.'
                if b.get('id')=='C08-11':
                    b['text']='ssh -p 2204 -o HostKeyAlgorithms=ssh-ed25519 \\\n  ccc@192.168.0.107'
                    b['syntax']='-p 2204는 접속할 서버 포트이다. -o는 SSH 설정을 지정하며 HostKeyAlgorithms=ssh-ed25519는 서버 확인에 Ed25519 키를 사용한다. 줄 끝 역슬래시(\\)는 다음 줄을 잇는다. bastion의 ccc 계정으로 접속한다. 첫 접속 안내가 나오면 승인하기 전에 별도 관리 창에서 C08-12를 실행해 지문을 대조한다.'
                if b.get('id')=='C09-31' and '예약식 전체' not in b.get('syntax',''):
                    b['syntax']=b.get('syntax','')+' 작은따옴표 안의 예약식 전체는 한 줄이다. 지면에서 줄이 나뉘어 보이면 복사용 C09-31.txt와 대조한다.'
                if b.get('id')=='C09-31' and 'purpose' not in b:
                    b['purpose']='실습용 스크립트를 매분 실행하는 예약 작업을 등록한다.'
                    b['syntax']=(b.pop('why','')+' '+b.get('syntax','')).strip()
                # 교정 과정의 이전 목적 문구가 구문에 중복되지 않게 한다.
                for previous in ('접속한 서버와 계정이 실습 대상인지 확인한다. ', 'bastion의 에이전트가 실행 중이며 조사 대상 경로를 감시하는지 확인한다. ', '같은 시간대의 로그인 세션과 명령 실행 기록을 대조한다. '):
                    if 'syntax' in b:b['syntax']=b['syntax'].replace(previous,'')
                if b.get('type')=='image' and b.get('path')=='assets/figures/chapter01/rev01-roadmap.png':
                    b['path']='assets/figures/rev02/chapter01-path.png';b['width_mm']=127
                if b.get('type')=='image' and b.get('path') in [f'assets/figures/chapter{n:02}/roadmap.png' for n in (8,9,10)]:
                    b['path']='assets/figures/rev02/'+src.stem.replace('volume01-','')+'-path.png'
                if b.get('id')=='C07-26':b['text']=b['text'].replace("  -H 'X-Api-Version:","  -H \\\n'X-Api-Version:")
                if b.get('type')=='table':
                    for row in b['rows']:
                        for i,s in enumerate(row):
                            if src.stem=='volume01-chapter09':
                                for number,section in [(22,'9.2'),(23,'9.3'),(24,'9.4'),(25,'9.5'),(26,'9.6'),(27,'9.7'),(28,'9.8')]:
                                    if s.startswith(f'{number} ·'):row[i]=s.replace(f'{number} ·',section+' ·',1)
                            if 'known_hosts에 추가된 bastion 키는 C02-05로 지운다' in s:
                                row[i]='이번에 새로 추가한 bastion 키를 제거하려면 C02-05를 사용한다. 기존 known_hosts 항목은 유지한다.'
                if b.get('type')=='p' and '8~10장의 저자 실습에는' in b.get('text',''):
                    b['text']='실습을 마치면 도구·센서·검색 패턴 가운데 유지할 항목과 되돌린 항목을 구분해 기록한다.'
            # 일러두기의 편집자용 표기 규칙은 저자 기록으로 옮긴다.
            for i in range(len(blocks)-2,-1,-1):
                if blocks[i].get('text')=='표기 원칙' and blocks[i+1]['type']=='table':
                    write(ED/'style-table-from-preface.json',blocks[i:i+2]);del blocks[i:i+2]
            # 입력 전에 옵션을 읽는다. 표 안의 결과 해석 표는 이동하지 않는다.
            for i in range(len(blocks)-1):
                b,t=blocks[i:i+2]
                if b.get('id') in ('C01-12','C04-05') and t['type']=='table':
                    blocks[i:i+2]=[t,b]
                    for k in ('why','purpose','syntax'):
                        if k in b:b[k]=b[k].replace('아래 옵션','설명한 옵션').replace('아래 표','앞 표')
            if src.stem=='volume01-chapter04' and p==d['pages'][0]:
                p['blocks']=[b for b in blocks if b.get('text')!='준비와 완료 기준']
        if src.stem.startswith('volume01-appendix-'):
            letter=src.stem[-1]
            for b in d['pages'][0]['blocks']:
                if b.get('text')=='실습 중 필요한 항목을 찾아 확인하고, 변경 전후의 상태와 근거를 기록한다.' and letter in INTROS:
                    b['text']=INTROS[letter]
        if src.stem.startswith('volume01-chapter'):
            ending={b['text'] for b in d['pages'][-1]['blocks'] if b['type']=='p'}
            for p in d['pages'][:-1]:
                p['blocks']=[b for b in p['blocks'] if not(b['type']=='p' and b['text'] in ending and b['text'].startswith(tuple(str(n)+'장에서는' for n in range(2,12))))]
        if json.dumps(d,ensure_ascii=False)!=before:edits.append(src.name);write(src,d)
    write(ED/'visual-corrections.json',{'documents':edits,'purpose_corrected':list(PURPOSE),'scope':'문장·참조·설명 순서의 정적 교정. 명령 실행 없음.'})
    print('Visual review corrections:',len(edits))

if __name__=='__main__':main()
