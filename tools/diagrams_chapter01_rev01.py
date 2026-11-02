"""REV01 1장 도식: 학습 순서(9개 절, 네 묶음)와 사건 노트 흐름."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import diagrams_chapter01 as base
from diagrams_chapter01 import Figure
# 학습 순서: 이해 → 설치 → 확인 → 기준점. 판면 높이를 아끼려고 네 묶음을 가로로 놓는다.
f=Figure(760)
cols=[('이해',['1.1\n구성 이해','1.2\n실습망']),('설치',['1.3\nVM·Ubuntu','1.4\n저장소·설정','1.5\nDocker·커널']),('확인',['1.6\n기동·접속','1.7\n수집기 연결']),('기준점',['1.8\n스냅샷·노트','1.9\n공격자 VM'])]
W,G,X0=318,74,15
for col,(label,items) in enumerate(cols):
 x=X0+col*(W+G)
 f.label((x,15,x+W,95),label,50)
 for row,title in enumerate(items):
  y=110+row*180;f.box((x,y,x+W,y+160),title,col%3,38)
 if col<3:f.arrow((x+W+8,280),(x+W+G-8,280))
f.label((15,660,1485,745),'1.9는 선택 · 막히면 부록 A · 설치된 VM은 1.6부터',42)
f.save('rev01-roadmap')
# 사건 노트: 공격 일지와 조사 기록을 11장에서 대조한다.
f=Figure(800)
f.box((35,35,605,235),'공격 일지\n5~10장 · 실행한 공격',0,46)
f.box((895,35,1465,235),'조사 기록\n5~10장 · Wazuh에서 확인',1,46)
f.box((450,300,1050,490),'11장 대조\n시각·출발지·입력',2,46)
f.arrow((320,240),(560,295));f.arrow((1180,240),(940,295))
f.box((35,565,605,765),'양쪽에 있음\n탐지된 행동',1,46)
f.box((895,565,1465,765),'공격 일지에만 있음\n공백 → 규칙 보완',0,46)
f.arrow((640,495),(420,560));f.arrow((860,495),(1080,560))
f.save('rev01-casebook')
