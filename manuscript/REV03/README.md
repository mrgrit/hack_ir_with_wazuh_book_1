# REV03 — 1권 순차 교정

현재 수록 파일은 **1장 전체**이다. 머리말·일러두기·권 구성·1.1~1.9·정리·확인 문제와 해설·참고문헌을 포함한다.

- 편집 원본: `volume01-chapter01.docx` — 부크크 B5, 최종 Word 렌더 38쪽.
- 조판 소스: `volume01-chapter01.json`.
- 복사용 입력과 기록 양식: 저장소 루트의 `examples/rev03/chapter01`.
- 설치 상세는 기존 `manuscript/REV02/volume01-appendix-a.docx`의 A.1~A.3, A.12~A.15를 함께 사용한다. 본문의 명령 번호와 예제 색인으로 찾는다.
- 교정·검증 기록: `editorial/REV03/chapter01-review.md`, `chapter01-validation.json`, `chapter01-visual-review.json`.

1.2에서 작성하기 시작한 준비 기록에 설치값·접속·수집기 상태를 차례로 추가한다. 1.8에서는 재기동 결과를 처음 기록과 대조한다. 장말에는 실행 순서 없이 같은 환경을 독립적으로 점검하고, 2장의 SSH 인증 실패 실습에 사용할 환경과 기록을 준비한다.

명령·쿼리는 연한 회색 바탕과 왼쪽 구분선으로 표시한다. 실제 UI 캡처에는 얇은 테두리를 넣고, 표 머리행에는 회색 음영·가로/세로 가운데 정렬·굵은 글씨를 적용한다.

사용자의 2026-11-04 요청에 따라 병렬 집필 없이 절 순서대로 교정했다. 이후에도 각 장의 교정·검수가 끝나면 해당 장의 변경을 커밋하고 push한다. REV01과 기존 REV02 원고는 보존한다.

## 다시 조판하기

저장소 루트에서 Python으로 순서대로 실행한다. 부크크 글꼴과 `python-docx`, `Pillow`가 필요하다.

```text
python tools/diagrams_rev03_chapter01.py
python tools/sync_inputs_rev03_chapter01.py
python tools/build_volume01_rev03.py manuscript/REV03/volume01-chapter01.json
```

검사용 렌더는 Windows Word가 설치된 환경에서 `tools/render_rev02.ps1`의 `-InputPattern`에 REV03 DOCX를 지정한다. 렌더 뒤 `tools/rasterize_rev02.py`와 `tools/check_rev03_chapter01.py`로 확인한다. PDF와 쪽 이미지는 `build/REV03`의 임시 검수물이며 배포 파일에 포함하지 않는다.

검사 도구에는 렌더 디렉터리를 첫 인자로 전달한다. `python-docx`, `pypdf`, Bash가 필요하다. `--check-baseline`은 교정 당시 로컬 작업 파일의 보존 여부를 확인하는 선택 옵션이며, 새로 내려받은 저장소의 일반 검증에는 사용하지 않는다.

실습 절차는 기준 kt66 코드·공식 문서·기존 실제 화면과 대조했다. 이번 교정에서 새 VM 설치, 공격 실행, 신규 UI 촬영은 수행하지 않았다.
