"""REV01 3장 도식: 학습 순서, 조건을 하나씩 더해 좁히는 검색."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import diagrams_chapter01 as base
base.OUT=base.ROOT/'assets/figures/chapter03';base.OUT.mkdir(parents=True,exist_ok=True)
Figure=base.Figure

# 학습 순서: 준비 → 검색 → 확인.
f=Figure(760)
cols=[('준비',['3.1\n검색의 세 조건','3.2\n대상 고르기','3.3\n기간 정하기']),('검색',['3.4\nDQL 기초','3.5\n결과와 상세','3.6\n사례 좁히기']),('확인',['3.7\n내 기록 찾기','3.8\n0건일 때','3.9\n조사 기록'])]
W,G,X0=420,105,15
for col,(label,items) in enumerate(cols):
 x=X0+col*(W+G)
 f.label((x,15,x+W,95),label,50)
 for row,title in enumerate(items):
  y=110+row*180;f.box((x,y,x+W,y+160),title,col,40)
 if col<2:f.arrow((x+W+10,280),(x+W+G-10,280))
f.label((15,660,1485,745),'실행 위치: Windows 브라우저 · Wazuh Dashboard의 Discover',42)
f.save('rev01-roadmap')

# 조건을 하나씩 더하고 건수를 본다. 0건이면 마지막 조건을 뺀다.
f=Figure(700)
steps=[('agent.name: "bastion"','에이전트'),('AND rule.id: "5710"','+ 규칙'),('AND data.srcip: "10.20.30.254"','+ 출발지')]
for i,(q,label) in enumerate(steps):
 y=40+i*200;inset=i*70
 f.box((35+inset,y,1065-inset,y+150),q,i,40)
 f.label((1110,y,1465,y+150),label+'\n건수 확인',40)
 if i<2:f.arrow((550,y+156),(550,y+194))
f.label((35,620,1465,690),'결과가 0건이 되면 마지막에 더한 조건부터 뺀다',42)
f.save('rev01-narrowing')
print('2 chapter 3 REV01 diagrams')
