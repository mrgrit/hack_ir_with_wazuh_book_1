5장 복사용 자료

본문은 브라우저 실습이며 curl은 5.13의 선택 실습이다.
B05-01~08: 브라우저 주소·입력값. browser-inputs.json에 목록이 있다.
SQL 입력 B05-03-sqli.txt는 -- 뒤의 공백 한 칸까지 복사한다.
B05-05·07은 물음표 뒤 쿼리 값, B05-06·08은 전체 URL이다.
본문에서 나눈 두 줄은 복사용 파일에서는 한 줄로 제공한다.
DVWA 주소는 http://dvwa.ccc.com이며 kt66 VM은 192.168.0.107이다.

C05-01~37.txt: 터미널 명령. 실행 위치와 설명은 manifest.json과 본문을 따른다.
Q05-01~07.txt: Discover DQL 검색식. 인덱스 패턴은 queries.json에 있다.
browser/: 기존 브라우저 실습에서 수집한 접속 로그·Wazuh 문서·SQL WAF 기록의 교육용 사본.
investigation.txt: 실습 결과 기록 양식.

book05-*.log / .json: 앞서 검증한 curl 요청의 원문·Wazuh 기록. 선택 실습의 참고 자료이다.
브라우저 검증은 로그인 후 정상 요청 200, 공격 요청 403이었다.
curl 검증은 로그인 쿠키 없이 정상 요청 302, 공격 요청 403이었다.
두 검증의 날짜·시각과 출발지는 각 원문과 editorial 기록에 따로 남겼다.
WAF 자료는 세션 식별자가 포함된 헤더와 원문을 제외하고 분석 필드를 보존했다.

REV02 자료 관리: 책의 고정 실습 주소와 도메인에 맞춰 예제의 해당 문자열을 통일했다.
통일 전 원문과 변경 해시는 editorial/REV02/original-example-values 및 example-value-provenance.json에 보존한다.
주소 통일은 편집 변환이며 새 실습 실행 결과를 의미하지 않는다.
