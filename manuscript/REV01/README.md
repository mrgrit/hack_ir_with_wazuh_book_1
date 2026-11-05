# REV01 — 재작성본 (1~4장·부록 A)

기존 `manuscript/volume01-chapter0N.*`은 그대로 두고, 재작성본을 이 디렉터리에 둔다. 검토 후 채택하면 기존 파일을 교체한다.

## 파일

| 파일 | 내용 |
|---|---|
| `volume01-chapter01.json` / `.docx` | 표지·머리말·일러두기·목차 + 1장 (렌더 41쪽) |
| `volume01-appendix-a.json` / `.docx` | 부록 A 설치 상세와 문제 해결 (렌더 8쪽) |
| `volume01-chapter02.json` / `.docx` | 2장 공격과 보안관제의 기초 (렌더 23쪽) |
| `volume01-chapter03.json` / `.docx` | 3장 Wazuh 기본 운용 (렌더 20쪽) |
| `volume01-chapter04.json` / `.docx` | 4장 로그 수집과 탐지 규칙 (렌더 31쪽) |
| `../../examples/rev01/chapter01/` | C01-01~26 복사용 명령, `manifest.json`, `casebook.txt`(사건 노트 양식) |
| `../../examples/rev01/appendix-a/` | CA-01~08 복사용 명령, `manifest.json` |
| `../../examples/rev01/chapter02/` | C02-01~09 복사용 명령, `manifest.json`, 사례(`case-ssh.json`·`.log`), `investigation.txt` |
| `../../assets/figures/chapter01/rev01-*.png` | 1장 로드맵(도식 1-1), 사건 노트 흐름(도식 1-8) |
| `../../assets/figures/chapter02/rev01-*.png` | 2장 로드맵(2-1), SSH 출발지 경로(2-2), 원문→필드(2-4) |
| `../../examples/rev01/chapter03/` | Q03-01~06 검색식, `queries.json`, `investigation.txt` |
| `../../assets/figures/chapter03/rev01-*.png` | 3장 로드맵(3-1), 조건을 하나씩 더하는 검색(3-3) |
| `../../examples/rev01/chapter04/` | C04-01~26 명령, Q04-01~02 검색식, Ruleset Test 입력 로그 3개, `book04_rules.xml`, `investigation.txt` |
| `../../assets/figures/chapter04/rev01-*.png` | 4장 로드맵(4-1), 문장에 따른 하위 디코더·필드·규칙 차이(4-4) |

## 기존 1장 대비 변경

1. **구성** — 12절을 9절로 줄였다. 1.1~1.2 이해 → 1.3~1.5 설치 → 1.6~1.7 확인 → 1.8 기준점 → 1.9 공격자 VM(선택).
2. **설치 상세 분리** — VMware·Ubuntu 클릭 절차, 설치 실패 대응, 화면·수집기 문제 해결을 부록 A로 옮겼다. 본문은 "무엇을 왜 하는가"와 확인 기준만 남긴다.
3. **장 도입부** — 시나리오, 학습 목표, 가로형 로드맵, 준비와 완료 기준 표를 첫 펼침면에 둔다.
4. **장 마무리** — 핵심 정리, 확인 문제 5개와 해설, 더 읽을거리(전체 URL)를 둔다.
5. **사건 노트** — 1.8에서 "공격 일지"와 "조사 기록" 두 칸을 만든다. 11장에서 두 기록을 대조해 탐지 공백을 찾는 흐름의 시작점이다.
6. **목차** — 장마다 "조사 질문" 열을 둔다.
7. **일러두기** — 표기 원칙 표와 예시값(IP·계정·경로) 표를 모았다.

## 기존 2장 대비 변경

1. **장 도입·정리** — 1장과 같은 형식(시나리오, 학습 목표, 로드맵, 준비와 완료 기준 / 핵심 정리, 확인 문제, 더 읽을거리).
2. **2.2 직접 남기기 (신규)** — kt66 VM에서 `ssh book02_probe@10.20.30.201`로 실패 기록을 남기고 `kt66-bastion`의 auth.log에서 찾는다. 출발지가 VM의 ext망 주소 10.20.30.254로 기록되는 이유로 "출발지 IP = 경로의 단서"를 설명한다. 2.1 사례의 출발지도 같은 주소라는 점을 조사 기록에 반영했다.
3. **2.3 디코더·규칙 원문** — Wazuh v4.10.0의 `ssh-invfailed` 디코더와 규칙 5700/5710 정의를 보여 주고 prematch·regex·order·if_sid·match를 설명한다. 경보 필드를 출처(원문/수집기/규칙)로 나눈 표, rule.mitre는 판단이 아니라 규칙의 분류라는 점, 5712(반복) 규칙을 추가했다.
4. **보이지 않는 것** — sshd는 암호를 기록하지 않음, 수준 3 미만·규칙 없는 기록은 wazuh-alerts-*에 없음(kt66은 wazuh-archives-* 활성), 5710만 검색하면 5760·5715가 빠짐.
5. **2.4 시각** — syslog 원문에 연도·시간대가 없다는 점, kt66 컨테이너는 VM 시간대와 무관하게 Asia/Seoul이라는 점(compose 소스), `timedatectl` 추가.
6. **2.5 웹 응답** — 302(이동 주소 확인) 추가, 없는 경로 요청(C02-09)을 "먼저 예측"으로 실행.
7. **2.7 조사 기록** — 사실/판단 구분 표, 사건 노트 조사 기록 한 줄 예시, `_index`·`_id` 기록.

