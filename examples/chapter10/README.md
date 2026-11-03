# 10장 복사용 예제

C10은 호스트·공격자·컨테이너 명령, Q10은 Discover DQL, S10은 osqueryi 입력이다. commands.txt는 전체 자동 실행 스크립트가 아니다. 각 블록의 사전 확인·위치·결과·원상복구를 읽고 한 번씩 입력한다.

collector-fragment.xml은 기존 ossec_config 내부의 수집 항목 조각이며 전체 설정을 대체하지 않는다. scheduled-listening-ports.sql은 예약 조회의 범위 설명용이다.

Q10-05만 wazuh-archives-*를 사용한다. 나머지는 wazuh-alerts-*이다. SQL은 osquery>에서 실행한다. IP·기간·에이전트·PID는 자신의 값으로 바꾼다. 스캔 대상은 허가된 kt66 VM 한 대이다. 기존 키·설정·방화벽을 먼저 기록하고 조건부 준비와 원상복구를 구분한다.

실제 개인 키는 제공하지 않는다. 실행·조회 증거와 검증하지 않은 조건은 editorial/chapter10-review.md에 기록한다. 초안은 REV01에 저장하지 않는다.
