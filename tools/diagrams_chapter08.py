"""8장 관계·절차 도식. UI와 실제 결과를 그리지 않는다."""
import math,os
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/figures/chapter08';OUT.mkdir(parents=True,exist_ok=True)
FONT=os.environ.get('BOOK_DIAGRAM_FONT',str(Path(os.environ.get('LOCALAPPDATA',''))/'Microsoft/Windows/Fonts/BookkGothic_Light.ttf'))
INK='#202638';PAPER='#fffdf8';PAL=['#e9dfd3','#dce7e4','#e1e3ef']
class Figure:
 def __init__(self,h):self.im=Image.new('RGB',(1500,h),PAPER);self.d=ImageDraw.Draw(self.im)
 def box(self,r,t,c=0,size=46):
  self.d.rectangle(r,fill=PAL[c],outline=INK,width=5)
  font=ImageFont.truetype(FONT,size);b=self.d.multiline_textbbox((0,0),t,font=font,spacing=12,align='center')
  x,y,z,w=r;assert b[2]-b[0]<z-x-30,(t,'width');assert b[3]-b[1]<w-y-20,(t,'height')
  self.d.multiline_text(((x+z-b[2]+b[0])/2,(y+w-b[3]+b[1])/2-b[1]),t,font=font,spacing=12,align='center',fill=INK)
 def arrow(self,a,b):
  x,y=b;t=math.atan2(y-a[1],x-a[0]);self.d.line((*a,x,y),fill=INK,width=7)
  self.d.polygon([(x,y),(x-24*math.cos(t)+13*math.sin(t),y-24*math.sin(t)-13*math.cos(t)),(x-24*math.cos(t)-13*math.sin(t),y-24*math.sin(t)+13*math.cos(t))],fill=INK)
 def save(self,n):self.im.save(OUT/(n+'.png'))

f=Figure(575)
for x,y,t,c in [(35,35,'16 암호 대입\n실패 기록',0),(535,35,'17 계정 탐색\n잘못된 이름',1),(1035,35,'18 인증 성공\n세션 확인',2),(1035,330,'19 root 접속\n정책 · 인증',0),(535,330,'20 sudo 실행\n사용자 · 명령',1),(35,330,'21 계정 변경\n생성 · 삭제',2)]:f.box((x,y,x+430,y+195),t,c)
for a,b in [((475,132),(525,132)),((975,132),(1025,132)),((1250,240),(1250,320)),((1025,428),(975,428)),((525,428),(475,428))]:f.arrow(a,b)
f.save('roadmap')
f=Figure(650)
for x,y,t,c in [(35,35,'공격자 VM\n.108 · SSH',0),(535,35,'kt66 VM\n.107:2204',1),(1035,35,'bastion:22\nsshd · 인증',2),(1035,365,'auth.log\n에이전트 수집',2),(535,365,'Wazuh\n분석 · 저장',1),(35,365,'Windows\nDiscover 검색',0)]:f.box((x,y,x+430,y+210),t,c)
for a,b in [((475,140),(525,140)),((975,140),(1025,140)),((1250,255),(1250,355)),((1025,470),(975,470)),((525,470),(475,470))]:f.arrow(a,b)
f.save('collection')
f=Figure(505)
f.box((35,35,680,220),'개별 실패 원문\n계정 · 출발지 · 시각',0)
f.box((820,35,1465,220),'반복 요약 원문\nmessage repeated',1)
f.arrow((350,230),(550,310));f.arrow((1150,230),(950,310))
f.box((150,325,1350,465),'추출된 필드와 이전 일치 이력\n동일 출발지 · 시간 조건으로 연관 판단',2,46);f.save('correlation')
f=Figure(590)
for x,t,c in [(35,'실패\n계정 · 출발지',0),(535,'성공\n방식 · 세션',1),(1035,'후속 행위\nsudo · 계정 변경',2)]:f.box((x,35,x+430,235),t,c,43)
f.arrow((475,135),(525,135));f.arrow((975,135),(1025,135));f.arrow((750,245),(750,330))
f.box((120,345,1380,535),'사용자 확인 · 승인된 작업과 대조\n침해 판단과 영향 범위 기록',0,50);f.save('timeline')
f=Figure(600)
for x,t,c in [(35,'초기 상태\nroot L\n로그인 금지',0),(535,'임시 실습\n암호 설정\n로그인 허용',1),(1035,'원상복구\n백업 복원\n새 접속 확인',2)]:f.box((x,35,x+430,285),t,c,45)
f.arrow((475,160),(525,160));f.arrow((975,160),(1025,160))
f.box((35,385,1465,550),'설정 파일과 암호 상태를 함께 보존\n복구 확인 전에는 다른 계정 변경을 진행하지 않음',0,46);f.save('root-state')
f=Figure(550)
for x,t,c in [(35,'SSH 인증\nccc',0),(535,'sudo 정책\n허용 범위 확인',1),(1035,'명령 실행\nroot 권한',2)]:f.box((x,35,x+430,235),t,c,45)
f.arrow((475,135),(525,135));f.arrow((975,135),(1025,135))
f.box((35,335,1465,495),'sudo 기록: srcuser=ccc · dstuser=root\n명령의 결과는 출력 · 종료 코드 · 시스템 상태로 확인',0,44);f.save('sudo')
f=Figure(550)
for x,t,c in [(35,'계정 생성\n이름 · UID · 홈',0),(535,'권한 변경\n그룹 · sudoers',1),(1035,'재접속 조건\n암호 · 키 · 정책',2)]:f.box((x,35,x+430,235),t,c,43)
f.arrow((475,135),(525,135));f.arrow((975,135),(1025,135))
f.box((35,335,1465,495),'삭제 뒤: 계정 · 그룹 · 홈의 부재 확인\n다른 경로의 파일 · 세션 · 예약 작업은 별도 조사',0,45);f.save('account')
print('7 chapter08 diagrams')
