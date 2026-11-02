"""REV01 2장 도식: 학습 순서, 원문에서 필드로, 직접 남긴 SSH 기록의 출발지 경로."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import diagrams_chapter01 as base
base.OUT=base.ROOT/'assets/figures/chapter02';base.OUT.mkdir(parents=True,exist_ok=True)
Figure=base.Figure

# 학습 순서: 읽기 → 연결 → 판단. 세 묶음을 가로로 놓는다.
f=Figure(760)
cols=[('읽기',['2.1\n원문 읽기','2.2\n직접 남기기']),('연결',['2.3\n로그 → 경보','2.4\n시각 맞추기']),('판단',['2.5\n시도와 결과','2.6\n관제와 대응','2.7\n조사 기록'])]
W,G,X0=420,105,15
for col,(label,items) in enumerate(cols):
 x=X0+col*(W+G)
 f.label((x,15,x+W,95),label,50)
 for row,title in enumerate(items):
  y=110+row*180;f.box((x,y,x+W,y+160),title,col,40)
 if col<2:f.arrow((x+W+10,280),(x+W+G-10,280))
f.label((15,660,1485,745),'사례: bastion의 SSH 로그인 실패 한 건 · 2.2만 터미널 실습',42)
f.save('rev01-roadmap')

# 원문의 어느 부분이 어느 필드가 되는가.
f=Figure(905)
f.label((35,20,735,95),'원문 · /var/log/auth.log',42);f.label((835,20,1465,95),'경보 필드',42)
rows=[('sshd[7249]','decoder.name: sshd'),('invalid user book03_probe','data.srcuser'),('from 10.20.30.254','data.srcip'),
      ('invalid user (규칙 조건)','rule.id: 5710'),('줄 전체','full_log')]
for i,(raw,field) in enumerate(rows):
 y=115+i*155
 f.box((35,y,735,y+125),raw,0,38);f.box((835,y,1465,y+125),field,1,38)
 f.arrow((745,y+62),(825,y+62))
f.save('rev01-fields')

# kt66 VM에서 bastion 내부 주소로 접속하면 sshd가 기록하는 출발지.
f=Figure(520)
f.box((25,40,465,260),'kt66 VM 터미널\nssh book02_probe\n@10.20.30.201',0,38)
f.box((530,40,970,260),'kt66 VM의\next망 주소\n10.20.30.254',2,40)
f.box((1035,40,1475,260),'bastion\n10.20.30.201\nsshd · 22번',1,40)
f.arrow((472,150),(522,150));f.arrow((977,150),(1027,150))
f.label((25,300,1475,480),'sshd는 직접 연결된 상대의 주소를 출발지로 기록한다\n→ data.srcip = 10.20.30.254',42)
f.save('rev01-ssh-path')
print('3 chapter 2 REV01 diagrams')
