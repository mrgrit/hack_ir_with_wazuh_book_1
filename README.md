# 해킹·침해대응 실무 with Wazuh

1권 **시스템 침투와 SIEM 분석**의 집필 저장소입니다.

**머리말·미리 안내·1~11장과 부록의 초안**을 작성했습니다. 다음 교정은 챕터별 DOCX를 기준으로 진행합니다. 핵심 설명, 독자의 행동, 확인 기준을 제시하며 기존 1~3장 폐기 원고는 Git 이력에 보존합니다.

- **[머리말·1장 DOCX](manuscript/volume01-chapter01.docx)** — 부크크 B5, 편집·검토용
- **[2장 초안 DOCX](manuscript/volume01-chapter02.docx)** — 공격과 보안관제의 기초, 9쪽
- **[3장 초안 DOCX](manuscript/volume01-chapter03.docx)** — Wazuh 기본 운용, 12쪽
- **[4장 초안 DOCX](manuscript/volume01-chapter04.docx)** — 로그 수집과 탐지 규칙, 31쪽
- **[5장 초안 DOCX](manuscript/volume01-chapter05.docx)** — 웹 공격의 시작과 입력값 검증, 76쪽
- **[6장 초안 DOCX](manuscript/volume01-chapter06.docx)** — 웹 탐색과 인증 공격, 70쪽
- **[7장 초안 DOCX](manuscript/volume01-chapter07.docx)** — 웹 서버 침투와 실행 흔적, 58쪽
- **[8장 초안 DOCX](manuscript/volume01-chapter08.docx)** — SSH 인증 공격과 계정 권한 조사, 58쪽
- **[9장 초안 DOCX](manuscript/volume01-chapter09.docx)** — 지속성 확보와 시스템 변경 탐지, 67쪽
- **[10장 초안 DOCX](manuscript/volume01-chapter10.docx)** — 네트워크 흔적과 현재 상태 조사, 55쪽
- **[11장 초안 DOCX](manuscript/volume01-chapter11.docx)** — 사건 재구성과 대응 판단, 30쪽
- **[부록 초안 DOCX](manuscript/volume01-appendices.docx)** — 실습 점검과 조사 자료, 27쪽
- [11장 분석 예제·증거 발췌·조사 양식](examples/chapter11/)
- [전체 입력 451개 색인](examples/appendices/example-index.csv)
- [11장·부록 집필 및 검토 기록](editorial/chapter11-appendices-review.md)
- [10장 복사용 명령·DQL·SQL·수집 설정·조사 양식](examples/chapter10/)
- [9장 복사용 명령·검색식·스크립트·조사 양식](examples/chapter09/)
- [7장 복사용 입력·명령·검색식·조사 양식](examples/chapter07/)
- [6장 복사용 입력·명령·검색식·실제 로그](examples/chapter06/)
- [5장 복사용 명령·검색식·실제 로그](examples/chapter05/)
- [4장 명령·검색식·규칙 파일](examples/chapter04/)
- [3장 복사용 검색식·조사 양식](examples/chapter03/)
- [2장 사례·복사용 명령](examples/chapter02/)
- [복사용 명령](examples/chapter01/) — 본문의 C01 번호와 대응
- [집필 지침](AGENTS.md)
- [검토·검증 기록](editorial/chapter01-review.json)
- [캐릭터 삽화](assets/illustrations/chapter01/) · [생성 프롬프트·출처 기록](editorial/chapter01-illustrations.json)
- [2026-11-03 시리즈 삽화 전체 점검](editorial/illustration-audit.md) · [새 장면 자산](assets/illustrations/diversity/)

2026-11-03에는 1·2권의 기존 인물 삽화 23곳을 모두 확인하고 반복되는 15곳을 교체했다. 2권 2·3장의 신규 4곳을 포함해 27곳에 서로 다른 장면 27개를 사용한다. 인물·장소·행동·소품을 달리하고 기존 본문은 보존했다. 1권 5장의 삽화 단독 페이지를 관련 설명 뒤로 옮겨 현재 Word 렌더 76쪽으로 정리했다. 변경된 장의 현재 페이지 수·파일 해시·렌더 비교는 삽화 점검 기록에 있다.

