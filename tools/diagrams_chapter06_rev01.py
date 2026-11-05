"""REV01 6장 도식: 학습 순서, 검증 환경 접속 기록의 출발지별 타임라인.

타임라인 값은 editorial/evidence/chapter06/wazuh-archives-records.json(2026-11-01 21:31:58~21:32:32 KST,
web 접속 기록 63건)에서 센 것이다.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import diagrams_chapter01 as base
base.OUT=base.ROOT/'assets/figures/chapter06';base.OUT.mkdir(parents=True,exist_ok=True)
Figure=base.Figure
from PIL import ImageFont

# 학습 순서: 공격 → 분석 → 마무리.
f=Figure(930)
cols=[('공격',['6.1\n준비','6.2\n경로 탐색','6.3\n헤더·메서드','6.4\n긴 URL']),('',['6.5\n인증 시도']),
      ('분석',['6.6\n분포와 필터','6.7\n피벗과 타임라인']),('마무리',['6.8\n원본·정의 확인','6.9\n원상복구','6.10\ncurl(선택)'])]
W,G,X0=318,74,15
for col,(label,items) in enumerate(cols):
 x=X0+col*(W+G)
 if label:f.label((x,15,x+W,95),label,50)
 for row,title in enumerate(items):
  y=110+row*180;f.box((x,y,x+W,y+160),title,0 if col<2 else col-1,36)
 if col<3:f.arrow((x+W+8,280),(x+W+G-8,280))
f.label((15,830,1485,915),'공격 일지에 적으며 보내고, 일지를 덮고 경보만으로 다시 찾는다',40)
f.save('rev01-roadmap')

# 출발지별 타임라인(21:32:00~24, 초 단위).
f=Figure(800)
X0,PX=330,46.5
def x(t):return int(X0+t*PX)
f.label((15,5,1485,75),'web 접속 기록 63건 · 2026-11-01 21:32:00~24 (KST)',38)
f.box((15,100,295,250),'192.168.0.202\n공격자 VM',0,32)
f.box((15,300,295,600),'10.20.30.254\n브라우저',1,32)
f.box((x(1.4),100,x(9.6),250),'02초 · 25건 / 0.05초\n404 22 · 200·302 3',2,32)
f.box((x(1.4),300,x(8.6),420),'POST 로그인 ×3\n302',0,30)
f.box((x(9.6),440,x(15.2),560),'Brute GET ×3\n200',0,30)
f.box((x(16.6),300,x(21.4),420),'404 ×5\n없는·관리 경로',0,30)
f.box((x(19.0),440,x(24.4),560),'UA·메서드 403\n긴 URL 200',0,30)
f.d.line((X0,650,x(24),650),fill=base.INK,width=5)
font=ImageFont.truetype(base.FONT,30)
for t in range(0,25,4):
 f.d.line((x(t),640,x(t),660),fill=base.INK,width=5)
 s=f'{t:02d}초';w=f.d.textlength(s,font=font);f.d.text((x(t)-w/2,670),s,font=font,fill=base.INK)
f.label((15,720,1485,790),'경보 인덱스에는 이 중 30건(404·403과 긴 URL)만 있다',36)
f.save('rev01-timeline')
print('2 chapter 6 REV01 diagrams')
