# 10장 초안 — 집필·검증 기록

검토일: 2026-11-03 (Asia/Seoul). 사용자의 “10장 가자” 요청에 따라 Module 01 실습 29·30·62를 집필했다. 이 기록은 초안의 검증 범위이며 REV01의 별도 검수를 대신하지 않는다.

## 산출물과 원자료

제목은 **네트워크 흔적과 현재 상태 조사**이다. 43개 JSON 편집 단위가 Word에서 55쪽으로 조판된다. 명령 44개, Discover DQL 10개, osqueryi 입력 4개, 실제 UI 영역 6개, 관계 도식 5개, 기존 인물 삽화 2개를 넣었다. XML 수집 설정 조각·예약 SQL·조사 양식도 복사용 파일로 제공한다. C10 모음은 일괄 실행 스크립트가 아니다.

Module 01 발표 순서 322~339와 627~635쪽의 개념·공격 입력·결과 해석을 대조했다. 627~628의 Windows 예제는 운영체제 비교 개념이며 Linux 실습 명령으로 복제하지 않았다. 공격 화면 이미지 323·333·629쪽도 직접 확인했다. 대응표는 `chapter10-source-coverage.json`, 발췌 기록과 원본 이미지 영역은 `evidence/chapter10/2026-11-03/`에 있다. 본문 UI는 이 슬라이드 화면을 재활용하지 않고 실제 이번 kt66에서 촬영했다.

- 원자료: https://docs.google.com/presentation/d/1o0H_2DDHBp8p2HvlSnEPbx6-jdURYzew/edit
- PPTX SHA-256: `b3550f87c2342a43e72ee5ac74c9a884de6aff38631b8c77a2364d0cf5d47099`.
- 연결 Google Drive 메타데이터: Module01_Wazuh_위협탐지_DQL.pptx, 17,276,372바이트, 수정 2026-10-31T13:56:32.317Z. 동일 자료의 기존 다운로드를 사용했다.
- kt66 기준 커밋: `63d4180b1d6866de986ef263a3bd831d6082b5d5`.
- 환경: Ubuntu 22.04, Wazuh Manager 4.10.0·에이전트 4.10.1, osquery 5.24.0, Nmap 7.80.

6장까지의 문체·명령 실행 위치·확인 기준·캡션과 7~9장의 초안/검토 기록 분리를 따랐다. `tools/assets/bookk-B5.docx`를 base로 열어 판형·여백·제본 여백·테마를 상속했다. 본문 부크크 명조 Light 10.5pt, 제목 부크크 고딕 Light, 명령 Consolas 10pt, 검정 글자와 단순 표를 유지했다. DOCX만 배포한다. REV01·다른 장 원고·강의 저장소는 수정하지 않았다. 기존 미추적 chapter07 증거 디렉터리는 커밋에서 제외했다.

## 실제 확인 결과

실습 시각은 한국 시간 08:35~08:53이며, 증거 JSON은 주로 전날 23시대 UTC이다. Discover 조회 기간은 2026-11-03 08:35~09:30 KST로 고정했다. 대상은 kt66 호스트 .107과 별도 공격자 VM .108이다. kt66 내부 attacker 컨테이너와 bastion 2204는 이번 대상이 아니다.

| 항목 | 실제 관찰 |
|---|---|
| 실습 29 | ccc의 nc 리스너 .107:31337, PID 181571. ss·ps·audit 실행 기록을 대조했다. |
| 실습 30 | .108에서 .107의 TCP 1~1000을 한 번 스캔했다. 4.91초, 7 open·993 filtered. kern.log와 08:37:47의 4151을 대조했다. |
| 개별 DROP | 준비된 archives 인덱스에서 대상·수집 경로·출발지 조건으로 592건을 조회했다. 이 숫자를 패킷 전체 수나 목적지 포트 종류 수로 해석하지 않았다. |
| 실습 62 포트 | .107:31338의 nc, PID 182078. 직접 SQL의 p.pid·p.path와 예약 결과를 대조했다. |
| 실습 62 키 | 임시 Ed25519 키를 ccc의 authorized_keys에 등록했다. restrict·from 옵션, 지문과 주석을 확인했다. 이 키로 SSH 인증을 시도하지 않았다. |
| osquery 차이 | 31337·31338·공개 키 added 각 1건, 제거 후 removed 각 1건. 원문 JSON과 Wazuh data.osquery 필드가 대응한다. |
| 533 | 08:42:21의 현재 출력에 두 포트, 08:48:21의 이전 출력에 두 포트가 남았다. 2건을 추가·원상복구 시각과 대조했다. |

`selected-alerts.json`은 9개 핵심 경보이며 `nc-execution-alerts.json`에는 audit 2건을 별도로 보관했다. `osquery-results.jsonl`은 원문 차이 기록 6행이다. `archive-drop-sample.jsonl`은 회전한 아카이브의 개별 DROP 4행이다. 09:00 KST는 Manager의 UTC 날짜 경계여서 현재 archives.json을 읽은 첫 조회가 빈 결과였고, `2026/Nov/ossec-archive-02.json.gz`에서 원문을 확인했다.