1장은 VMware·Ubuntu 준비, kt66 설치·기동, 웹·Wazuh 접속, 센서 확인, 중지·복구를 다룹니다. kt66과 공격자 VM의 브리지 구성도와 선택적 공격자 VM 준비 절차도 포함합니다. 공격자 VM은 Ubuntu 22.04 Live Server를 사용하며 5장의 선택 curl 실습과 이후 터미널 실습에 필요합니다. 도구 일괄 설치 명령은 C01-52입니다. 머리말·1장은 35쪽이며 설명 도식 7개와 작은 캐릭터 삽화 3개를 수록합니다. 1장의 12개 절은 한 쪽의 학습 순서 도식으로 정리했습니다. 작은 삽화는 인물·장소·소품을 달리한 v2로 교체했습니다. 1권 전체 범위는 Module 01 실습 01~30 및 62, 11장과 부록입니다. 2장은 기존 kt66의 SSH 인증 실패 경보를 사례로 로그·탐지·판단·대응을 설명합니다. 새 공격을 실행하지 않고 기존 경보 조회와 시각·웹 응답 확인을 수행했습니다.

3장은 Discover에서 인덱스·기간·DQL을 지정하고 경보의 필드·원문을 읽는 실습입니다. 실제 UI 화면 8개, 개념 도식 2개, 작은 삽화 1개를 수록했습니다. 기존 SSH 사례를 검색한 두 조건은 각각 2건을 반환했습니다. 모든 장의 참고 자료에는 제목과 전체 URL을 함께 인쇄합니다.

4장은 bastion에 확인 문구를 기록하고 아카이브에서 찾은 뒤, 사용자 규칙 100410을 적용해 새 경보를 생성하는 실습입니다. 수집·규칙 시험·실제 경보 생성·규칙 제거와 재시작을 기존 kt66에서 검증했습니다. 실제 화면 7개, 도식 5개, 야외 통신함 점검 삽화 1개를 수록했습니다. SSH 원문과 추출 필드의 대응, 실제 디코더·규칙 파일의 위치와 조회 절차, logger·grep의 옵션과 정규표현식 해석을 보완했습니다.

6장은 Module 01 실습 04~06, 13~15를 다룹니다. 브라우저 경로 탐색, User-Agent 변경, 일반 로그인과 Brute Force 결과 비교, PROPFIND, 관리 경로, 긴 URL을 실제 kt66에서 확인했습니다. Gobuster는 공격자 VM에서 23행의 짧은 경로 목록으로 시험하며, curl 두 예제는 선택 실습입니다. **70쪽, 실제 화면 33개, 도식 6개, 새 삽화 2개**이며 복사용 명령 28개·DQL 13개·브라우저 입력 11개를 제공합니다.

6장의 DQL 13개를 실제 Discover에서 검증했고, 수집된 access 기록 63개를 Apache 원문과 대조했습니다. 일반 로그인은 성공·실패 모두 302, Brute Force는 모두 200이므로 이동 주소·본문과 함께 읽도록 설명했습니다. WAF 차단 근거, 로그·코드 위치, 명령 옵션·기호, 문제 해결과 원상복구 절차를 포함했습니다. 새 VM 설치와 패키지 재설치는 수행하지 않았습니다.

7장은 Module 01 실습 07~12를 바탕으로 2026-11-02에 다시 집필했습니다. 공격 준비와 입력, HTTP 응답, Wazuh 수집·검색, 조사·대응, 원상복구를 연결합니다. **58쪽, 슬라이드 화면 영역 19개, 도식 8개, 삽화 2개, 명령 30개, DQL 11개, 브라우저·hosts 입력 12개와 PHP 파일 예제 1개**를 제공합니다. 브라우저 입력을 먼저 설명하고 헤더·POST·반복문의 curl 예제는 7.9에 모았습니다.

