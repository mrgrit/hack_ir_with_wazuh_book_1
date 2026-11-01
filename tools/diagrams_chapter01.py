"""절차·설정·기록 흐름을 설명하는 저자용 도식."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/figures/chapter01';OUT.mkdir(parents=True,exist_ok=True)
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
INK='#202638';PAPER='#fffdf8';PALETTE=['#e9dfd3','#dce7e4','#e1e3ef']
class Figure:
 def __init__(self,h):
  self.im=Image.new('RGB',(1500,h),PAPER);self.d=ImageDraw.Draw(self.im)
 def label(self,r,t,size=48):
  f=ImageFont.truetype(FONT,size);x0,y0,x1,y1=r;b=self.d.multiline_textbbox((0,0),t,font=f,spacing=12,align='center')
  assert b[2]-b[0]<x1-x0-24,(t,'width');assert b[3]-b[1]<y1-y0-16,(t,'height')
  self.d.multiline_text(((x0+x1-b[2]+b[0])/2,(y0+y1-b[3]+b[1])/2-b[1]),t,font=f,fill=INK,spacing=12,align='center')
 def box(self,r,t,c=0,size=48):
  self.d.rectangle(r,fill=PALETTE[c],outline=INK,width=5);self.label(r,t,size)
 def arrow(self,start,end):
  import math
  x,y=end;a=math.atan2(y-start[1],x-start[0]);self.d.line((*start,x,y),fill=INK,width=7)
  self.d.polygon([(x,y),(x-24*math.cos(a)+13*math.sin(a),y-24*math.sin(a)-13*math.cos(a)),(x-24*math.cos(a)-13*math.sin(a),y-24*math.sin(a)+13*math.cos(a))],fill=INK)
 def save(self,name):self.im.save(OUT/(name+'.png'))
# Installation responsibilities and order.
f=Figure(360)
for i,(title,desc) in enumerate([('VM·Ubuntu','독자가 설치'),('Docker','kt66 install'),('서비스·센서','kt66 up')]):
 x=35+i*500;f.box((x,35,x+430,235),title+'\n'+desc,i)
 if i<2:f.arrow((x+435,135),(x+490,135))
f.label((35,250,1465,345),'설치 후: 웹 접속 → Wazuh 로그인 → 에이전트 연결 확인',46);f.save('installation')
# Wazuh data flow. Each arrow has one clear direction.
f=Figure(570)
for x,y,title,c in [(35,35,'Ubuntu 기록',0),(535,35,'Agent\n수집·전송',1),(1035,35,'Manager\n분석',2),(1035,335,'Indexer\n저장·검색',2),(535,335,'Dashboard\n검색 화면',1),(35,335,'Windows\n브라우저',0)]:f.box((x,y,x+430,y+195),title,c,48)
f.arrow((470,130),(525,130));f.arrow((970,130),(1025,130));f.arrow((1250,240),(1250,325));f.arrow((1025,430),(970,430));f.arrow((525,430),(470,430));f.save('wazuh-flow')
# Config source / user edits / application reads.
f=Figure(375)
f.box((35,35,465,195),'.env.example\n배포용 예시',0)
f.box((535,35,965,195),'cp → nano\n복사 후 편집',1)
f.box((1035,35,1465,195),'.env\n실습 설정',2)
f.arrow((470,115),(525,115));f.arrow((970,115),(1025,115))
f.label((35,220,1465,350),'install: 주소·선택 저장     up: 설정을 읽고 서비스 실행',46);f.save('env-flow')
# Address and service selection.
f=Figure(500)
f.box((35,30,1465,155),'https://192.168.0.189:5601/',0,64)
f.label((35,170,1465,270),'HTTPS: 통신 방식    192.168.0.189: VM 주소    5601: 포트',43)
f.box((35,320,670,460),'HTTP · 80 → kt66 웹',1,52)
f.box((775,320,1465,460),'HTTPS · 5601 → Wazuh',2,49);f.save('ports')
# Down/up leave data volumes intact.
f=Figure(330)
f.box((35,35,510,180),'컨테이너 실행 중',1)
f.box((990,35,1465,180),'컨테이너 제거',2)
f.arrow((520,85),(980,85));f.label((525,5,975,75),'down',45)
f.arrow((980,155),(520,155));f.label((525,160,975,225),'up · 다시 생성',43)
f.box((35,240,1465,315),'데이터 볼륨은 유지',0,45);f.save('lifecycle')
# Troubleshooting sequence.
f=Figure(360)
for i,t in enumerate(['주소·브리지','컨테이너 상태','오류 로그']):
 x=35+i*500;f.box((x,35,x+430,185),t,i,49)
 if i<2:f.arrow((x+435,110),(x+490,110))
f.label((35,220,1465,330),'설정 수정 → kt66 기동 → 같은 주소로 다시 접속',48);f.save('troubleshooting')
print('6 explanatory diagrams')