DQL Q10-01~10의 최종 건수는 순서대로 **2, 2, 2, 1, 592, 3, 1, 1, 2, 1**이다. Q10-05만 archives이며 나머지는 alerts이다. 입력 직후 UI에 잠깐 남는 이전 건수를 최종 증거로 사용하지 않고 검색 응답이 갱신된 상태를 다시 저장했다. AX 기록과 원본 PNG, 정확한 검색식은 `query-proof.json` 및 `ui/`에 있다.

## 원자료 해석 보정

- 새 포트가 있는 서버는 kt66 호스트이다. 슬라이드 공격 화면의 일괄 문구 “공격자 VM”과 피해 서버 명령을 구분했다. nc의 연결 대기는 백도어 인증·셸 실행·외부 연결 성공의 증거가 아니다.
- 533은 `netstat listening ports` 별칭에 해당하는 출력의 차이를 검사한다. full_log와 previous_output을 대조했고 data.extra_data가 항상 있다는 전제를 제거했다. previous_log도 실제 JSON에 있으나 본문은 검색·대조에 사용한 previous_output으로 통일했다. PID 등의 출력 변화도 경보를 만들 수 있다.
- 4101은 firewall 범주의 DROP이며 no_log가 있다. 4151은 같은 출발지의 4101을 frequency 18, timeframe 45, ignore 240으로 상관 분석한다. 별도의 wazuh-logtest 세션에 동일 원문 25행을 넣었을 때 18번째가 4151이었다. 이 시험은 실제 스캔이나 경보 저장을 추가하지 않는다.
- 4151의 실제 그룹은 firewall·multiple_drops이다. 현재 data.dstport 한 값과 previous_output 일부만으로 스캔 전체 범위를 집계하지 않는다. 아카이브 저장 여부를 alerts 저장 여부와 구분한다.
- perimeter.sh의 예외는 적용 당시 리스닝 포트에서 만든다. RETURN은 최종 ACCEPT와 다르고, LOG는 DROP과 별개이다. INPUT과 Docker DNAT 이후 FORWARD 경로를 구분했다. LOG 제한이 있으므로 로그 수와 패킷 수가 다를 수 있지만 이번 592건의 차이를 특정 원인 하나로 확정하지 않았다.
- filtered의 원인을 반드시 DROP 하나로 단정하지 않는다. Nmap SERVICE 열은 기본 이름이며 서비스 버전 검증 결과가 아니다. -Pn의 Host is up도 별도 생존 확인의 성공 증거가 아니다.
- osqueryi 직접 조회, osqueryd 예약 결과, Wazuh DQL을 분리했다. 예약 포트 SQL은 PID를 선택하지 않으므로 직접 SQL에서 보충한다. authorized_keys 예약 SQL은 key·options를 선택하지 않으므로 그 열만 달라지면 변화가 보이지 않을 수 있다.
- 첫 added는 기존 상태일 수 있다. interval 60과 splay 10을 구분하고, removed만으로 파일 삭제를 단정하지 않는다. 24010은 정상 JSON 조회 결과 분류이며 악성 판정이 아니다. 530/533·24000/24010의 부모·하위 조건과 kernel/iptables의 이름 상속도 설명했다.

설치된 규칙·디코더와 기준 kt66 코드를 읽고 공식 Wazuh·osquery·Nmap·OpenSSH·iptables 문서를 대조했다. 관련 전체 URL은 본문에 인쇄했다. OpenBSD sshd 문서 첫 직접 조회는 시간 초과했고 검색 인덱스의 공식 문서와 다른 공식 OpenBSD 버전 문서로 restrict/from 정의를 확인했다.

## 준비 변경과 원상복구

시작 당시 호스트 에이전트는 active, osquery는 설치됐으나 inactive·disabled였다. /etc/osquery와 결과 로그 디렉터리는 비어 있었다. Wazuh osquery 모듈은 disabled=yes, kern.log localfile은 없었다. INPUT은 ACCEPT였고 KT66-PERIMETER는 없었다. ccc의 authorized_keys는 원래 존재한 0바이트 파일이었다.

ossec.conf를 백업한 뒤 기준 osquery-linux.conf를 설치하고 config_check를 수행했다. 기존 osquery 블록을 disabled=no·run_daemon=no로 바꾸고 kern.log 수집을 추가했다. Wazuh 두 검사 명령을 통과한 뒤 osqueryd 시작·에이전트 재시작을 수행했다. 최초 저자용 문자열 치환은 Python 구문 오류로 적용되지 않았으며 수정한 실행만 성공 기록으로 취급한다.