7장의 결과 화면은 제공된 PPTX에 수록된 기존 기록입니다. 이번 집필에서는 **공격 실행·신규 UI 촬영·DQL 실서버 검증을 하지 않았습니다.** 원본 공격 입력의 변형과 응답을 빠짐없이 대조하고, 웹셸 파일 생성과 업로드, 탐지 규칙과 실제 실행 성공을 구분했습니다. 수정 구문은 정적으로 검사했으며 모든 지면·전체 참고 URL·화면 원본 픽셀·복사용 파일을 확인했습니다. 초안과 검토 기록은 일반 원고 경로에 저장했고 REV01은 수정하지 않았습니다.

## 확인한 범위

5장은 Module 01 실습 01~03의 SQL 인젝션·XSS·경로 조작을 **브라우저 중심**으로 진행합니다. Windows 웹 이름 등록 → DVWA 로그인 → 첫 DB 초기화 → Low 선택 → 실습 메뉴 → 입력·Submit → Network 응답 → Wazuh 기록 순서입니다. 브라우저와 Wazuh의 실제 화면 25개, 설명 도식 6개, 삽화 2개를 수록했습니다. 현재 Word 렌더는 76쪽이며 명령 37개, DQL 7개와 브라우저 복사용 입력 8개를 제공합니다.

기존 curl 명령은 **5.13 ‘다른 방법 · 같은 요청을 curl로 보내기’**로 옮겼습니다. --get·--data-urlencode·--data와 따옴표·변수·줄 연결을 실행 전에 설명합니다. 브라우저와 curl의 로그인 상태 차이도 구분했습니다.

실제 Chromium에서 DB 초기화·로그인·Low 설정·입력·클릭·로그아웃을 확인했습니다. 로그인한 정상 조회는 사용자 1의 이름과 200을 반환했고, SQL·XSS·두 가지 경로 요청은 모두 WAF 차단으로 403을 받았습니다. Wazuh 규칙과 네 요청의 감사 기록을 대조했고 검색식 7개도 실제 Discover에서 검증했습니다. Windows hosts 편집은 공식 문서와 대조했으며 Windows에서 직접 실행한 것으로 주장하지 않습니다.

kt66 커밋 `63d4180b1d6866de986ef263a3bd831d6082b5d5`의 코드·설정과 공식 문서를 대조했습니다. 기존 가동 환경에서 웹 응답, 데모 계정 Wazuh 로그인, kt66-host 연결 상태를 확인하고 실제 화면을 촬영했습니다.

**새 VMware VM에 대한 설치·중지·스냅샷 복원은 실행 검증 전입니다.** VMware·Ubuntu 설치 화면 두 곳은 저자 촬영 지시를 두었습니다. 나머지 그림은 실제 삽입했습니다. 강의·kt66 저장소는 수정하지 않았습니다.

## 편집과 재생성

DOCX를 직접 편집할 수 있습니다. 조판기는 기본적으로 `build/`에 출력하므로 검토 중인 원고를 덮어쓰지 않습니다. DOCX에서 고친 내용이 Python·JSON 원본에 자동 반영되지는 않습니다.

```bash
.venv/bin/python tools/write_chapter01.py
.venv/bin/python tools/diagram_chapter01.py
.venv/bin/python tools/diagrams_chapter01.py
.venv/bin/python tools/roadmap_chapter01.py
.venv/bin/python tools/build_chapter01.py
```

- 내용 원본: `tools/write_chapter01.py` → `manuscript/volume01-chapter01.json`
- 조판 원본: `tools/assets/bookk-B5.docx`의 첫 구역 판형·여백·테마 상속
- 본문 10.5pt 부크크 명조 Light, 제목 부크크 고딕 Light, 코드 10pt Consolas
- 저자용 의존성: `tools/requirements-docx.txt`
- UI 촬영: `tools/capture_chapter01.py`; 기존 환경을 조회하며 설치 작업은 하지 않음

2장 재생성:

```bash
.venv/bin/python tools/write_chapter02.py
.venv/bin/python tools/diagrams_chapter02.py
.venv/bin/python tools/build_chapter01.py --source manuscript/volume01-chapter02.json --output build/volume01-chapter02.docx
```

