# 9장 초안 — 저자용 집필·검증 기록

검토일: 2026-11-03 (Asia/Seoul). 대상: `manuscript/volume01-chapter09.docx`와 JSON 원고. 사용자의 “9장 가자” 요청에 따라 8장 이후 집필을 진행했다. 이 기록은 초안의 검증 범위이며 REV01의 별도 검수를 대신하지 않는다.

## 범위와 형식

Module 01 실습 22~28을 준비·입력·응답·Wazuh 수집/검색·조사/대응·원상복구 순서로 집필했다. 47개의 JSON 편집 단위가 최종 Word 렌더에서 67쪽이 된다. 명령 69개, DQL 12개, 실제 UI 영역 8개, 관계 도식 8개, 기존 인물 삽화 2개이다. 참고자료는 전체 URL을 인쇄했다. 복사용 예제는 개별 C09/Q09 파일과 모음, x.sh·a.sh, 조사 양식으로 제공한다.

6장까지의 문체·명령 위치·캡션·B5 조판과 7·8장의 초안/저자 기록 분리를 따랐다. `tools/assets/bookk-B5.docx`를 base로 열어 판형·여백·제본 여백·테마를 상속했다. 본문 부크크 명조 Light 10.5pt, 제목 부크크 고딕 Light, 코드 Consolas 10pt, 검정 문자와 표 테두리를 사용한다. DOCX만 배포하며 PDF/PNG 렌더는 build의 임시 검사용이다.

7장에 한정된 공격 실행·신규 UI 촬영 금지는 유지했다. 이번 실제 시험은 9장의 일곱 사례뿐이다. REV01·강의 저장소·다른 장 원고는 수정하지 않았다. 기존 미추적 `editorial/evidence/chapter07/2026-11-02/`는 커밋에서 제외한다.

## 원자료와 버전

- Module 01: https://docs.google.com/presentation/d/1o0H_2DDHBp8p2HvlSnEPbx6-jdURYzew/edit
- 받은 PPTX SHA-256: `b3550f87c2342a43e72ee5ac74c9a884de6aff38631b8c77a2364d0cf5d47099`. 연결 Drive 메타데이터의 변경 상태를 확인하고 기존 동일 PPTX를 사용했다.
- 실제 발표 순서 258~321쪽을 대조했다. 내부 slide XML 번호와 발표 순서는 다르다. 대응표는 `chapter09-source-coverage.json`이다.
- kt66 기준 커밋: `63d4180b1d6866de986ef263a3bd831d6082b5d5`. https://github.com/mrgrit/kt66
- Ubuntu 22.04, Wazuh Manager 4.10.0·에이전트 4.10.1. 설치된 규칙·디코더·audit-keys와 FIM/audit 설정을 읽고 실제 이벤트를 대조했다.
- 공식 Wazuh FIM/audit 문서, OpenSSH, Ubuntu crontab/auditctl/ausearch, curl, Python HTTP 서버, Debian dpkg 설명서를 참고했다. Ubuntu nc 도움말(OpenBSD netcat 1.218-4ubuntu1)과 dpkg 1.21.1을 현장에서 확인했다. GNU Bash 웹 문서 조회는 시간 초과했으며 PIPESTATUS 동작은 실제 두 종료 상태와 셸 구문으로 확인했다.

## 실제 실행과 경보

시각은 한국 시간 2026-11-03 07:49~07:54, 증거 JSON의 timestamp는 UTC인 전날 22시대이다. Discover는 07:45~08:05를 고정해 조회했다. `evidence/chapter09/2026-11-03/selected-alerts.json`에는 해당 경로·명령·인증에 한정한 28개 경보가 있다. 전체 호스트 감사 기록이나 인증 비밀은 게시하지 않는다.

