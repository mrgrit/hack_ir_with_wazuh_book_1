# 시리즈 삽화 점검 · 2026-11-03

1권 1~11장·부록과 2권 1장의 인물 삽화 23곳을 모두 확인했다. 기존 고유 그림은 11개였다. 첫 배치 8곳을 유지하고 반복되는 15곳을 새로 제작했다. 2권 2·3장의 신규 4곳을 합하면 현재 27곳에 서로 다른 그림 27개를 사용한다. REV01은 점검·수정 대상에서 제외했다.

화풍은 제한된 색면·선명한 픽셀·점무늬 음영으로 통일하되 인물의 나이·성별·외형, 장소, 행동, 시점, 소품을 분리해 기획했다. 사무실 외에 수리 작업장·서버 통로·철도 정비소·하역장·교실·도서관 IT실을 사용했다. 기술 구성도와 실제 화면을 인물 삽화로 대체하지 않았다.

## 교체 목록

| 원고 | 새 장면 자산 |
|---|---|
| volume01-chapter05 | v1-c05-response |
| volume01-chapter06 | v1-c06-path |
| volume01-chapter06 | v1-c06-logs |
| volume01-chapter07 | v1-c07-file |
| volume01-chapter07 | v1-c07-response |
| volume01-chapter08 | v1-c08-auth |
| volume01-chapter08 | v1-c08-changes |
| volume01-chapter09 | v1-c09-fim |
| volume01-chapter09 | v1-c09-compare |
| volume01-chapter10 | v1-c10-process |
| volume01-chapter10 | v1-c10-sensor |
| volume01-chapter11 | v1-c11-evidence |
| volume01-appendices | v1-app-route |

## 조판 확인

교체 대상 DOCX 9개, 기존 472쪽을 Word로 다시 렌더해 본문 텍스트와 페이지 픽셀을 비교했다. 첫 교체 렌더는 문장·페이지 수가 같고 차이가 삽화 15곳 안에만 있었다. 삽화 원본 19개와 바뀐 지면 15쪽을 육안 검수했다. 1권 5장은 기존 삽화 단독 페이지를 관련 XSS 설명 뒤로 옮겨 77쪽에서 76쪽으로 정리하고 해당 지면을 다시 확인했다. 나머지 8개 문서는 페이지 수가 같다. 기존 그림과 수정 전 검증 기록은 이력·기존 참조를 위해 보존한다. 현재 파일 해시는 illustration-audit.json이 기준이다.

새 이미지는 built-in image_gen으로 생성했다. 전체 프롬프트는 illustration-prompts.json, 생성 파일·해시·배치 크기는 illustration-refresh.json에 있다. tools/illustration_assets.py와 장별 생성기를 함께 수정해 재생성 시 교체 그림을 사용하게 했다. 기존 프레임은 비율을 유지해 맞추며 그림을 늘려 찌그러뜨리지 않는다.

2권 3장에는 통신함 앞에서 출발지 기록을 비교하는 조사자(v2-c03-identity), 장비 보관실에서 구성원 목록과 승인서를 대조하는 두 담당자(v2-c03-permission)를 추가했다.
