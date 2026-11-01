"""저자용 네트워크 구성도. 두 VM의 브리지 연결과 접속 포트."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/figures/chapter01/environment.png'
im=Image.new('RGB',(1500,1250),'#fffdf8');d=ImageDraw.Draw(im)
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';INK='#202638'
def label(rect,text,size=48):
    f=ImageFont.truetype(FONT,size);x0,y0,x1,y1=rect
    bb=d.multiline_textbbox((0,0),text,font=f,spacing=12,align='center')
    assert bb[2]-bb[0]<x1-x0-24,text
    assert bb[3]-bb[1]<y1-y0-14,text
    d.multiline_text(((x0+x1-bb[2]+bb[0])/2,(y0+y1-bb[3]+bb[1])/2-bb[1]),text,font=f,fill=INK,spacing=12,align='center')
def box(rect,text,fill='#e1e3ef',size=48):
    d.rectangle(rect,fill=fill,outline=INK,width=5);label(rect,text,size)
def arrow(x0,y0,x1,y1):
    d.line((x0,y0,x1,y1),fill=INK,width=7)
    d.polygon([(x1-15,y1-22),(x1+15,y1-22),(x1,y1)],fill=INK)
d.rectangle((25,25,1475,1000),outline=INK,width=5)
label((45,35,1455,135),'Windows PC · VMware Workstation',54)
box((70,155,1430,275),'브라우저 → 웹 HTTP :80 / Wazuh HTTPS :5601','#e9dfd3',43)
box((70,355,720,800),'kt66 VM\nUbuntu 22.04\n192.168.0.189\n\n웹 서비스 · Wazuh\n호스트 센서',size=51)
box((790,355,1430,800),'attacker VM\nUbuntu 22.04\nLive Server\n192.168.0.202\n\n공격 도구',fill='#dce7e4',size=51)
label((90,810,700,890),'Bridged',48);label((810,810,1410,890),'Bridged',48)
d.line((395,890,395,970,1110,970,1110,890),fill=INK,width=7)
d.line((750,970,750,1040),fill=INK,width=7)
box((130,1040,1370,1160),'실습망 192.168.0.0/24 · DHCP','#e9dfd3',50)
label((70,285,1430,345),'공격 요청: 192.168.0.202 → 192.168.0.189',43)
OUT.parent.mkdir(parents=True,exist_ok=True);im.save(OUT);print(OUT)
