"""장말 자료에 구체적인 읽을 이유를 붙이고 중복 안내를 줄인다."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
READINGS = {
1: [
'Wazuh의 Components에서 Agent·Server·Indexer·Dashboard의 역할을 도식 1-3과 대조한다.',
'Docker의 What is a container?에서 컨테이너와 가상머신의 차이를 읽는다. kt66 README는 설치한 서비스와 접속 주소를 다시 찾을 때 쓴다.'
],
2: [
'Wazuh 4.10의 Rules Syntax에서 2.3에 나온 if_sid, match, frequency, timeframe, noalert의 정의를 확인한다.',
'MITRE ATT&CK의 T1110.001 Password Guessing에서 암호 추측의 행동 특성을 읽고, 한 번의 로그인 실패만으로 구분하기 어려운 이유를 설명한다.'
],
3: [
'OpenSearch 2.16의 Dashboards Query Language에서 와일드카드·날짜 범위·중첩 필드 검색을 읽고 3.4의 조건을 변형한다.',
'Wazuh 4.10의 Event logging에서 경보 파일과 아카이브 파일의 차이, wazuh-archives-* 검색을 위한 설정을 3.2와 대조한다.'
],
4: [
'Wazuh의 Log data collection: How it works에서 원본 로그가 수집기로 전달되는 과정을 읽고 4장의 수집 경로를 다시 그린다.',
'Wazuh의 localfile 설명에서 location과 log_format의 역할을 확인한다. 파일이 존재하는 것과 그 파일을 수집하도록 설정한 것을 구분한다.'
],
5: [
'DVWA 공식 저장소의 설치 안내에서 데이터베이스 초기화와 보안 수준 설정의 선행 조건을 확인한다.',
'DVWA의 SQL injection low.php에서 브라우저의 입력값이 SQL 문에 들어가는 위치를 찾는다. 접속 로그의 요청 문자열과 서버가 처리하는 값을 나누어 읽는다.'
],
6: [
'Chrome DevTools의 Network 안내에서 요청·응답 헤더와 이동 경로를 확인하는 방법을 읽는다. HTTP 상태 코드만으로 인증 결과를 판단하기 어려운 사례에 적용한다.',
'Gobuster 2.0.1 README에서 사전 파일과 응답 코드 선택 옵션을 확인한다. 사전에 없는 경로가 검색 결과에 나타나지 않는 이유를 설명한다.'
],
7: [
'Apache HTTP Server 2.4의 Log Files에서 접속 로그 형식에 포함되는 항목을 읽는다. 요청 본문이나 서버의 프로세스 실행을 확인하려면 어떤 기록이 더 필요한지 구분한다.',
'OWASP의 File Upload Cheat Sheet에서 확장자·내용·저장 위치·실행 권한을 각각 검토하는 이유를 읽는다. 파일 업로드 성공과 서버 실행 성공을 나누어 판단한다.'
],
8: [
'Ubuntu 22.04의 ssh 사용 설명서에서 클라이언트 인증 옵션을, sshd와 sshd_config에서 서버의 유효 설정과 인증 조건을 확인한다.',
'Wazuh 4.10.0 SSH 규칙에서 단일 실패와 반복 실패 규칙의 관계를 읽는다. frequency와 timeframe의 조건을 실제 검색 시간 범위와 구분한다.'
],
9: [
'Wazuh의 syscheck 설정에서 감시 경로와 검사 방식을 확인한다. 파일이 바뀌었다는 기록으로 그 파일의 실행까지 알 수 있는지 판단한다.',
'Wazuh의 FIM 고급 설정에서 변경 내용과 실행 주체를 조사하는 데 필요한 설정을 읽는다. 현재 실습에서 실제 수집한 필드와 대조한다.'
],
10: [
'기준 커밋의 kt66 호스트 센서·예약 조회 설정에서 조회 대상과 실행 간격을 확인한다. 직접 실행한 SQL 결과와 예약 실행 결과가 기록되는 위치를 비교한다.',
'osquery의 결과 로그 설명에서 added·removed와 snapshot의 차이를 읽는다. 한 시점의 조회 결과를 계속 유지된 상태로 해석하지 않도록 비교 시점을 기록한다.'
],
11: [
'NIST SP 800-61 Rev. 3에서 사고 대응을 준비·탐지·대응·복구 활동에 연결하는 관점을 읽는다. 이번 조사에서 확정한 사실과 추가 확인이 필요한 판단을 나누어 대응 근거를 점검한다.',
'Wazuh의 Event logging에서 경보와 원본 이벤트의 보존 경로를 다시 확인한다. 발췌 파일만 보존했을 때 놓칠 수 있는 조사 범위를 적는다.'
]}

def main():
    for chapter, paragraphs in READINGS.items():
        path = ROOT / f'manuscript/REV02/volume01-chapter{chapter:02}.json'
        data = json.loads(path.read_text('utf8'))
        blocks = data['pages'][-1]['blocks']
        start = next(i for i,b in enumerate(blocks) if b.get('text') == '더 읽을거리')
        data['pages'][-1]['blocks'] = blocks[:start+1] + [
            {'type':'p','text':f'자료의 전체 주소는 권말 참고문헌 {chapter}장에서 찾는다.'},
            *[{'type':'p','text':p} for p in paragraphs]
        ]
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
    print('11 chapter reading notes revised')

if __name__ == '__main__':
    main()