- [2장 검토 기록](editorial/chapter02-review.json)
- [2장 삽화와 생성 프롬프트](editorial/chapter02-illustrations.json)

3장 재생성:

```bash
.venv/bin/python tools/write_chapter03.py
.venv/bin/python tools/diagrams_chapter03.py
.venv/bin/python tools/build_chapter01.py --source manuscript/volume01-chapter03.json --output build/volume01-chapter03.docx
```

- [3장 검토·화면 촬영 기록](editorial/chapter03-review.json)
- [3장 삽화 생성 프롬프트](editorial/chapter03-illustrations.json)

4장 재생성:

```bash
.venv/bin/python tools/write_chapter04.py
.venv/bin/python tools/diagrams_chapter04.py
.venv/bin/python tools/build_chapter01.py --source manuscript/volume01-chapter04.json --output build/volume01-chapter04.docx
```

- [4장 검토·검증 기록](editorial/chapter04-review.json)
- [4장 야외 삽화와 생성 프롬프트](editorial/chapter04-illustrations.json)

5장 재생성:

```bash
.venv/bin/python tools/write_chapter05.py
.venv/bin/python tools/diagrams_chapter05.py
.venv/bin/python tools/build_chapter01.py --source manuscript/volume01-chapter05.json --output build/volume01-chapter05.docx
```

- [5장 검토·검증 기록](editorial/chapter05-review.json)
- [5장 삽화·생성 프롬프트](editorial/chapter05-illustrations.json)
- [브라우저 화면 촬영 기록](assets/screens/chapter05/browser/provenance.json) · [대응하는 Wazuh 화면](assets/screens/chapter05/browser/wazuh-provenance.json)
- [이전 curl 검증 기록](editorial/chapter05-curl-review.json)

6장 재생성:

```bash
.venv/bin/python tools/write_chapter06.py
.venv/bin/python tools/diagrams_chapter06.py
.venv/bin/python tools/build_chapter01.py --source manuscript/volume01-chapter06.json --output build/volume01-chapter06.docx
```

- [6장 검토·검증 기록](editorial/chapter06-review.json)
- [6장 삽화·생성 프롬프트](editorial/chapter06-illustrations.json)
- [브라우저 촬영 기록](assets/screens/chapter06/provenance.json) · [추가 촬영 기록](assets/screens/chapter06/detail-provenance.json) · [Wazuh 촬영 기록](assets/screens/chapter06/wazuh-provenance.json)
- 저자용 촬영: `tools/capture_chapter06.py`, `tools/capture_chapter06_details.py`, `tools/capture_chapter06_wazuh.py`
- 저자용 조회 검증: `tools/verify_chapter06.py`

7장 재생성:

```bash
python -m pip install -r tools/requirements-chapter07.txt
python tools/write_chapter07.py
python tools/build_chapter07.py --output build/volume01-chapter07.docx
```

- [7장 검토 기록](editorial/chapter07-review.json) · [원본 슬라이드와 공격·방어 대응표](editorial/chapter07-source-coverage.json)
- [7장 정적·조판 검사](editorial/chapter07-layout-check.json) · [슬라이드 화면 출처](assets/screens/chapter07/provenance.json)
- 화면 원본 9개는 `assets/screens/chapter07/source/`에 보존했습니다. `python tools/extract_chapter07.py "원본.pptx"`로 19개 영역을 추출합니다. 출처의 슬라이드 번호는 실제 발표 순서이며 내부 XML 파일 번호와 구분합니다.
- 그림은 저장소의 PNG를 사용합니다. 새 수집 경로 도식만 다시 만들 때는 `python tools/chapter07_collection.py --font "부크크고딕_파일.ttf"`를 사용합니다.
- `tools/check_chapter07.py DOCX경로 임시PDF경로 --bash Bash실행파일경로`로 템플릿·글꼴·참고 URL·화면 픽셀·복사용 명령·셸 구문을 검사합니다. `bash -n` 구문 분석만 수행하며 예제 명령과 DQL은 실행하지 않습니다. Word로 렌더한 임시 PDF에서 전체 지면을 별도로 확인합니다.
- [기존 삽화 재사용 기록](editorial/chapter07-illustrations.json)

