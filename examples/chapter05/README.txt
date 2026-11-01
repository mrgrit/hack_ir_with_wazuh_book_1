5장 복사용 자료

C05-01~37.txt: 본문의 개별 터미널 명령. 실행 위치와 설명은 manifest.json과 본문을 따른다.
Q05-01~07.txt: Discover에 입력하는 DQL 검색식. 인덱스 패턴은 queries.json에 기록했다.
book05-normal.log / .json: 정상 id=1 요청의 실제 접속 로그·아카이브 문서.
book05-sqli.log / .json: SQL 구문 요청의 실제 접속 로그·아카이브 문서.
book05-xss.log / .json: 스크립트 요청의 실제 접속 로그·아카이브 문서.
book05-path.log / .json: 경로의 슬래시를 %2F로 인코딩한 요청의 실제 기록.
book05-path-raw.log / .json: 슬래시를 그대로 보낸 요청의 실제 기록.
book05-sqli-waf.json: SQL 요청과 대응하는 실제 ModSecurity 감사 기록의 아카이브 문서.
investigation.txt: 실습 결과 기록 양식.

검증 일시: 2026-11-01 20:13~20:18 KST.
검증 주소: kt66 192.168.0.189, 공격자 192.168.0.202, DVWA dvwa.ccc.com.
본문 예시 dvwa.kt66.lab은 자신의 .env LAB_DOMAIN에 맞춰 바꾼다.
공격 요청은 WAF에서 차단됐다. 로그의 공격 분류와 실제 침투 성공 여부를 구분한다.
계정·암호 목록은 이후 인증 공격 실습에서 준비한다.
