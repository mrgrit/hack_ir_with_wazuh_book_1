"""REV01 4장 도식: 학습 순서, 문장 차이에 따른 디코더·필드·규칙 차이."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import diagrams_chapter01 as base
base.OUT=base.ROOT/'assets/figures/chapter04';base.OUT.mkdir(parents=True,exist_ok=True)
Figure=base.Figure

# 학습 순서: 수집 → 분석 → 규칙 → 마무리.
f=Figure(930)
cols=[('수집',['4.1\n수집 경로','4.2\n수집 설정','4.3\n문구 남기기','4.4\n아카이브 확인']),('분석',['4.5\nRuleset Test','4.6\n문장 비교']),
      ('규칙',['4.7\n규칙 작성','4.8\n검사·시험','4.9\n적용·새 경보']),('마무리',['4.10\n원상복구','4.11\n멈춘 단계 찾기'])]
W,G,X0=318,74,15
for col,(label,items) in enumerate(cols):
 x=X0+col*(W+G)
 f.label((x,15,x+W,95),label,50)
 for row,title in enumerate(items):
  y=110+row*180;f.box((x,y,x+W,y+160),title,col%3,36)
 if col<3:f.arrow((x+W+8,280),(x+W+G-8,280))
f.label((15,830,1485,915),'실행 위치: kt66 VM 터미널 · bastion·siem 컨테이너 · Windows 브라우저',40)
f.save('rev01-roadmap')

# 같은 sshd 로그라도 문장이 다르면 다른 하위 디코더·필드·규칙이 적용된다.
f=Figure(700)
f.label((35,10,1465,80),'같은 부모 디코더 sshd · 0310-ssh_decoders.xml',40)
rows=[('Failed password for\ninvalid user book03_probe','ssh-invfailed','srcuser · srcip','5710'),
      ('Failed password for\nbook03_probe','ssh-failed','dstuser · srcip\n· srcport','5760')]
for i,(msg,dec,fields,rule) in enumerate(rows):
 y=100+i*300
 f.box((15,y,520,y+230),msg,0,34)
 f.box((585,y,925,y+230),'하위 디코더\n'+dec,1,34)
 f.box((990,y,1285,y+230),fields,2,34)
 f.box((1345,y,1485,y+230),rule,0,34)
 f.arrow((527,y+115),(577,y+115));f.arrow((932,y+115),(982,y+115));f.arrow((1292,y+115),(1337,y+115))
f.save('rev01-variant')
print('2 chapter 4 REV01 diagrams')