8장 초안:

- [8장 Word 원고](manuscript/volume01-chapter08.docx) · [본문 JSON](manuscript/volume01-chapter08.json)
- Module 01 실습 16~21: SSH 인증 실패·성공, root 직접 로그인, sudo 실행, 계정 생성·그룹 변경·삭제.
- [복사용 명령·DQL·목록 파일](examples/chapter08/README.md) · [저자용 검토 기록](editorial/chapter08-review.md)
- [슬라이드 대응표](editorial/chapter08-source-coverage.json) · [검사 결과](editorial/chapter08-validation.json) · [실제 화면 출처](assets/screens/chapter08/provenance.json)

```bash
python tools/write_chapter08.py
python tools/build_chapter08.py --output build/volume01-chapter08.docx
```

UTF-8 모드와 `python-docx`, `Pillow`, `pypdf`를 갖춘 환경에서 실행합니다. Windows에서는 실행 전 `$env:PYTHONUTF8='1'`을 지정합니다. 저장소의 그림을 그대로 사용하며, 도식 재생성 시 `BOOK_DIAGRAM_FONT`에 부크크 고딕 Light 글꼴 파일 경로를 지정하고 `tools/diagrams_chapter08.py`를 실행합니다. `tools/check_chapter08.py DOCX경로 임시PDF경로 --bash Bash실행파일경로`는 정적 검사를 수행하며 실습 명령을 실행하지 않습니다. 실습 시험과 검색 결과는 저자용 기록에 별도로 보존했습니다. 이번 초안은 REV01에 저장하지 않았습니다.

9장 초안:

- Module 01 실습 22~28: sudoers 변경, SSH 공개 키, cron 예약, 리버스 셸, 다운로드 실행, 바이너리 변조, 로그 삭제·내용 비우기.
- 67쪽, 명령 69개, DQL 12개, 실제 화면 8개, 도식 8개, 재사용 삽화 2개. 로그 훼손은 원본을 보존하고 실습 전용 복사본으로 확인했습니다.
- [Word 원고](manuscript/volume01-chapter09.docx) · [본문 JSON](manuscript/volume01-chapter09.json) · [복사용 예제](examples/chapter09/README.md)
- [저자용 검토 기록](editorial/chapter09-review.md) · [슬라이드 대응표](editorial/chapter09-source-coverage.json) · [검사 결과](editorial/chapter09-validation.json) · [화면 출처](assets/screens/chapter09/provenance.json)
- 실제 일곱 실습의 결과와 원상복구, Discover 검색 12개를 확인했습니다. 조건부 초기 파일 생성 등 수행하지 않은 경로와 저자용 자동 접속·독자용 대화형 절차의 차이는 검토 기록에 명시했습니다. 호스트 수집은 정상화해 유지하고, 임시 접근 키·HTTP 서버·셸 연결·실습 파일은 정리했습니다.

```bash
python tools/write_chapter09.py
python tools/build_chapter09.py --output build/volume01-chapter09.docx
```

9장도 위와 같은 Python 의존성과 글꼴을 사용합니다. 도식 재생성은 `tools/diagrams_chapter09.py`, 정적 검사는 `tools/check_chapter09.py DOCX경로 임시PDF경로 --bash Bash실행파일경로`입니다. 검사는 명령을 실행하지 않습니다. 일반 원고 경로에 초안을 저장했으며 REV01은 수정하지 않았습니다.

PDF는 배포하지 않습니다. 임시 PDF·페이지 이미지는 DOCX 배치 검사용으로만 사용합니다. Consolas가 없는 환경에서는 대체 글꼴로 보일 수 있으므로 Word에서 최종 인쇄 크기를 재확인합니다.


## 10장 — 네트워크 흔적과 현재 상태 조사

