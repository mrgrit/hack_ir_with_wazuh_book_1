# 해킹·침해대응 실무 with Wazuh

강의 자료와 분리한 집필용 저장소입니다. 1권 제목은 **시스템 침투와 SIEM 분석**입니다.
현재 최신 집필·검토본은 **2장 — 공격과 보안관제의 기초**입니다. 1장 수정은 보류하고 2장을 별도 DOCX로 이어 작성했습니다.

[2장 DOCX](manuscript/volume01-chapter02.docx) · [2장 예제 자료](examples/chapter02/) · [실제 화면 출처](editorial/chapter02-screenshots.json) · [2장 작성·검증 기록](editorial/chapter02-review.json)

2장은 로그인 실패 뒤 성공 사례, 인증·권한, HTTP 요청·응답, 로그·경보, Wazuh 데이터 흐름과 조사 판단을 연결합니다. 브라우저 UI에서 정상 요청을 확인하는 실습과 실제 캡처, 사건 읽기용 합성 자료를 포함합니다.

앞서 작성한 **목차·머리말·1장 DOCX**는 그대로 보존합니다. kt66 저장소의 설치 절차를 바탕으로
초보자용 설명, 개별 명령, 확인 기준, 실패 시 점검 순서, 실제 화면을 넣을 자리를 작성했습니다.

- [목차·머리말·1장 DOCX](manuscript/volume01-opening.docx)
- [1장 복사용 명령·설정 예시](examples/chapter01/)
- [1장 촬영 위치와 지시](editorial/chapter01-screenshots.json)
- [1장 작성 근거·검증 상태·편집 안내](editorial/chapter01-review.json)
- [DOCX 초기 조판 원본](manuscript/volume01-opening.json)
- [삽화 화풍·구도 기준](editorial/ILLUSTRATION_STYLE.md)

기존 29쪽 시범본은 표현 방식 참고용으로 보존합니다. 이번 집필 원고와 구분합니다.
[기존 HTML](preview.html) · [기존 PDF](build/volume01-sample.pdf) ·
[기존 원고 원본](manuscript/sample.json) · [기존 검토 기록](editorial/REVIEW.md)

## DOCX 편집

`manuscript/volume01-opening.docx`와 `manuscript/volume01-chapter02.docx`를 Word 또는 LibreOffice Writer에서 직접 편집합니다.
1장의 스크린샷 자리는 캡션·삽입 공간·촬영 지시를 포함합니다. 실제 촬영 화면으로 교체합니다. 2장의 브라우저 실습에는 검증한 실제 캡처 3장을 삽입했습니다.
새 환경에서 kt66 설치를 실행한 결과는 아직 검증하지 않았으며, 촬영하면서 확인할 항목은 검토 파일에 남겼습니다.
Ubuntu 24.04 LTS·x86_64를 집필 기준으로 잡고, 가상화 프로그램별 화면은 촬영 환경에 맞춰 확정합니다.

`volume01-opening.json`은 이번 초안의 초기 조판 원본입니다. DOCX를 수동 수정한 뒤 재생성하면
그 수정 사항이 JSON으로 자동 반영되지 않습니다. 기본 출력 경로를 별도로 두어 편집 원고를 보호합니다.
저자용 재생성 명령은 다음과 같습니다. 실습 환경에 접속하거나 설치 명령을 실행하지 않습니다.

```bash
python3 -m venv .venv-docx
.venv-docx/bin/pip install -r tools/requirements-docx.txt
.venv-docx/bin/python tools/build_docx.py
```

생성 사본은 `build/docx/volume01-opening.generated.docx`입니다. Noto Sans CJK KR와
Noto Sans Mono CJK KR 글꼴을 사용하며, 글꼴 대체와 편집기 버전에 따라 쪽 나눔은 달라질 수 있습니다.
2장 생성 사본은 다음 명령으로 만듭니다. 수동 편집한 원고 DOCX는 덮어쓰지 않습니다.

```bash
.venv-docx/bin/python tools/build_docx.py --source manuscript/volume01-chapter02.json --output build/docx/volume01-chapter02.generated.docx
```

신규 배포 형식은 DOCX이며 새 PDF는 배포하지 않습니다.

## 학습 원칙

한 단계에서 한 가지 행위만 수행합니다. 터미널 명령은 직접 입력하고, 결과를 읽은 다음
다음 단계로 이동합니다. 로그 검색은 Discover의 메뉴·검색창·필드·문서 펼치기로 진행합니다.
실습 전체를 실행하는 스크립트, 자동 로그인, 일괄 API 조회는 학습 경로에 넣지 않습니다.
예제 txt는 실행 스크립트가 아닌 개별 명령의 복사용 파일입니다. 전체 폴더를 실행하지 않습니다.
꺾쇠괄호 자리표시자는 자신의 환경에서 확인한 값으로 바꿉니다.

## 환경과 변경 범위

집필 저장소의 보존 위치는 `/home/ccc/hack_ir_with_wazuh_book_1`입니다.
원격 저장소는 https://github.com/mrgrit/hack_ir_with_wazuh_book_1 입니다.
강의 레포의 기존 파일을 수정·삭제하지 않았고, 기존 이미지의 사본만 사용했습니다.
현재 시범본은 신규 공격을 실행하거나 kt66 설정을 변경하지 않고 제작했습니다.

## 기존 시범본의 HTML·PDF 출력

`manuscript/sample.json`의 title/body가 페이지별 편집 원본입니다. HTML 본문은 복사 가능한
텍스트와 그림 경로를 포함합니다. 원고를 수정한 뒤 아래 제작 명령을 한 줄씩 실행합니다.
이 명령들은 **저자용 조판 도구**이며 kt66이나 Wazuh에 접속하지 않습니다.

```bash
python3 tools/build.py
python3 tools/typeset_pdf.py
```

PDF 출력에는 Python Pillow, 시스템 Cairo·Pango·librsvg, Noto Sans CJK KR 글꼴이 필요합니다.
PDF는 Cairo/Pango로 출력했습니다. Chromium으로 HTML 29쪽의 넘침과 이미지 로딩도 확인했습니다.
브라우저 기반 출력 도구 render_pdf.py는 별도 출력 방식입니다.
`tools/draft_sample.py`는 최초 시범본 생성 기록이며 다시 실행하면 원고 편집 내용을 덮어씁니다.
`tools/diagrams.py`는 생성형 픽셀오피스 삽화에 한글 설명을 별도 조판하는 SVG 구성 도구입니다.
삽화 원본은 `assets/illustrations/`, 내장 imagegen 도구의 최종 프롬프트는 `editorial/illustration-prompts.json`에 있습니다. 실제 화면 캡처와 구분합니다.
