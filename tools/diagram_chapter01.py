"""저자용 구성 도식. 실제 화면을 흉내 내지 않는다."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/figures/chapter01/environment.png'
im = Image.new('RGB',(1500,1150),'#fffdf8')
d = ImageDraw.Draw(im)
font = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
ink = '#202638'

def label(box, text, size=49):
    f=ImageFont.truetype(font,size)
    x0,y0,x1,y1=box
    bb=d.multiline_textbbox((0,0),text,font=f,spacing=14,align='center')
    assert bb[2]-bb[0] < x1-x0-36, text
    assert bb[3]-bb[1] < y1-y0-20, text
    d.multiline_text(((x0+x1-bb[2]+bb[0])/2,(y0+y1-bb[3]+bb[1])/2-bb[1]),text,font=f,fill=ink,spacing=14,align='center')

def box(rect,text,fill='#dce7e4',size=49):
    d.rectangle(rect,fill=fill,outline=ink,width=5)
    label(rect,text,size)

box((35,25,1465,180),'Windows PC  ·  VMware Workstation', '#e9dfd3',54)
box((70,220,600,370),'브라우저', '#ffffff',56)
box((650,220,1430,370),'Ubuntu 가상머신의 주소로 접속', '#fffdf8',43)
d.line((335,375,335,470),fill=ink,width=7)
d.polygon([(320,450),(350,450),(335,477)],fill=ink)
d.rectangle((35,485,1465,1115),fill='#e1e3ef',outline=ink,width=5)
label((60,500,1440,610),'Ubuntu 22.04 LTS 가상머신',57)
box((80,640,610,815),'kt66 웹 서비스\nHTTP · 80', '#faf4e8')
box((850,640,1420,815),'Wazuh 대시보드\nHTTPS · 5601', '#faf4e8')
label((70,830,1430,925),'Docker가 각 서비스를 컨테이너로 실행한다.',46)
box((80,950,1420,1075),'Ubuntu 호스트 센서 → Wazuh 수집·분석', '#dce7e4',49)
OUT.parent.mkdir(parents=True,exist_ok=True)
im.save(OUT)
print(OUT)