## 기존 3장 대비 변경

1. **장 도입·정리** — 1·2장과 같은 형식. 조사 질문 "원하는 기록을 어떻게 찾는가"를 검색 대상·시간 범위·검색 조건 세 가지와 0건의 의미로 풀었다.
2. **3.2 인덱스 패턴 표** — wazuh-alerts-*(경보, 수준 3 이상)와 wazuh-archives-*(전체 기록, kt66이 활성화)를 구분한다.
3. **3.4 DQL 연산자 표** — AND·OR·NOT·괄호·`필드: *`·범위, 계산 순서(NOT→AND→OR). OpenSearch Dashboards 2.16 문서와 대조했다.
4. **보이지 않는 것** — 필드 조건은 그 필드가 없는 기록(예: message repeated 요약 줄)을 뺀다.
5. **3.6 경보 건수 ≠ 시도 횟수** — 한 접속의 Invalid user·Failed password·연결 종료 줄이 각각 5710이 된다. 2026-11-02 실제 kt66 경보(8장 증거 `editorial/evidence/chapter08/2026-11-02/authentication-alerts.json`)로 확인한 동작이다.
6. **3.7 직접 남긴 기록 찾기 (신규)** — 2.2의 book02_probe를 data.srcuser, full_log, 같은 출발지의 실패·성공(5710·5760·5715) 순으로 찾는다. 결과가 없을 때 아카이브로 넘어가는 판단을 현장 노트로 넣었다.
7. **3.8** — 아카이브 확인 단계를 추가하고 "검색 상태 원상복구"로 이름을 맞췄다. 절 번호 3.8·3.9는 기존과 같다.

## 기존 4장 대비 변경

1. **장 도입·정리** — 조사 질문 "기록은 어떻게 경보가 되는가". 3.7·3.8의 "아카이브 → 수집 단계" 확인을 이어받는다. 4.12의 완료 근거 표는 장 정리의 완료 점검표로 옮겼다.
2. **4.1 단계별 확인 위치 표** — 원본 → 수집 설정 → 전달 → 분석 → 경보를 확인 위치·절과 연결하고, 4.11의 문제 해결 순서와 같게 맞췄다.
3. **명령 정리** — 기존 C04-01~47을 같은 목적끼리 묶어 C04-01~26으로 줄였다(hostname+grep, chown+chmod 전후 ls, 검사+종료 상태, restart+status 등). 2.3에서 설명한 정규표현식·5700/5710 문법은 반복하지 않고 설치 파일 대조 한 블록(C04-08)만 남겼다. 같은 kt66-siem 셸을 4.5~4.9에서 이어 쓴다.
4. **4.4 경보 0건을 실습 결과로** — 같은 검색식을 wazuh-alerts-*로 바꾸면 0건인 것을 3.8의 "아카이브에는 있고 경보에는 없는" 경우로 연결했다.
5. **4.6 보이지 않는 것** — 문장에 따라 계정이 srcuser(5710) 또는 dstuser(5760)로 추출되어 data.srcuser 검색이 5760·5715를 놓친다. 도식 4-4 추가.
6. **먼저 예측 3곳** — 문구가 아카이브·경보에 있을지, 바꾼 문장의 필드·규칙, 적용 전 문구가 경보가 될지.
7. **4.10 원상복구 확인** — 규칙 삭제 후 문구를 다시 남겨 아카이브에만 있고 100410 경보가 없음을 확인하는 단계를 넣었다(기존 실측 `editorial/evidence/chapter04/collection-restored.json`).

## 새 조판 규칙 (`tools/build_chapter01.py` 확장, 기존 장과 호환)

| 규칙 | JSON | 비고 |
|---|---|---|
| 흐름 조판 | page에 `"break": false`, `"level": "section"` | 절마다 새 쪽을 쓰지 않는다. 절 제목 13.5pt |
| 명령 블록 | command에 `purpose`, `syntax`, `result` | 목적 → 입력 → 구문 → 확인 순서로 출력 |
| 상자 4종 | `{"type":"box","kind":...}` | predict 먼저 예측 / caution 주의 / blind 보이지 않는 것 / field 현장 노트 (+ answer 해설) |
| UI 라벨 | 본문 안 `**텍스트**` | 고딕으로 출력. 명령·코드 안에서는 적용하지 않는다 |
| 목록 | `{"type":"list","ordered":bool,"items":[...]}` | 4항목 이하 목록만 한 쪽에 묶는다 |
| 표 묶기 | table에 `"keep": true` | 표가 쪽 사이에서 나뉘지 않게 한다 |

