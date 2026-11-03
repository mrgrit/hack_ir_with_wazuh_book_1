REV02 복사용 입력과 조사 자료

input-index.csv에서 문서·절·입력 번호·실행 위치·파일 경로를 찾는다.
입력은 본문의 선행 조건을 확인하고 한 명령씩 실행한다. 장 전체를 일괄 실행하는 스크립트가 아니다.
1장 상세 설치 입력은 부록 A로 이동했으며 C01 파일은 chapter01에 유지한다.
공통 실행 일지·조사 기록 양식은 casebook.txt이다.

기존 사례 데이터:
- chapter02/case-ssh.log, case-ssh.json: SSH 원문과 경보
- chapter04/*.log: Ruleset Test 입력
- chapter05/browser/*.log: 브라우저 요청 사례 원문
- chapter06/records/*.log: 요청 종류별 사례 원문
- chapter11/evidence/: 8~10장의 발췌 증거와 출처·해시 manifest

이 자료는 책과 같은 원문을 읽는 분석 과제에 쓴다. 전체 SIEM 인덱스나 VM 스냅샷이 아니며,
파일을 복사하는 것만으로 Discover에 같은 시각·문서 수가 만들어지지는 않는다.
자신이 실행한 요청은 자신의 시각과 주소로 검색한다. 사례 데이터와 실제 실행 결과를 구분해 기록한다.

기존 manifest와 README에 있는 검증 일자는 해당 원본 시험의 이력이다.
REV02가 새로 실행했다는 뜻은 아니다. 최종 입력 위치는 input-index.csv를 따른다.
