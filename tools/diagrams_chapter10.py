"""10장 관계·흐름 도식. 실제 UI나 실행 결과를 합성하지 않는다."""
import math,os
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/figures/chapter10';OUT.mkdir(parents=True,exist_ok=True)
FONT=os.environ.get('BOOK_DIAGRAM_FONT',str(Path(os.environ.get('LOCALAPPDATA',''))/'Microsoft/Windows/Fonts/BookkGothic_Light.ttf'))
INK='#202638';PAPER='#fffdf8';PAL=['#e9dfd3','#dce7e4','#e1e3ef']
class Figure:
 def __init__(self,h):self.im=Image.new('RGB',(1500,h),PAPER);self.d=ImageDraw.Draw(self.im)
 def box(self,r,t,c=0,size=46):
  self.d.rectangle(r,fill=PAL[c],outline=INK,width=5)
  font=ImageFont.truetype(FONT,size);b=self.d.multiline_textbbox((0,0),t,font=font,spacing=12,align='center');x,y,z,w=r
  assert b[2]-b[0]<z-x-30,(t,'width');assert b[3]-b[1]<w-y-20,(t,'height')
  self.d.multiline_text(((x+z-b[2]+b[0])/2,(y+w-b[3]+b[1])/2-b[1]),t,font=font,spacing=12,align='center',fill=INK)
 def arrow(self,a,b):
  x,y=b;t=math.atan2(y-a[1],x-a[0]);self.d.line((*a,x,y),fill=INK,width=7)
  self.d.polygon([(x,y),(x-24*math.cos(t)+13*math.sin(t),y-24*math.sin(t)-13*math.cos(t)),(x-24*math.cos(t)-13*math.sin(t),y-24*math.sin(t)+13*math.cos(t))],fill=INK)
 def save(self,n):self.im.save(OUT/(n+'.png'))

f=Figure(700)
for x,t,c in [(35,'실습 29\n새 포트 · 프로세스',0),(535,'실습 30\n스캔 · DROP',1),(1035,'실습 62\nSQL · 공개 키',2)]:f.box((x,35,x+430,270),t,c,43)
f.arrow((475,150),(525,150));f.arrow((975,150),(1025,150))
f.box((35,385,1465,650),'원문 · Wazuh 경보 · 현재 상태 대조\n증거 보존 → 대응 판단 → 원상복구',0,48)
f.arrow((1250,280),(1250,375));f.save('roadmap')
f=Figure(780)
for y,t,u,c in [(35,'호스트 소켓','ss · netstat\n주소 / 포트 / 프로세스',0),(280,'경계의 패킷','iptables · kern.log\nSRC / DST / SPT / DPT',1),(525,'현재 상태 조회','osquery SQL\n선택한 열 / 조회 시각',2)]:
 f.box((35,y,610,y+200),t,c,49);f.box((775,y,1465,y+200),u,c,45);f.arrow((620,y+100),(765,y+100))
f.save('layers')
f=Figure(900)
f.box((35,35,1465,195),'공격자 Nmap · TCP 연결 시도',0,49)
for x,t,c in [(35,'SYN/ACK 응답\nopen',0),(535,'RST 응답\nclosed',1),(1035,'무응답 등\nfiltered',2)]:
 f.box((x,320,x+430,535),t,c,44);f.arrow((x+215,205),(x+215,310))
f.box((535,650,1465,850),'이 실습: LOG 후 DROP\nkern.log → Wazuh 4151',2,47)
f.arrow((1250,545),(1250,640));f.save('scan')
f=Figure(1000)
f.box((35,35,675,245),'osqueryi · 직접 SQL\n현재 상태 질문',0,46);f.box((825,35,1465,245),'터미널 결과\nss · 파일과 대조',0,46);f.arrow((685,140),(815,140))
f.box((35,375,675,585),'osqueryd · 예약 SQL\n이전 결과와 차이',1,46);f.box((825,375,1465,585),'결과 로그\nadded / removed',1,46);f.arrow((685,480),(815,480))
f.box((35,730,675,940),'Discover · 저장 기록\nDQL로 검색',2,46);f.box((825,730,1465,940),'Wazuh osquery 모듈\nJSON 수집 · 규칙',2,46)
f.arrow((1145,595),(1145,720));f.arrow((815,835),(685,835));f.save('osquery')
f=Figure(820)
for x,y,t,c in [(35,35,'증거 보존\n원문 · 시각 · 식별자',0),(825,35,'현재 상태 대조\nss · SQL · 키 지문',1),(825,475,'판단과 대응\n승인 여부 · 접속 경로',2),(35,475,'원상복구 확인\n현재 상태 + 제거 기록',0)]:f.box((x,y,x+640,y+275),t,c,45)
f.arrow((685,170),(815,170));f.arrow((1145,320),(1145,465));f.arrow((815,610),(685,610));f.save('decision')
print('5 chapter10 diagrams')