| 실습 | 실제 확인 | 원상복구 |
|---|---|---|
| 22 | ccc SSH에서 sudoers 전용 파일 추가, 주석 추가, visudo 검사. 554·550·553. 27→44바이트와 diff | 전용 파일 제거, 전체 정책 parsed OK |
| 23 | 임시 Ed25519 공개 키 추가, 공개 키 전용 SSH로 bastion·uid 1000 응답, 5715 원문의 키 지문 대조 | 기존 authorized_keys를 cp -p·cmp·해시로 복원, 새 키 접속 255 거부, 임시 키와 백업 제거 |
| 24 | cron 설치·시작, 전용 cron 파일, x.sh 제공. 07:52:01 GET 200와 결과 `book09-cron user=root host=bastion` | cron 파일·결과 제거, cron 중지 |
| 25 | 별도 attacker의 제한 시간 nc 대기, 호스트 ccc의 FIFO/nc. hostname·id·exit만 송수신, audit 6630와 Sysmon EventID 1 확인 | 연결 종료, FIFO 제거, 4444 연결/대기 없음 |
| 26 | a.sh 사전 조회와 curl→sh 실행. HTTP 200, 사용자·호스트 출력, PIPESTATUS `0 0`. audit 부모·자식 대조 | HTTP 서버 종료, 제공 파일·작업 디렉터리 제거 |
| 27 | web의 yes 백업 뒤 NUL+BOOK09 7바이트 추가. 31,112→31,119, FIM 550·dpkg yes 불일치 | cp -p·cmp=0·초기 해시·크기·권한 일치, yes 불일치 제거, 백업 제거 |
| 28 | 모의 .bash_history 20→0 및 btmp 복사본 제거. 550과 553 구분 | 원본 btmp 해시 불변, 원래 없던 실제 .bash_history도 생성하지 않음. 실습 경로 제거 |

실행 기록은 `execution-records.json`에 보존한다. GUI 검색은 `query-proof.json`과 12개 원본 PNG로 보존한다. 순서대로 3, 1, 2, 1, 2, 1, 7, 2, 3, 2, 1, 1건이다. Q09-07의 7건은 같은 PID의 exec 기록을 포함하므로 프로세스 7개로 해석하지 않았다.

## 수행 방식과 미검증 경로

저자는 Paramiko·OpenSSH를 통해 제한된 명령을 보냈고 컨테이너 관리에는 저자용 일회성 docker exec도 사용했다. 본문은 독자가 대화형 docker exec -it 셸에 들어가 한 명령씩 실행하고 exit로 나오는 흐름이다. 공개 키 붙여 넣기/Ctrl+D, 개별 창 입력, 처음 접속 지문 승인까지 사람이 본문 전체를 그대로 재현했다고 주장하지 않는다. 본문의 키 추가와 같은 파일 변경·키 인증·복원 결과를 대조했다.

저자 리버스 셸은 대기 45초·대상 35초 timeout과 FIFO 정리 trap을 추가했다. 본문은 준비 시간을 위해 대기 90초를 사용하고 대상 창의 Ctrl+C·FIFO 제거를 명시한다. 핵심 FIFO/nc 명령은 같다. HTTP 서버도 저자는 600초 상한을 두었고 실제 중지·포트 해제를 확인했다. 본문은 전경 서버/Ctrl+C 흐름이다.

authorized_keys가 처음부터 없을 때의 install 준비·제거 분기는 실행하지 않았다. 기존 키 파일 경로를 시험했다. 새 VM 설치, 모든 도구 재설치, 다른 운영 체제·다른 Wazuh 버전, 실제 로그 훼손, 운영 사건의 차단 정책·서비스 복구는 검증 범위 밖이다. /dev/tcp와 nc -e는 구현 차이 설명만 하고 추가 공격으로 실행하지 않았다. 본문 명령 69개는 Bash 구문 검사이며 전체를 일괄 실행하지 않는다. 규칙 조회 sed 세 가지와 ausearch -if는 최종 본문 구문으로 별도 읽기 검증했다.

## 준비 단계에서 남긴 정상 상태

호스트 에이전트는 설치되었으나 inactive였고 client.keys가 비어 있었다. 기존 Manager 주소 10.20.32.100과 등록 정책을 확인한 뒤 kt66-host로 등록·시작했다. ID 006, Active를 확인했다. 서비스는 현재 active이며 systemd enable 설정은 원래의 disabled를 유지했다. 등록 키는 게시하지 않는다. 기존 auditd·Sysmon·감사 규칙은 유지했으며 최종 audit lost=0이다.