`break`, `level`, `purpose`가 없는 기존 JSON은 이전과 같은 결과가 나온다(2·5·7장 `document.xml` 동일 확인).

## 빌드

```bash
python3 tools/diagrams_chapter01_rev01.py
python3 tools/write_chapter01_rev01.py
python3 tools/write_appendix_a_rev01.py
python3 tools/build_chapter01.py --source manuscript/REV01/volume01-chapter01.json --output manuscript/REV01/volume01-chapter01.docx
python3 tools/build_chapter01.py --source manuscript/REV01/volume01-appendix-a.json --output manuscript/REV01/volume01-appendix-a.docx
python3 tools/diagrams_chapter02_rev01.py
python3 tools/write_chapter02_rev01.py
python3 tools/build_chapter01.py --source manuscript/REV01/volume01-chapter02.json --output manuscript/REV01/volume01-chapter02.docx
python3 tools/diagrams_chapter03_rev01.py
python3 tools/write_chapter03_rev01.py
python3 tools/build_chapter01.py --source manuscript/REV01/volume01-chapter03.json --output manuscript/REV01/volume01-chapter03.docx
python3 tools/diagrams_chapter04_rev01.py
python3 tools/write_chapter04_rev01.py
python3 tools/build_chapter01.py --source manuscript/REV01/volume01-chapter04.json --output manuscript/REV01/volume01-chapter04.docx
```

`tools/check_chapter01.py`는 "JSON 1쪽 = 렌더 1쪽"을 검사하므로 흐름 조판인 REV01에는 맞지 않는다. REV01은 명령↔예제 파일 일치, `bash -n`, 줄 길이 60자 이하, 판형·글꼴·색을 따로 확인했다.

## 채택 시 다른 장에서 고칠 참조

| 장 | 현재 문구 | 고칠 곳 |
|---|---|---|
| 3장 | "1.9의 서비스·센서 상태", "1.9에서 에이전트 연결" | 1.7 (수집기 문제는 부록 A.6) |
| 4장 | "1.11의 서비스 점검" | 부록 A.5·A.6 |
| 4장 | "1.12의 공격자 VM" | 1.9 |
| 5장 | "1.12의 일괄 설치", "1.12의 Ubuntu" | 1.9 (VM 생성은 부록 A.3) |
| 6장 | "1.12" 4곳 (도구 준비·공격자 VM hosts) | 1.9 |
| 7장 | "1.12" 2곳 (도구 설치) | 1.9 |
| 3장 | `examples/chapter02/case-ssh.json`, "2장에서 제공한 SSH 실패 기록" | REV01 3장에서 반영함 |
| 4장 | `examples/chapter02/case-ssh.json` | `examples/rev01/chapter02/case-ssh.json` |

## 미검증·작가 작업

- 새 VM에서 처음부터 설치하는 절차는 실행 검증하지 않았다(기존 kt66 화면과 명령 문법만 확인).
- 부록 A의 캡처 자리 2곳(VMware 설정 요약, Ubuntu 설치 첫 화면)은 저자가 직접 촬영해 넣는다.
- 2장 2.2(C02-01~05)는 새 VM에서 실행 검증하지 않았다. 출발지 10.20.30.254는 기존 kt66 기록(book03_probe)과 kt66 소스(ext망 게이트웨이 .254, bastion 10.20.30.201)로 대조한 예상 결과이다. 실행 후 화면을 촬영해 넣는다.
- 2장 C02-09(없는 경로)의 응답 코드는 확인하지 않았다. 본문은 "먼저 예측" 후 표에서 읽도록 썼다.
- 3장 3.7(Q03-04~06)은 2.2를 실행한 VM에서 검색 검증하지 않았다. 결과 설명은 5710 동작(8장 증거)과 2.2의 예상 출발지에 근거한다. Connection closed by invalid user 줄의 필드 추출 여부는 확인하지 않아 "일 수 있다"로 썼다. 실행 후 화면을 촬영해 넣는다.
- 4장의 명령·화면·결과는 2026-11-01 기존 kt66 실측(`editorial/chapter04-review.json`)을 따른다. 묶은 명령 블록(C04-02, 09, 12, 13, 14, 17, 21, 22, 25)은 같은 명령을 한 블록에 모은 것이며 블록 단위로 다시 실행하지 않았다.
- 3장 화면 3-1~3-8은 기존 kt66(에이전트 ID 010 시기)의 화면이다. 현재 환경의 bastion 에이전트 ID는 001이다.
- 렌더 쪽수는 LibreOffice 대체 글꼴 기준이다. 부크크 글꼴이 있는 Word에서 쪽 나눔을 다시 확인한다.
