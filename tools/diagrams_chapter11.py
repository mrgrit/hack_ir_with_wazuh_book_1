"""11장의 관계·절차 도식. UI 합성 없음."""
import os,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/figures/chapter11';OUT.mkdir(parents=True,exist_ok=True)
FONT=str(Path(os.environ['LOCALAPPDATA'])/'Microsoft/Windows/Fonts/BookkGothic_Light.ttf')
class F:
 def __init__(self,h):self.im=Image.new('RGB',(1500,h),'#fffdf8');self.d=ImageDraw.Draw(self.im)
 def box(self,r,t,c=0,s=46):
  self.d.rectangle(r,fill=['#e9dfd3','#dce7e4','#e1e3ef'][c],outline='#202638',width=5)
  font=ImageFont.truetype(FONT,s);b=self.d.multiline_textbbox((0,0),t,font=font,spacing=14,align='center');x,y,z,w=r
  assert b[2]-b[0]<z-x-30,(t,'width');assert b[3]-b[1]<w-y-20,(t,'height')
  self.d.multiline_text(((x+z-b[2]+b[0])/2,(y+w-b[3]+b[1])/2-b[1]),t,font=font,spacing=14,align='center',fill='#202638')
 def arrow(self,a,b):
  x,y=b;t=math.atan2(y-a[1],x-a[0]);self.d.line((*a,x,y),fill='#202638',width=7);self.d.polygon([(x,y),(x-24*math.cos(t)+13*math.sin(t),y-24*math.sin(t)-13*math.cos(t)),(x-24*math.cos(t)-13*math.sin(t),y-24*math.sin(t)+13*math.cos(t))],fill='#202638')
 def save(self,n):self.im.save(OUT/(n+'.png'))
f=F(810)
for x,y,t,c in [(35,35,'범위 고정\n대상 · 기간 · 수집원',0),(825,35,'기록 연결\n시각 · 계정 · 세션',1),(825,460,'판단과 대응\n사실 · 가설 · 영향',2),(35,460,'복구와 인계\n검증 · 남은 과제',0)]:f.box((x,y,x+640,y+280),t,c)
f.arrow((685,175),(815,175));f.arrow((1145,325),(1145,450));f.arrow((815,600),(685,600));f.save('roadmap')
f=F(690)
for x,t,c in [(35,'프로그램 원문\n발생 시각',0),(535,'Wazuh 경보\ntimestamp',1),(1035,'Discover 표시\n설정한 시간대',2)]:f.box((x,35,x+430,280),t,c,43)
f.arrow((475,155),(525,155));f.arrow((975,155),(1025,155));f.box((35,425,1465,635),'원문 값은 보존 · 표시 시간대는 통일\n지연과 시계 오차는 별도로 기록',0,49);f.save('time')
f=F(880)
for i,t in enumerate(['시간대 · 시작과 끝','패턴 · 필터 · 실제 필드','원본 로그 · 센서 · 수신','인덱싱 · 회전 · 보존 기간']):
 y=30+i*215;f.box((190,y,1310,y+150),t,i%3,49)
 if i<3:f.arrow((750,y+160),(750,y+205))
f.save('empty')
f=F(920)
for y,t,u,c in [(30,'실행 기록','호스트 · PID · 사용자 · 명령',0),(335,'현재 소켓','주소 · 포트 · PID · 조회 시각',1),(640,'예약 결과','선택한 열 · added / removed',2)]:
 f.box((35,y,480,y+235),t,c,47);f.box((635,y,1465,y+235),u,c,44);f.arrow((490,y+118),(625,y+118))
f.save('layers')
f=F(840)
f.box((35,30,1465,200),'현재 영향 · 진행 중인 행위 · 업무와 관리 경로',0,48)
f.box((35,350,700,590),'증거 확보\n원문 · 현재 상태 · 해시',1,44);f.box((800,350,1465,590),'피해 감소\n접근 제한 · 격리 · 중지',2,44)
f.arrow((367,210),(367,340));f.arrow((1132,210),(1132,340))
f.box((35,690,1465,805),'결정 근거 · 실행 결과 · 복구 조건 기록',0,48);f.arrow((367,600),(367,680));f.arrow((1132,600),(1132,680));f.save('response')
print('5 diagrams')