bastion의 기존 `/etc/sudoers.d/ccc` 권한 0644 오류를 0440으로 수정해 정상화했다. 파일 내용은 변경하지 않았다. cron은 설치되어 있지 않아 공식 Ubuntu 패키지로 준비했고 패키지는 유지하되 서비스는 원래 중지 상태로 돌렸다. 이 준비 변경을 “시스템 전체가 처음과 완전히 동일”하다고 표현하지 않는다.

기존 authorized_keys SHA-256 `bd0120b8a37a90bf87b05c2a7856bd3c76e50050799739c4a94a7cfc8b6421d1`, 디렉터리 0755·파일 0600·ccc 소유를 보존했다. btmp 원본 SHA-256 `450b1eb3c0f14a0ee6be04e0ef164507633f605e70eaa456d24bcc34f18fa860`을 보존했다. yes는 초기 SHA-256 `a63b5b6bd13460b0914b8bb4f4b08a3f2587f4cbcf630d771e364344b06a40b8`, 31,112바이트·0755·root로 돌아왔다. 공격자 `/home/att/book09` 안의 이번 파일만 명시적으로 삭제하고 빈 디렉터리를 rmdir로 제거했다.

## 원자료에서 바로잡은 해석

- FIM은 감시·기준 상태·제외·권한·수집 상태의 영향을 받는다. 모든 변경을 무조건 즉시 잡는다고 쓰지 않았다. metadata만 바뀌어도 modified일 수 있다.
- uid_after/uname_after는 파일 소유자이다. 실제 사건 mode는 realtime이며 행위자를 표시한 who-data 사건이라고 설명하지 않았다. diff는 선택적 텍스트 기능이며 민감 정보 정책과 구분했다.
- useradd와 시간 근접만으로 정상 변경, 그 부재로 수동 변조를 확정하지 않았다.
- 키 등록·공개 키 인증·기존 세션 종료, cron 등록·서비스 실행·이미 실행된 프로세스 종료를 분리했다. 공개 키 주석을 신원으로 쓰지 않았다.
- auid와 현재 uid/euid를 구분했다. 일반 로그인 ID에서 시작한 컨테이너 명령도 host audit에 관찰되므로 컨테이너 잡음을 전부 제외한다고 설명하지 않았다.
- audit success/exit는 execve 호출의 결과이며 프로그램 최종 종료·접속 성공이 아니다. SYSCALL a0와 EXECVE a0도 구분했다.
- 실제 nc SYSCALL exe는 `/usr/bin/nc.openbsd`, 추출 필드는 `/usr/bin/nc`이다. 차이는 실증했으나 단일 정규표현식만으로 원인을 확정하지 않았다. 실제 추출 인자와 원문을 함께 검색한다.
- URL은 추가 옵션 때문에 curl의 a4에 있다. a1/a2만 검색하는 누락을 피했다. 가까운 curl/sh 시간만으로 파이프를 확정하지 않고 부모·세션·원문·HTTP·출력을 대조했다.
- yes 백업을 변조 전에 만든다. dpkg -V는 로컬 MD5 검사이며 기존 doc/man missing과 이번 yes 불일치를 구분했다.
- 28의 원본 로그 삭제 대신 전용 복사본을 사용했다. 591과 553은 정상/악성을 완전히 분류하는 짝이 아니다.

## 조판·검사

번들 render_docx.py를 시도했으나 Windows PATH에 soffice.exe가 없어 실패했다. 설치된 Microsoft Word COM으로 비공개 PDF를 생성하고 pypdfium2로 모든 페이지를 렌더했다. 첫 65쪽에서 화면 툴팁 가림을 발견해 실제 UI를 다시 촬영했고, 짧은 표가 페이지에 걸치지 않도록 묶었다. 조건부 키 준비와 실패 시 연결 정리를 보완한 최종본은 67쪽이다.

최종 전체 지면을 육안 점검했다. DOCX 그림 18개 삽입, 템플릿 테마·판형 상속, 69개 복사용 명령·12개 DQL 일치, Bash 구문, 화면 원본 SHA-256·crop 픽셀 일치, PDF의 모든 참고 URL·세 글꼴을 검사했다. 자세한 수치는 `chapter09-validation.json`에 남긴다. 실제 화면을 그림 코드로 재현하지 않았다. UI 원본과 잘라낸 영역은 provenance로 연결했다.
