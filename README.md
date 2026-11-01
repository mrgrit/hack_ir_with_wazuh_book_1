# 해킹·침해대응 실무 with Wazuh

1권 **시스템 침투와 SIEM 분석**의 집필 저장소입니다.

기존 1~3장 원고를 백지화하고 **머리말·미리 안내·1장**을 새로 썼습니다. 핵심 설명, 독자의 행동, 확인 기준을 짧게 제시합니다. 이전 원고는 Git 이력에만 남습니다.

- **[새 원고 DOCX](manuscript/volume01-chapter01.docx)** — 부크크 B5, 편집·검토용
- [복사용 명령](examples/chapter01/) — 본문의 C01 번호와 대응
- [집필 지침](AGENTS.md)
- [검토·검증 기록](editorial/chapter01-review.json)

1장은 VMware·Ubuntu 준비, kt66 설치·기동, 웹·Wazuh 접속, 센서 확인, 중지·복구를 다룹니다. 1권 전체 범위는 Module 01 실습 01~30 및 62, 11장과 부록입니다. 이번 산출물에 2장 이후 본문은 없습니다.

## 확인한 범위

kt66 커밋 `63d4180b1d6866de986ef263a3bd831d6082b5d5`의 코드·설정과 공식 문서를 대조했습니다. 기존 가동 환경에서 웹 응답, 데모 계정 Wazuh 로그인, kt66-host 연결 상태를 확인하고 실제 화면을 촬영했습니다.

**새 VMware VM에 대한 설치·중지·스냅샷 복원은 실행 검증 전입니다.** VMware·Ubuntu 설치 화면 두 곳은 저자 촬영 지시를 두었습니다. 나머지 그림은 실제 삽입했습니다. 강의·kt66 저장소는 수정하지 않았습니다.

## 편집과 재생성

DOCX를 직접 편집할 수 있습니다. 조판기는 기본적으로 `build/`에 출력하므로 검토 중인 원고를 덮어쓰지 않습니다. DOCX에서 고친 내용이 Python·JSON 원본에 자동 반영되지는 않습니다.

```bash
.venv/bin/python tools/write_chapter01.py
.venv/bin/python tools/diagram_chapter01.py
.venv/bin/python tools/build_chapter01.py
```

- 내용 원본: `tools/write_chapter01.py` → `manuscript/volume01-chapter01.json`
- 조판 원본: `tools/assets/bookk-B5.docx`의 첫 구역 판형·여백·테마 상속
- 본문 10.5pt 부크크 명조 Light, 제목 부크크 고딕 Light, 코드 10pt Consolas
- 저자용 의존성: `tools/requirements-docx.txt`
- UI 촬영: `tools/capture_chapter01.py`; 기존 환경을 조회하며 설치 작업은 하지 않음

PDF는 배포하지 않습니다. 임시 PDF·페이지 이미지는 DOCX 배치 검사용으로만 사용합니다. Consolas가 없는 환경에서는 대체 글꼴로 보일 수 있으므로 Word에서 최종 인쇄 크기를 재확인합니다.
