# REV01 — 1장 재작성본

기존 `manuscript/volume01-chapter01.*`은 그대로 두고, 재작성본을 이 디렉터리에 둔다. 검토 후 채택하면 기존 파일을 교체한다.

## 파일

| 파일 | 내용 |
|---|---|
| `volume01-chapter01.json` / `.docx` | 표지·머리말·일러두기·목차 + 1장 (렌더 41쪽) |
| `volume01-appendix-a.json` / `.docx` | 부록 A 설치 상세와 문제 해결 (렌더 8쪽) |
| `../../examples/rev01/chapter01/` | C01-01~26 복사용 명령, `manifest.json`, `casebook.txt`(사건 노트 양식) |
| `../../examples/rev01/appendix-a/` | CA-01~08 복사용 명령, `manifest.json` |
| `../../assets/figures/chapter01/rev01-*.png` | 1장 로드맵(도식 1-1), 사건 노트 흐름(도식 1-8) |

## 기존 1장 대비 변경

1. **구성** — 12절을 9절로 줄였다. 1.1~1.2 이해 → 1.3~1.5 설치 → 1.6~1.7 확인 → 1.8 기준점 → 1.9 공격자 VM(선택).
2. **설치 상세 분리** — VMware·Ubuntu 클릭 절차, 설치 실패 대응, 화면·수집기 문제 해결을 부록 A로 옮겼다. 본문은 "무엇을 왜 하는가"와 확인 기준만 남긴다.
3. **장 도입부** — 시나리오, 학습 목표, 가로형 로드맵, 준비와 완료 기준 표를 첫 펼침면에 둔다.
4. **장 마무리** — 핵심 정리, 확인 문제 5개와 해설, 더 읽을거리(전체 URL)를 둔다.
5. **사건 노트** — 1.8에서 "공격 일지"와 "조사 기록" 두 칸을 만든다. 11장에서 두 기록을 대조해 탐지 공백을 찾는 흐름의 시작점이다.
6. **목차** — 장마다 "조사 질문" 열을 둔다.
7. **일러두기** — 표기 원칙 표와 예시값(IP·계정·경로) 표를 모았다.

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

## 미검증·작가 작업

- 새 VM에서 처음부터 설치하는 절차는 실행 검증하지 않았다(기존 kt66 화면과 명령 문법만 확인).
- 부록 A의 캡처 자리 2곳(VMware 설정 요약, Ubuntu 설치 첫 화면)은 저자가 직접 촬영해 넣는다.
- 렌더 쪽수는 LibreOffice 대체 글꼴 기준이다. 부크크 글꼴이 있는 Word에서 쪽 나눔을 다시 확인한다.
