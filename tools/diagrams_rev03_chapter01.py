"""REV03 1장의 실행 관계·확인 순서 도식. UI나 인물 삽화는 생성하지 않는다."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/figures/rev03/chapter01';OUT.mkdir(parents=True,exist_ok=True)
FONT='C:/Users/Student/AppData/Local/Microsoft/Windows/Fonts/BookkGothic_Light.ttf'
INK='#202638';PAPER='#fffdf8';COLORS=['#e9dfd3','#dce7e4','#e1e3ef']
LABELS={}
class Figure:
 def __init__(self,h):self.im=Image.new('RGB',(1500,h),PAPER);self.d=ImageDraw.Draw(self.im);self.labels=[]
 def label(self,r,t,size=46):
  f=ImageFont.truetype(FONT,size);x0,y0,x1,y1=r;b=self.d.multiline_textbbox((0,0),t,font=f,spacing=14,align='center')
  assert b[2]-b[0]<x1-x0-18,(t,'width',r);assert b[3]-b[1]<y1-y0-12,(t,'height',r)
  self.d.multiline_text(((x0+x1-b[2]+b[0])/2,(y0+y1-b[3]+b[1])/2-b[1]),t,font=f,fill=INK,spacing=14,align='center');self.labels.append(t)
 def box(self,r,t,c=0,size=46):self.d.rectangle(r,fill=COLORS[c],outline=INK,width=5);self.label(r,t,size)
 def arrow(self,a,b):
  x,y=b;angle=math.atan2(y-a[1],x-a[0]);self.d.line((*a,x,y),fill=INK,width=6)
  self.d.polygon([(x,y),(x-22*math.cos(angle)+12*math.sin(angle),y-22*math.sin(angle)-12*math.cos(angle)),(x-22*math.cos(angle)-12*math.sin(angle),y-22*math.sin(angle)+12*math.cos(angle))],fill=INK)
 def save(self,n):self.im.save(OUT/(n+'.png'));LABELS[n]=self.labels

f=Figure(840)
rows=[('1.1~1.3','환경과 주소','Ubuntu·자원·주소 확인'),('1.4~1.5','코드와 실행 준비','커밋·설정·Docker 확인'),('1.6~1.7','서비스와 수집기','접속·센서·연결 확인'),('1.8','보존과 재기동','스냅샷·재기동 결과 대조')]
for i,(sec,title,out) in enumerate(rows):
 y=25+i*205;f.box((35,y,635,y+150),sec+'\n'+title,i%3,49);f.arrow((650,y+75),(755,y+75));f.box((775,y,1465,y+150),out,1,46)
 if i<3:f.arrow((335,y+160),(335,y+195))
f.save('learning-sequence')

f=Figure(640)
f.box((35,30,1465,175),'Windows PC · VMware와 브라우저',0,51)
f.box((100,235,1400,600),'',1)
f.label((110,245,1390,330),'Ubuntu VM · 독자가 설치',51)
f.box((145,365,720,550),'Docker\nkt66.sh install',0,48)
f.box((800,365,1355,550),'서비스·호스트 센서\nkt66.sh up',2,44)
f.arrow((750,185),(750,230));f.arrow((730,460),(790,460));f.save('installation')

f=Figure(620)
f.box((35,35,465,240),'에이전트\n로그 수집·전송',0,47)
f.box((535,35,965,240),'매니저 분석\nFilebeat 전송',1,47)
f.box((1035,35,1465,240),'인덱서\n저장·검색',2,47)
f.arrow((475,135),(525,135));f.arrow((975,135),(1025,135))
f.box((35,365,465,560),'Windows\n브라우저',0,48)
f.box((535,365,965,560),'대시보드\n검색 조건·결과',1,47)
f.arrow((475,435),(525,435));f.arrow((525,490),(475,490))
f.arrow((975,425),(1250,425));f.arrow((1250,425),(1250,250))
f.arrow((1340,250),(1340,505));f.arrow((1340,505),(975,505))
f.label((1000,285,1230,385),'검색',40);f.label((1110,530,1450,605),'결과 반환',40);f.save('wazuh-flow')

f=Figure(460)
f.box((35,30,465,260),'Windows PC\n브라우저',0,49)
f.box((535,30,965,260),'kt66 VM\n192.168.0.107',1,47)
f.box((1035,30,1465,260),'공격자 VM\n192.168.0.108',2,47)
f.arrow((475,145),(525,145));f.arrow((1025,145),(975,145))
f.label((35,285,1465,365),'접속 대상: kt66 VM · 공격자 VM은 뒤의 공격 실습에 사용',42)
f.label((35,365,1465,445),'두 VM: Bridged · Windows와 같은 192.168.0.0/24 망',46);f.save('environment')

f=Figure(460)
f.box((35,30,465,245),'.env.example\n배포용 예시',0,48)
f.box((535,30,965,245),'복사·편집\n.env',1,48)
f.box((1035,30,1465,245),'install\n주소·선택 저장',2,47)
f.arrow((475,135),(525,135));f.arrow((975,135),(1025,135))
f.box((35,315,1465,425),'up: 저장된 .env를 읽어 서비스 실행',1,49);f.arrow((1250,255),(1250,305));f.save('env-flow')

f=Figure(480)
f.box((35,30,1465,165),'https://192.168.0.107:5601/',0,61)
f.label((35,180,1465,265),'HTTPS: 통신 방식    192.168.0.107: VM 주소    5601: 포트',42)
f.box((35,310,715,445),'HTTP · 80\nkt66 웹',1,48)
f.box((785,310,1465,445),'HTTPS · 5601\nWazuh',2,48);f.save('ports')

f=Figure(560)
f.box((35,35,570,205),'컨테이너 실행',1,49)
f.box((930,35,1465,205),'컨테이너 제거',2,49)
f.arrow((580,95),(920,95));f.label((580,0,920,80),'down',45)
f.arrow((920,155),(580,155));f.label((580,170,920,255),'up · 재생성',43)
f.box((35,300,1465,405),'Wazuh 로그·인덱서 데이터 볼륨 유지',0,48)
f.label((35,430,1465,540),'컨테이너 내부에만 만든 파일은 제거 전에 별도 보관',44);f.save('lifecycle')

f=Figure(650)
f.box((35,35,1465,145),'사례 번호 02-02-01 · 2.2의 첫 실행',0,49)
f.box((35,225,700,460),'실행 일지\n시스템·시각·입력\n응답과 실제 상태',1,47)
f.box((800,225,1465,460),'조사 기록\n원문·필드·식별자\n판단과 추가 확인',2,47)
f.arrow((365,155),(365,215));f.arrow((1130,155),(1130,215))
f.arrow((365,470),(365,550));f.arrow((1130,470),(1130,550))
f.label((35,550,1465,635),'같은 사례의 입력·응답과 수집된 근거를 대조',49);f.save('case-records')
(OUT/'labels.json').write_text(json.dumps(LABELS,ensure_ascii=False,indent=2)+'\n','utf8')
print('8 diagrams generated')
