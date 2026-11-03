# 11장 복사용 자료

명령은 Windows PowerShell에서 저장소 루트를 기준으로 한 블록씩 사용한다. DQL은 본문의 사례별 시간대·기간·패턴을 함께 지정한다. 기존 장에서 UI 검증한 검색식을 재사용하며 이번 장에서 재공격하지 않는다. evidence는 기존 경보의 발췌본이며 원본 파일 위치와 선택 기준·해시는 manifest.json에 있다. 양식 CSV는 UTF-8 BOM, 문서 양식은 UTF-8이다.

증거 사본 JSON은 evidence/.gitattributes로 줄바꿈 자동 변환을 끈다. manifest의 sha256은 배포 사본, source_sha256은 지정 커밋의 Git 원본, source_checkout_sha256은 집필 PC 작업 사본의 해시이다. 원본 작업 사본은 Git 설정에 따라 줄바꿈이 바뀔 수 있다. 검사는 지정 커밋의 원본 바이트와 발췌 내용을 함께 대조한다.
