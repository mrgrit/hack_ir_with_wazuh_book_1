# 9장 복사용 예제

본문의 C09·Q09 번호와 일치한다. commands.txt는 전체 실행 스크립트가 아니다. 실행 위치·사전 확인·정상 결과·원상복구를 읽고 한 블록씩 사용한다. 공개 키 붙여 넣기와 Ctrl+D, nc 연결 창의 입력은 대화형 단계이다.

DQL은 Discover의 wazuh-alerts-*용이다. 날짜·시간대, 주소, agent.name과 PID·세션·이벤트 번호를 자신의 값으로 바꾼다. 기본 실습망은 kt66 192.168.0.107, 별도 공격자 192.168.0.108이다. 22번 포트는 호스트, 2204는 bastion이다.

x.sh와 a.sh는 사용자·호스트 이름만 출력하는 HTTP 제공 파일이다. 본문의 here-document와 동일한 동작을 한다. authorized_keys·yes는 사전 백업을 검증하고 복원한다. 로그 훼손은 book09 전용 모의 이력과 btmp 복사본만 사용하며 원본 로그는 보존한다. 실제 비밀 키·Wazuh 등록 키는 예제에 포함하지 않는다.

실행 증거와 DQL 결과는 editorial/evidence/chapter09/2026-11-03, 범위·차이는 editorial/chapter09-review.md에 기록했다. 이 초안은 REV01 검수본이 아니다.
