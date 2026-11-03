"""REV02의 구성·조사 기록 도식만 생성한다. 실제 화면과 삽화는 수정하지 않는다."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/figures/rev02'
FONT='C:/Users/Student/AppData/Local/Microsoft/Windows/Fonts/BookkGothic_Light.ttf'
INK='#202638'; COLORS=['#e9dfd3','#dce7e4','#e1e3ef']
class Figure:
    def __init__(self,h):
        self.im=Image.new('RGB',(1500,h),'#fffdf8');self.d=ImageDraw.Draw(self.im)
    def text(self,rect,text,size=42):
        x0,y0,x1,y1=rect;f=ImageFont.truetype(FONT,size)
        a,b,c,d=self.d.multiline_textbbox((0,0),text,font=f,spacing=15,align='center')
        assert c-a<x1-x0-20 and d-b<y1-y0-12,(text,rect)
        self.d.multiline_text(((x0+x1-c-a)/2,(y0+y1-d-b)/2),text,font=f,spacing=15,align='center',fill=INK)
    def box(self,r,text,c=0,size=42):
        assert r[0]>=0 and r[2]<1500
        self.d.rectangle(r,fill=COLORS[c],outline=INK,width=5);self.text(r,text,size)
    def arrow(self,start,end):
        x,y=end;ang=math.atan2(y-start[1],x-start[0]);self.d.line((*start,x,y),fill=INK,width=7)
        self.d.polygon([(x,y),(x-24*math.cos(ang)+13*math.sin(ang),y-24*math.sin(ang)-13*math.cos(ang)),(x-24*math.cos(ang)-13*math.sin(ang),y-24*math.sin(ang)+13*math.cos(ang))],fill=INK)
    def save(self,name):OUT.mkdir(parents=True,exist_ok=True);self.im.save(OUT/(name+'.png'))

def main():
    f=Figure(760)
    groups=[('이해',['1.1 구성 이해','1.2 실습망']),('준비',['1.3 VM·Ubuntu','1.4 코드·설정','1.5 Docker·커널']),('확인',['1.6 기동·접속','1.7 수집기 연결']),('기준 상태',['1.8 스냅샷·기록','1.9 공격자 VM'])]
    for i,(title,items) in enumerate(groups):
        x=30+i*375
        f.text((x,15,x+315,95),title,46)
        for j,item in enumerate(items):f.box((x,115+j*155,x+315,245+j*155),item,i%3,35)
        if i<3:f.arrow((x+322,280),(x+365,280))
    f.text((30,620,1470,735),'상세 설치는 부록 A.12~A.15\n설치된 VM은 1.6부터 확인한다.',42)
    f.save('chapter01-path')
    for chapter,labels in {
        8:['8.2 암호 대입\n실패 기록','8.3 계정 탐색\n잘못된 이름','8.4 인증 성공\n세션 확인','8.5 root 접속\n정책·인증','8.6 sudo 실행\n사용자·명령','8.7 계정 변경\n생성·삭제'],
        9:['9.2 권한 파일\nsudoers','9.3 공개 키\n재접속 조건','9.4 cron\n예약·실행','9.5·9.6 실행\n연결·다운로드','9.7 실행 파일\n내용 변경','9.8 로그\n삭제·비우기'],
    }.items():
        f=Figure(575)
        coords=[(35,35),(535,35),(1035,35),(1035,330),(535,330),(35,330)]
        for i,((x,y),label) in enumerate(zip(coords,labels)):f.box((x,y,x+430,y+195),label,i%3,42)
        for a,b in [((475,132),(525,132)),((975,132),(1025,132)),((1250,240),(1250,320)),((1025,428),(975,428)),((525,428),(475,428))]:f.arrow(a,b)
        f.save(f'chapter{chapter:02}-path')
    f=Figure(700)
    for i,label in enumerate(['10.3 포트\n리스너·프로세스','10.4·10.5 탐색\n스캔·DROP','10.6·10.7 조회\nSQL·공개 키']):
        x=35+i*500;f.box((x,35,x+430,270),label,i,42)
        if i<2:f.arrow((x+440,150),(x+490,150))
    f.box((35,385,1465,650),'원문·Wazuh 경보·현재 상태를 대조한다.\n10.8 원상복구 · 10.10 조사 결과',0,46)
    f.arrow((1250,280),(1250,375));f.save('chapter10-path')
if __name__=='__main__':main()
