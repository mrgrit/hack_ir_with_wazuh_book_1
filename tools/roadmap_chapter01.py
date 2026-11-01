"""1장 학습 순서: 12개 절을 네 묶음으로 표시한다."""
from diagrams_chapter01 import Figure
f=Figure(1640)
rows=[('환경 준비',['1.1\n구성 이해','1.2\n가상머신 생성','1.3\n사전 확인']),('설치',['1.4\n저장소·설정','1.5\n인덱서 준비','1.6\nDocker 설치']),('실행 확인',['1.7\nkt66 기동','1.8\n화면 접속','1.9\n센서 확인']),('운용·추가 준비',['1.10\n중지·복구','1.11\n문제 해결','1.12\n공격자 VM'])]
for row,(label,items) in enumerate(rows):
 y=25+row*380
 f.label((35,y,1465,y+85),label,58)
 for col,title in enumerate(items):
  x=35+col*500;f.box((x,y+105,x+430,y+285),title,row%3,50)
  if col<2 and row<3:f.arrow((x+438,y+195),(x+488,y+195))
 if row<2:f.arrow((750,y+300),(750,y+365))
f.label((35,1490,1465,1615),'문제 해결은 필요할 때 · 공격자 VM은 5장 실습 전에 준비',45)
f.save('chapter-roadmap')
