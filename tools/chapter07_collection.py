"""웹 요청과 파일 변화의 수집 관계만 그린다. UI를 재현하지 않는다."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse, math
ROOT=Path(__file__).resolve().parents[1]
def build(font):
    im=Image.new('RGB',(1500,630),'#fffdf8');d=ImageDraw.Draw(im)
    ink='#202638';colors=['#e9dfd3','#dce7e4','#e1e3ef']
    def box(r,text,c=0,size=44):
        f=ImageFont.truetype(str(font),size);b=d.multiline_textbbox((0,0),text,font=f,spacing=12)
        assert b[2]-b[0]<r[2]-r[0]-25
        assert b[3]-b[1]<r[3]-r[1]-20
        d.rectangle(r,fill=colors[c],outline=ink,width=5)
        d.multiline_text(((r[0]+r[2]-b[2]+b[0])/2,(r[1]+r[3]-b[3]+b[1])/2-b[1]),text,font=f,fill=ink,spacing=12,align='center')
    def arrow(a,b):
        d.line((*a,*b),fill=ink,width=7);ang=math.atan2(b[1]-a[1],b[0]-a[0]);x,y=b
        d.polygon([(x,y),(x-22*math.cos(ang)+12*math.sin(ang),y-22*math.sin(ang)-12*math.cos(ang)),(x-22*math.cos(ang)-12*math.sin(ang),y-22*math.sin(ang)+12*math.cos(ang))],fill=ink)
    box((35,30,430,190),'웹 요청\n브라우저 · curl',0)
    box((35,250,430,410),'웹 폴더 변화\n파일 생성 · 삭제',0)
    box((530,30,965,190),'Apache · WAF\n접속 · 감사 기록',1)
    box((530,250,965,410),'FIM\n경로 · 변경 이벤트',1)
    box((1070,140,1465,330),'Wazuh\n수집 · 규칙 분석',2)
    arrow((440,110),(520,110));arrow((440,330),(520,330))
    arrow((975,110),(1060,205));arrow((975,330),(1060,270))
    box((260,490,1240,595),'Discover: 원문 · 필드 · 응답 · 시각 대조',2,43)
    arrow((1270,340),(1270,450));arrow((1270,450),(1150,480))
    out=ROOT/'assets/figures/chapter07/collection.png';im.save(out);print(out)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--font',type=Path,required=True);build(ap.parse_args().font)
