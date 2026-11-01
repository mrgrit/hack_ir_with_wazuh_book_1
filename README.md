# 해킹·침해대응 실무 with Wazuh

1권 **시스템 침투와 SIEM 분석**의 집필 저장소입니다.

기존 1~3장 원고를 백지화하고 **머리말·미리 안내·1장**을 새로 썼고 **2~5장 초안**을 추가했습니다. 핵심 설명, 독자의 행동, 확인 기준을 짧게 제시합니다. 이전 원고는 Git 이력에만 남습니다.

- **[머리말·1장 DOCX](manuscript/volume01-chapter01.docx)** — 부크크 B5, 편집·검토용
- **[2장 초안 DOCX](manuscript/volume01-chapter02.docx)** — 공격과 보안관제의 기초, 9쪽
- **[3장 초안 DOCX](manuscript/volume01-chapter03.docx)** — Wazuh 기본 운용, 12쪽
- **[4장 초안 DOCX](manuscript/volume01-chapter04.docx)** — 로그 수집과 탐지 규칙, 31쪽
- **[5장 초안 DOCX](manuscript/volume01-chapter05.docx)** — 웹 공격의 시작과 입력값 검증, 55쪽
- [5장 복사용 명령·검색식·실제 로그](examples/chapter05/)
- [4장 명령·검색식·규칙 파일](examples/chapter04/)
- [3장 복사용 검색식·조사 양식](examples/chapter03/)
- [2장 사례·복사용 명령](examples/chapter02/)
- [복사용 명령](examples/chapter01/) — 본문의 C01 번호와 대응
- [집필 지침](AGENTS.md)
- [검토·검증 기록](editorial/chapter01-review.json)
- [캐릭터 삽화](assets/illustrations/chapter01/) · [생성 프롬프트·출처 기록](editorial/chapter01-illustrations.json)

1장은 VMware·Ubuntu 준비, kt66 설치·기동, 웹·Wazuh 접속, 센서 확인, 중지·복구를 다룹니다. kt66과 공격자 VM의 브리지 구성도와 선택적 공격자 VM 준비 절차도 포함합니다. 공격자 VM은 Ubuntu 22.04 Live Server를 사용하며 5장의 선택 curl 실습과 이후 터미널 실습에 필요합니다. 도구 일괄 설치 명령은 C01-52입니다. 머리말·1장은 35쪽이며 설명 도식 7개와 작은 캐릭터 삽화 3개를 수록합니다. 1장의 12개 절은 한 쪽의 학습 순서 도식으로 정리했습니다. 작은 삽화는 인물·장소·소품을 달리한 v2로 교체했습니다. 1권 전체 범위는 Module 01 실습 01~30 및 62, 11장과 부록입니다. 2장은 기존 kt66의 SSH 인증 실패 경보를 사례로 로그·탐지·판단·대응을 설명합니다. 새 공격을 실행하지 않고 기존 경보 조회와 시각·웹 응답 확인을 수행했습니다.

3장은 Discover에서 인덱스·기간·DQL을 지정하고 경보의 필드·원문을 읽는 실습입니다. 실제 UI 화면 8개, 개념 도식 2개, 작은 삽화 1개를 수록했습니다. 기존 SSH 사례를 검색한 두 조건은 각각 2건을 반환했습니다. 모든 장의 참고 자료에는 제목과 전체 URL을 함께 인쇄합니다.

4장은 bastion에 확인 문구를 기록하고 아카이브에서 찾은 뒤, 사용자 규칙 100410을 적용해 새 경보를 생성하는 실습입니다. 수집·규칙 시험·실제 경보 생성·규칙 제거와 재시작을 기존 kt66에서 검증했습니다. 실제 화면 7개, 도식 5개, 야외 통신함 점검 삽화 1개를 수록했습니다. SSH 원문과 추출 필드의 대응, 실제 디코더·규칙 파일의 위치와 조회 절차, logger·grep의 옵션과 정규표현식 해석을 보완했습니다.

## 확인한 범위

5장은 Module 01 실습 01~03의 SQL 인젝션·XSS·경로 조작을 **브라우저 중심**으로 진행합니다. Windows 웹 이름 등록 → DVWA 로그인 → 첫 DB 초기화 → Low 선택 → 실습 메뉴 → 입력·Submit → Network 응답 → Wazuh 기록 순서입니다. 브라우저와 Wazuh의 실제 화면 25개, 설명 도식 6개, 삽화 2개를 수록했습니다. 전체 55쪽이며 명령 37개, DQL 7개와 브라우저 복사용 입력 8개를 제공합니다.

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

PDF는 배포하지 않습니다. 임시 PDF·페이지 이미지는 DOCX 배치 검사용으로만 사용합니다. Consolas가 없는 환경에서는 대체 글꼴로 보일 수 있으므로 Word에서 최종 인쇄 크기를 재확인합니다.