Module 01 실습 29·30·62를 다룹니다. 호스트 리스닝 포트와 533 경보, Nmap TCP 스캔과 커널 DROP·4151, osquery 직접 SQL과 예약 조회의 added/removed를 연결했습니다. **55쪽, 실제 UI 영역 6개, 도식 5개, 기존 삽화 2개**이며 명령 44개·DQL 10개·osqueryi 입력 4개와 XML/SQL 복사용 파일을 제공합니다.

실제 제공된 VM에서 31337·31338 리스너, 1~1000 포트 스캔, 유효한 임시 공개 키의 등록·제거를 확인했습니다. DQL 10개를 Discover에서 대조했고, 키·수집 설정의 초기 해시와 소켓·방화벽 원상복구를 확인했습니다. 공격자 VM에 설치한 Nmap과 새 archives 검색 패턴은 유지했습니다. 처음부터 파일이 없던 경우 등 조건부 절차, 전경 셸과 저자 실행 방식의 차이는 검토 기록에 명시합니다. 새 VM 설치나 이 키로의 SSH 인증 성공을 검증했다고 주장하지 않습니다.

```bash
.venv/bin/python tools/write_chapter10.py
.venv/bin/python tools/diagrams_chapter10.py
.venv/bin/python tools/build_chapter10.py
```

- [10장 집필·검증 기록](editorial/chapter10-review.md)
- [원자료 대응표](editorial/chapter10-source-coverage.json)
- [조판·예제·검색 검증 결과](editorial/chapter10-validation.json)
- [실행·조회 증거](editorial/evidence/chapter10/2026-11-03/)

초안은 일반 원고 경로에 저장했으며 REV01과 강의 저장소는 수정하지 않았습니다. PDF는 배포하지 않습니다.

## 11장과 부록 — 장별 교정용 초안

11장은 독립된 세 실습 사례의 시간·대상·인증·프로세스·수집 결과를 대조하고, 증거 대장·시간표·대응 계획·조사 보고서를 작성하는 종합 연습입니다. **30쪽, 기존 화면 4개, 새 관계 도식 5개, 기존 삽화 1개**를 수록했습니다. PowerShell 명령 5개는 Windows에서 확인했고 DQL 6개는 8~10장에서 검증한 검색식을 재사용했습니다. 새 공격과 VM 변경, 새 화면 촬영은 수행하지 않았습니다.

부록은 **27쪽**으로 환경과 실행 위치, 명령·검색 참조, 원상복구 점검, 용어·필드 해석, 조사 양식, Module 01 실습 01~30 및 62의 장별 대응표를 제공합니다. 전체 복사용 입력 451개의 위치와 파일을 CSV 색인으로 연결했습니다. 이번 작업에서는 1~10장 원고와 REV01을 유지했고, 사용자 요청에 따라 합본은 산출물에 포함하지 않았습니다.

```bash
python tools/write_chapter11.py
python tools/write_appendices.py
python tools/build_remaining.py chapter11 appendices
```

위 조판 명령은 `build/volume01-final/`에 DOCX를 출력합니다. 확정한 원고를 저장할 때만 `--output-dir manuscript`를 지정합니다. 본문의 직접 Word 교정은 JSON·Python에 자동 반영되지 않으므로 재생성 전에 변경 내용을 보존합니다. 앞 장과 같은 글꼴 및 Python 의존성을 사용하며 Windows에서는 UTF-8 모드로 실행합니다. 저장된 그림을 사용하므로 도식 재생성은 필수가 아닙니다.

- [본문·복사용 파일·템플릿·증거 검사](editorial/chapter11-appendices-validation.json)
- [그림 출처와 재사용 기록](editorial/chapter11-assets.json)
- [PowerShell 실행 기록](editorial/evidence/chapter11/2026-11-03/)
- 정적 검사: `python tools/check_remaining.py 11장임시PDF경로 부록임시PDF경로`. 이 명령은 실습 입력을 실행하지 않습니다.

장별 DOCX는 교정 전 초안입니다. 1장에 남아 있는 VMware·Ubuntu 설치 화면 두 곳은 기존 저자 촬영 대상으로 유지합니다. PDF와 임시 페이지 이미지는 조판 검사에만 사용합니다.
