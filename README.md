# 해킹·침해대응 실무 with Wazuh

강의 자료와 분리한 집필용 로컬 Git 저장소입니다. 1권 제목 제안 **시스템 침투와 SIEM 분석**을 시범 표지에 적용했습니다.
시범 원고는 SQL 인젝션·SSH 인증 기록·osquery 상태 조사의 세 사례를 B5 29쪽으로 구성합니다.

- [브라우저로 읽기](preview.html)
- [PDF 시범 원고](build/volume01-sample.pdf)
- [원고 원본](manuscript/sample.json)
- [실습별 복사 파일](examples/)
- [제작·검증 현황](editorial/REVIEW.md)
- [화면 출처](assets/screens/provenance.json)
- [삽화 화풍·구도 기준](editorial/ILLUSTRATION_STYLE.md)

## 학습 원칙

한 단계에서 한 가지 행위만 수행합니다. 터미널 명령은 직접 입력하고, 결과를 읽은 다음
다음 단계로 이동합니다. 로그 검색은 Discover의 메뉴·검색창·필드·문서 펼치기로 진행합니다.
실습 전체를 실행하는 스크립트, 자동 로그인, 일괄 API 조회는 학습 경로에 넣지 않습니다.
예제 txt는 실행 스크립트가 아닌 개별 명령의 복사용 파일입니다. 전체 폴더를 실행하지 않습니다.
꺾쇠괄호 자리표시자는 자신의 환경에서 확인한 값으로 바꿉니다.

## 환경과 변경 범위

쓰기 허용 범위 때문에 현재 저장소 위치는 `/tmp/wazuh-ir-books`입니다. /tmp는 임시 저장 영역이므로
후속 작업 전에 보존할 작업 위치로 이동해야 합니다. 원격 저장소는 https://github.com/mrgrit/hack_ir_with_wazuh_book_1 입니다.
강의 레포의 기존 파일을 수정·삭제하지 않았고, 기존 이미지의 사본만 사용했습니다.
현재 시범본은 신규 공격을 실행하거나 kt66 설정을 변경하지 않고 제작했습니다.

## 편집과 출력

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
