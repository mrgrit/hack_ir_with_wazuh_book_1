# 삽화 인체·시점 재검토 — 2026-11-03

사용자가 지적한 세 팔, 문서 뒷면 읽기, 부자연스러운 문서 각도를 계기로 1·2권 원고에 실제 삽입된 삽화 27개를 각각 열어 다시 확인했다. 이전 다양화 작업의 육안 검수에서 이 오류들을 놓쳤다. 당시 검수 기록은 인체·시점 정확성의 근거로 사용하지 않으며, 현재 판정은 이 기록과 illustration-physical-review.json을 따른다.

15개를 고치고 12개를 유지했다. 종이 앞면은 읽는 인물을 향하게 하고, 두 사람이 함께 검토하는 문서는 카트·작업대에 놓았다. 태블릿 뒷면을 누르던 동작은 양손으로 가장자리를 받치는 동작으로 바꿨다. 2권 3장의 터번 인물은 한국의 장년 기술자로 바꿨다. 장면의 장소·복장·행동 차이는 유지했다.

## 확인 범위

- 원본 27개와 교체 결과 15개를 개별 확인했다. 인물별 팔·손 연결, 시선, 종이·화면의 앞뒤, 소품의 지지점을 확인했다.
- 12개 DOCX의 613쪽을 교체 직전본과 비교했다. 페이지 수와 모든 페이지의 추출 텍스트가 같다. 598쪽의 렌더 픽셀이 같고, 차이는 삽화가 있는 15쪽에 있다. 그 15쪽은 실제 지면 크기로 별도 열어 확인했다.
- 27개 자산 해시와 원고 내부 이미지 해시를 대조했다. 기존 프레임·본문·캡션은 유지했다. 1권 4장 그림의 가로 1픽셀 차이는 프레임 내부 여백으로 비율을 맞췄다.
- 1권 1장·3장의 검은 외곽 잔상을 추가 제거하고 두 원고를 다시 렌더·비교했다.
- 기본 렌더러는 LibreOffice 미설치로 실행되지 않아 Microsoft Word의 숨김 COM 렌더와 pypdfium2를 사용했다. PDF·PNG는 build 내부 검사물이다.

## 장별 교정 때 확인할 기존 항목

1권 1장 39쪽의 삽화 단독 지면과 1권 3장 14쪽 표 테두리 간격은 수정 직전본에도 있던 상태이다. 이번 삽화 교정으로 장 전체의 교정·조판이 완료되었다고 표시하지 않는다. 사용자가 예정한 장별 교정에서 배치를 검토한다.

## 자산과 프롬프트

생성 엔진은 built-in image_gen이다. 현재 파일의 생성명·수정 전후 해시·개별 판정·전체 수정 프롬프트는 illustration-physical-review.json, 재생성용 경로와 프레임은 illustration-refresh.json에 있다. illustration-prompts.json의 physical_correction_2026_11_03이 이번 수정 프롬프트이다. 그 이전 scenes는 최초 제작 이력이다.

| 원고 | 수정 자산 |
|---|---|
| volume01-chapter05 | assets/illustrations/diversity/v1-c05-response.png |
| volume01-chapter09 | assets/illustrations/diversity/v1-c09-compare.png |
| volume02-chapter03 | assets/illustrations/diversity/v2-c03-permission.png |
| volume01-chapter01 | assets/illustrations/chapter01/notes-v2.png |
| volume01-chapter03 | assets/illustrations/chapter03/time.png |
| volume01-chapter04 | assets/illustrations/chapter04/field-check.png |
| volume01-chapter06 | assets/illustrations/diversity/v1-c06-logs.png |
| volume01-chapter07 | assets/illustrations/diversity/v1-c07-file.png |
| volume01-chapter08 | assets/illustrations/diversity/v1-c08-auth.png |
| volume01-chapter08 | assets/illustrations/diversity/v1-c08-changes.png |
| volume01-chapter09 | assets/illustrations/diversity/v1-c09-fim.png |
| volume01-chapter10 | assets/illustrations/diversity/v1-c10-process.png |
| volume01-appendices | assets/illustrations/diversity/v1-app-route.png |
| volume02-chapter01 | assets/illustrations/diversity/v2-c01-evidence.png |
| volume02-chapter03 | assets/illustrations/diversity/v2-c03-identity.png |
