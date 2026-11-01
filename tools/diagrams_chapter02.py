"""2장 개념 도식: 사례의 확인 단계와 탐지·대응 흐름."""
import diagrams_chapter01 as drawing
from pathlib import Path
drawing.OUT=drawing.ROOT/'assets/figures/chapter02';drawing.OUT.mkdir(parents=True,exist_ok=True)
Figure=drawing.Figure
f=Figure(650)
f.box((400,30,1100,170),'SSH 인증 요청',0,56)
f.arrow((550,180),(340,280));f.arrow((950,180),(1160,280))
f.box((35,290,670,440),'인증 실패',1,55);f.box((830,290,1465,440),'인증 성공',2,55)
f.label((35,465,690,625),'같은 출발지의\n반복 시도 확인',47)
f.label((805,465,1465,625),'승인된 접속인지 확인\n후속 활동 조사',47);f.save('authentication')
f=Figure(390)
for i,t in enumerate(['로그\n인증 실패 원문','디코더\n계정·주소 추출','탐지 규칙\n조건 대조']):
 x=35+i*500;f.box((x,35,x+430,230),t,i,47)
 if i<2:f.arrow((x+438,130),(x+488,130))
f.label((35,250,1465,370),'조건·경보 설정 충족 → 규칙 번호와 분석 결과 저장',46);f.save('detection')
f=Figure(610)
for x,y,t,c in [(35,35,'기록 확인',0),(850,35,'범위 조사',1),(850,350,'대응 결정',2),(35,350,'복구·재확인',0)]:f.box((x,y,x+615,y+180),t,c,54)
f.arrow((660,125),(840,125));f.arrow((1157,225),(1157,340));f.arrow((840,440),(660,440));f.save('response')
print('3 chapter 2 diagrams')
