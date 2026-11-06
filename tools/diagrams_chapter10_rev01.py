"""REV01 10장 도식: 학습 순서, 같은 리스너를 보는 세 기록의 시각, 스캔 한 번이 기록마다 남는 수."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import diagrams_chapter01 as base
base.OUT=base.ROOT/'assets/figures/chapter10';base.OUT.mkdir(parents=True,exist_ok=True)
Figure=base.Figure

# 학습 순서.
f=Figure(580)
cols=[('준비',['10.1\n세 가지 기록']),('관찰',['10.2\n새 리스닝\n포트','10.3\n포트 스캔과\n방화벽']),
      ('현재 상태',['10.4\nosquery\n직접 조회','10.5\n원상복구와\nremoved']),('분석·마무리',['10.6\n교차 분석','10.7\n정의 확인'])]
W,G,X0=318,74,15
for col,(label,items) in enumerate(cols):
 x=X0+col*(W+G)
 f.label((x,15,x+W,95),label,46)
 for row,title in enumerate(items):
  y=110+row*180;f.box((x,y,x+W,y+160),title,col%3,34)
 if col<3:f.arrow((x+W+8,190),(x+W+G-8,190))
f.label((15,485,1485,565),'같은 변화를 기록마다 다른 시각과 다른 수로 본다',38)
f.save('rev01-roadmap')

# 같은 리스너(31337)를 세 기록이 본 시각.
f=Figure(700)
X0,X1=420,1330
def x(m):return int(X0+(m-36.5)/(49-36.5)*(X1-X0))   # m: 08시 기준 분(소수)
f.label((15,5,1485,70),'31337 리스너 · 2026-11-03 08:36~08:49 (KST)',36)
rows=[('auditd\n80792',0,[(36+55/60,'nc 실행 08:36:55')]),
      ('osquery\n24010 · 60초',1,[(37+1/60,'added 08:37:01'),(45,'removed 08:45:00')]),
      ('netstat\n533 · 360초',2,[(42+21/60,'현재 출력 08:42:21'),(48+21/60,'이전 출력 08:48:21')])]
for i,(name,c,evs) in enumerate(rows):
 y=100+i*170
 f.box((15,y,300,y+130),name,c,30)
 f.d.line((X0,y+65,X1,y+65),fill=base.INK,width=3)
 for m,t in evs:
  xx=x(m);f.d.ellipse((xx-14,y+51,xx+14,y+79),fill=base.INK)
  lx=min(max(xx-160,320),1490-320);f.label((lx,y+2,lx+320,y+48),t,28)
f.label((x(44)-260,640,x(44)+260,690),'08:44 nc 종료(Ctrl+C)',28)
f.d.line((x(44),95,x(44),635),fill=base.INK,width=3)
f.save('rev01-latency')

# 스캔 한 번이 기록마다 남는 수.
f=Figure(820)
stages=[('Nmap이 조사한 포트','1,000개 · filtered 993',0),('방화벽 LOG 상한(4.9초)','처음 200 + 초당 100 ≈ 690줄',1),
        ('아카이브의 DROP 기록','592건',2),('경보 인덱스','4151 1건 (4101은 저장 안 함)',0)]
for i,(a,b,c) in enumerate(stages):
 y=20+i*190;w=1450-i*190;x0=(1500-w)//2
 f.box((x0,y,x0+w,y+150),a+'\n'+b,c,34)
 if i<3:f.arrow((750,y+152),(750,y+186))
f.save('rev01-funnel')
print('3 chapter 10 REV01 diagrams')
