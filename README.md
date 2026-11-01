# 해킹·침해대응 실무 with Wazuh

강의 자료와 분리한 집필용 저장소입니다. 1권 제목은 **『시스템 침투와 SIEM 분석』**입니다.
직접 공격을 실행하고, 흔적을 분석하며, 침해에 대응하는 과정을 초보자(대학 1~2학년) 눈높이로 다룹니다.

현재 원고는 **머리말과 1장(kt66 실습 환경 준비)**까지입니다.

- [머리말·1장 DOCX](manuscript/volume01-opening.docx) — 부크크 B5 서식으로 조판
- [원고 내용 소스(JSON)](manuscript/volume01-opening.json)
- [1장 복사용 명령·설정 예시](examples/chapter01/)
- [삽화 화풍·구도 기준](editorial/ILLUSTRATION_STYLE.md) · [삽화 원본](assets/illustrations/)

## 서식과 조판

최종 산출물은 **부크크(Bookk) B5(46배판) Word 서식**을 그대로 따릅니다. 본문은 **부크크 명조 Light**,
제목·강조는 **부크크 고딕 Light**, 명령·코드는 Consolas 를 쓰고, 색을 쓰지 않는 단순한 표로 조판합니다.
페이지 크기·여백·테마는 서식 템플릿(`tools/assets/bookk-B5-template.docx`)을 base 로 열어 그대로 상속합니다.

원고는 두 단계로 만듭니다. 내용을 `build_opening_src.py` 가 JSON 으로 쓰고, `build_bookk.py` 가 그 JSON 을
부크크 서식 DOCX 로 조판합니다. 두 도구 모두 **저자용 조판 도구이며 kt66·Wazuh 에 접속하지 않습니다.**

```bash
python3 -m venv .venv-docx
.venv-docx/bin/pip install -r tools/requirements-docx.txt
.venv-docx/bin/python tools/build_opening_src.py                 # 내용 → manuscript/volume01-opening.json
.venv-docx/bin/python tools/build_bookk.py                        # JSON → manuscript/volume01-opening.docx
```

부크크 명조/고딕 글꼴은 부크크 서식 배포본에 포함되어 있습니다(저자 PC에 설치). 이 저장소에는 글꼴을
동봉하지 않습니다. 글꼴이 없는 환경에서 열면 Word 가 대체 글꼴로 표시하므로 쪽 나눔이 달라질 수 있습니다.
신규 배포 형식은 DOCX 이며 PDF 는 배포하지 않습니다.

## 집필 원칙

자세한 기준은 [AGENTS.md](AGENTS.md) 에 있습니다. 요약하면,

- 학습자는 화면을 보며 한 명령씩 입력하고, UI 를 클릭하고, 결과를 읽습니다. 실습 전체를 하나의 스크립트·
  API 로 대체하지 않습니다. `examples/chapterNN/` 의 txt 는 명령을 한 줄씩 복사하는 파일이며 폴더를 통째로
  실행하지 않습니다. 파일 이름의 C 번호가 본문 명령 번호와 같습니다.
- 낯선 명령은 처음 등장할 때 역할·기본 구문·사용한 옵션과 기호·정상 결과를 함께 설명합니다.
- 실제 화면 캡처와 레트로 픽셀오피스 삽화를 명시적으로 구분합니다. 설치 화면은 저자가 촬영해 삽입할
  자리(캡션·촬영 지시 포함)를 본문에 마련했습니다. 검증하지 않은 성공을 주장하지 않습니다.
- 1장 설치 절차는 kt66 저장소(기준 커밋 `63d4180`)의 문서·코드를 대조해 서술했습니다.

## 범위

1권은 강의 Module 01 의 실습 01~30 및 62 를 실습 기반으로 삼습니다(11장 + 부록). 머리말·1장을 먼저
집필했고, 2장(공격과 보안관제 기초)부터 이어서 집필합니다.

## 환경

집필 저장소의 보존 위치는 `/home/ccc/hack_ir_with_wazuh_book_1`,
원격 저장소는 https://github.com/mrgrit/hack_ir_with_wazuh_book_1 입니다.
강의 레포의 파일을 수정·삭제하지 않습니다.