08:37에 perimeter를 적용하고 스캔한 뒤 08:42에 이번 INPUT 이동 규칙·전용 체인만 제거했다. 08:44에 소유자·PID·명령줄을 확인한 두 nc에 TERM을 보냈고 공개 키 파일을 백업으로 복원했다. removed 3건과 후속 533을 수집한 뒤 osqueryd를 중지하고 ossec.conf를 원본으로 복원했다. 두 검사 후 에이전트를 다시 시작했다.

- ossec.conf 최종 SHA-256: `1e0a7877f48dc736204f6fada543c89fed6b21903368ee8dd3466153ac4bc83d` — 초기와 일치.
- authorized_keys 최종 SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` — 초기와 일치, ccc 소유·0600 유지.
- 31337·31338 소켓 없음. INPUT ACCEPT이며 iptables-save와 nft의 filter 표에 KT66-PERIMETER 없음. 없는 체인을 직접 조회한 iptables-nft의 incompatible 메시지를 남은 체인의 증거로 해석하지 않았다.
- osqueryd inactive·disabled, wazuh-agent active·disabled로 초기 실행/자동 시작 상태 복원. 이번에 생성한 osquery.conf·빈 flags, 양쪽 임시 키·공개 키 복사본·리스너 출력 파일·저자 백업은 제거했다. 결과 로그와 osquery 상태 DB는 보존했다.
- 공격자 VM에는 Ubuntu 공식 패키지 Nmap과 의존 패키지를 설치해 유지했다. 설치 전 첫 nmap 호출은 command not found였으며 설치 후 한 번의 스캔만 성공했다.
- 기존 archives 데이터는 있었지만 Dashboard의 검색 패턴이 없었다. UI에서 `wazuh-archives-*`, 시간 필드 timestamp로 패턴을 생성해 유지했다. alerts 기본 패턴은 바꾸지 않았다. 생성 결과 캡처를 보관했다.
- kt66 저장소 HEAD는 기준 커밋이고 작업 트리는 깨끗했다.

## 검증하지 않은 경로

저자는 SSH/Paramiko로 제한된 명령을 실행했다. 컨테이너 정의 조회에는 저자용 일회성 docker exec를 사용했으나 본문은 docker exec -it로 들어가 직접 입력하고 exit로 나온다. nc는 저자 실행에서 nohup과 출력 파일을 사용하고 PID를 확인해 TERM으로 종료했다. 본문은 전경 터미널과 Ctrl+C를 기본으로 한다. 전경 셸 전체를 사람이 책 순서대로 재현했다고 주장하지 않는다.

공개 키는 저자 실행에서 SFTP로 전달했다. 본문의 scp 로그인·호스트 지문 승인 과정을 새로 재현하지 않았다. 추가 전 빈 파일을 사용했으므로 기존 마지막 행에 줄바꿈이 없는 분기는 실서버 시험하지 않았다. 본문 printf에는 첫 줄바꿈을 추가해 기존 마지막 키와 새 키가 합쳐지는 문제를 피했다. 이 변경과 처음에 .ssh/authorized_keys가 없는 조건부 준비·정리는 정적 검토 범위다. 기존 파일 복원 경로는 실제 cmp·해시로 검증했다.

새 VMware/Ubuntu 설치, osquery 재설치, apt-get update, 다른 버전·OS·방화벽 구성, 운영 사건의 차단 정책·복구, 추가한 키로의 SSH 인증 성공은 시험 범위 밖이다. 실제 침해를 판정하지 않았다. 명령 44개의 Bash 검사는 문법 검사이며 모든 블록의 일괄 실행 성공을 뜻하지 않는다.

## 조판과 QA

번들 render_docx.py는 Windows PATH에 soffice.exe가 없어 실패했다. 설치된 Microsoft Word의 비공개 PDF 출력과 pypdfium2로 전체 페이지를 렌더했다. 기존 임시 PDF 덮어쓰기에서 Word 오류가 한 번 발생해 새 임시 파일명으로 재출력했다. PDF는 배포하거나 Git에 넣지 않는다.

초기 53쪽을 모두 육안 검토한 뒤 전송 파일 사전 확인과 조건부 원상복구를 보완해 55쪽이 됐다. 최종 변경 페이지를 다시 확인했고 나머지 페이지는 이전 검토 이미지와 픽셀 동일성을 대조했다. 최종 55쪽의 화면 글자·명령 상자·표 경계·캡션·페이지 번호·전체 URL을 확인했다.

DOCX 그림 13개 실제 삽입, base 판형/테마 일치, 복사용 명령·DQL·osquery 입력 일치, Bash 구문, XML 조각 구조, UI 원본 SHA-256·crop 픽셀 일치, 인쇄된 전체 URL, 세 지정 글꼴을 검사했다. 최종 DOCX 해시와 결과는 `chapter10-validation.json`이다. UI는 코드로 모사하지 않았으며 임시 렌더는 build에만 남긴다.
