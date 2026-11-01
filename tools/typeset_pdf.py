"""Offline print fallback using system Cairo/Pango/librsvg; no browser or lab access."""
import ctypes as C
from pathlib import Path
from html.parser import HTMLParser
import json
import xml.etree.ElementTree as ET
from PIL import Image
R=Path(__file__).resolve().parents[1]
D=C.c_double; I=C.c_int; P=C.c_void_p; S=C.c_char_p
c=C.CDLL('libcairo.so.2'); p=C.CDLL('libpango-1.0.so.0'); pc=C.CDLL('libpangocairo-1.0.so.0'); g=C.CDLL('libgobject-2.0.so.0'); rv=C.CDLL('librsvg-2.so.2')
def bind(lib,n,args,ret=None):
 f=getattr(lib,n);f.argtypes=args;f.restype=ret;return f
pdf=bind(c,'cairo_pdf_surface_create',[S,D,D],P);create=bind(c,'cairo_create',[P],P)
move=bind(c,'cairo_move_to',[P,D,D]); rgb=bind(c,'cairo_set_source_rgb',[P,D,D,D]);rect=bind(c,'cairo_rectangle',[P,D,D,D,D]);fill=bind(c,'cairo_fill',[P]);save=bind(c,'cairo_save',[P]);restore=bind(c,'cairo_restore',[P]);scale=bind(c,'cairo_scale',[P,D,D]);translate=bind(c,'cairo_translate',[P,D,D]);clip=bind(c,'cairo_clip',[P]);paint=bind(c,'cairo_paint',[P]);showpage=bind(c,'cairo_show_page',[P]);finish=bind(c,'cairo_surface_finish',[P]);destroy=bind(c,'cairo_surface_destroy',[P]);status=bind(c,'cairo_surface_status',[P],I)
png=bind(c,'cairo_image_surface_create_from_png',[S],P);source=bind(c,'cairo_set_source_surface',[P,P,D,D])
newlayout=bind(pc,'pango_cairo_create_layout',[P],P);show=bind(pc,'pango_cairo_show_layout',[P,P]);settext=bind(p,'pango_layout_set_text',[P,S,I]);setwidth=bind(p,'pango_layout_set_width',[P,I]);setwrap=bind(p,'pango_layout_set_wrap',[P,I]);setspace=bind(p,'pango_layout_set_spacing',[P,I]);getsize=bind(p,'pango_layout_get_size',[P,C.POINTER(I),C.POINTER(I)]);fontnew=bind(p,'pango_font_description_from_string',[S],P);setfont=bind(p,'pango_layout_set_font_description',[P,P]);fontfree=bind(p,'pango_font_description_free',[P]);unref=bind(g,'g_object_unref',[P]);resolution=bind(pc,'pango_cairo_context_set_resolution',[P,D]);getctx=bind(p,'pango_layout_get_context',[P],P)
rnew=bind(rv,'rsvg_handle_new_from_file',[S,P],P);rrender=bind(rv,'rsvg_handle_render_cairo',[P,P],I)
class N:
 def __init__(self,tag='',attrs=()):self.tag=tag;self.attrs=dict(attrs);self.children=[]
 def text(self):return ''.join(x.text() if isinstance(x,N) else x for x in self.children)
 def find(self,tag):
  if self.tag==tag:return self
  for ch in self.children:
   if isinstance(ch,N):
    found=ch.find(tag)
    if found:return found
class Parser(HTMLParser):
 def __init__(self,s):
  super().__init__();self.root=N('root');self.stack=[self.root];self.feed(s)
 def handle_starttag(self,t,a):
  n=N(t,a);self.stack[-1].children.append(n)
  if t=='br':n.children.append('\n')
  if t not in ['img','br','hr','meta']:self.stack.append(n)
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==t:self.stack=self.stack[:i];break
 def handle_data(self,s):self.stack[-1].children.append(s)
mm=72/25.4;W=182*mm;H=257*mm;M=14*mm;CW=W-2*M;BOTTOM=H-17*mm
surface=pdf(str(R/'build/volume01-sample.pdf').encode(),W,H);cr=create(surface)
records=[];num=0;y=0;section='';title=''
def color(hex):
 rgb(cr,*[int(hex[i:i+2],16)/255 for i in (1,3,5)])
def box(x,y,w,h,col):color(col);rect(cr,x,y,w,h);fill(cr)
def text(s,x,yy,w,size=10.5,col='#263449',mono=False,bold=False,draw=True):
 layout=newlayout(cr);resolution(getctx(layout),72)
 desc=fontnew((('DejaVu Sans Mono, Noto Sans CJK KR' if mono else 'Noto Sans CJK KR')+(' Bold' if bold else '')+f' {size}').encode())
 setfont(layout,desc);fontfree(desc);setwidth(layout,int(w*1024));setwrap(layout,2);setspace(layout,int(size*.35*1024));settext(layout,s.encode(),-1)
 ww=I();hh=I();getsize(layout,C.byref(ww),C.byref(hh));h=hh.value/1024
 if draw:color(col);move(cr,x,yy);show(cr,layout)
 unref(layout);return h

def start(cont=False):
 global y,num
 num+=1;box(0,0,W,H,'#fffdf8');box(M,12*mm,CW,2,'#263449');y=16*mm
 y+=text(section+(' · 계속' if cont else ''),M,y,CW,9,'#287f78')+9
 y+=text(title,M,y,CW,20,bold=True)+13
 records.append({'page':num,'section':section,'title':title,'blocks':[]})
def end():
 text('해킹·침해대응 실무 with Wazuh · 시범 원고',M,H-11*mm,CW-35,8,'#687581');text(str(num),W-M-25,H-11*mm,25,8,'#687581');showpage(cr)
def ensure(h):
 if y+h>BOTTOM:end();start(True)
def para(s,size=10.5,bg=None,mono=False,bold=False):
 global y
 pad=8 if bg else 0
 h=text(s,0,0,CW-2*pad,size,mono=mono,bold=bold,draw=False)+2*pad
 ensure(h)
 if bg:box(M,y,CW,h,bg)
 text(s,M+pad,y+pad,CW-2*pad,size,mono=mono,bold=bold)
 records[-1]['blocks'].append({'kind':'text','y':round(y,1),'height':round(h,1),'font_pt':size});y+=h+8

def image(node,detail=False):
 global y
 src=node.attrs['src'];path=R/src
 if path.suffix=='.svg':
  _,_,iw,ih=map(float,ET.parse(path).getroot().attrib['viewBox'].split())
 else:iw,ih=Image.open(path).size
 dw=250*mm if detail else CW;dh=ih*dw/iw
 ensure(dh+8)
 save(cr);rect(cr,M,y,CW,dh);clip(cr);translate(cr,M,y);scale(cr,dw/iw,dh/ih)
 if path.suffix=='.svg':
  handle=rnew(str(path).encode(),None);assert handle;assert rrender(handle,cr);unref(handle)
 else:
  im=png(str(path).encode());assert status(im)==0;source(cr,im,0,0);paint(cr);destroy(im)
 restore(cr);records[-1]['blocks'].append({'kind':'image','src':src,'y':round(y,1),'height':round(dh,1),'source_px':[iw,ih],'display_width_mm':round(dw/mm,1)});y+=dh+8

def walk(node):
 global y
 if not isinstance(node,N):return
 t=node.tag
 if t=='p':para(node.text(),8 if node.attrs.get('class')=='file' else 10.5)
 elif t=='h3':para(node.text(),13,bold=True)
 elif t=='pre':para(node.text(),10,bg='#eef3f4',mono=True)
 elif t=='aside':para(node.text(),10,bg='#f4ebdd')
 elif t in ['ol','ul']:
  items=[n for n in node.children if isinstance(n,N) and n.tag=='li']
  for i,item in enumerate(items,1):para((f'{i}. ' if t=='ol' else '• ')+item.text())
 elif t=='figure':
  img=node.find('img');cap=node.find('figcaption');div=node.find('div');detail='detail' in div.attrs.get('class','')
  image(img,detail)
  if cap:para(cap.text(),9)
 elif t=='img':image(node)
 elif t=='table':
  for tr in node.children:
   if not isinstance(tr,N) or tr.tag!='tr':continue
   cells=[a for a in tr.children if isinstance(a,N) and a.tag in ['td','th']];cw=CW/len(cells)
   h=max(text(a.text(),0,0,cw-10,9.5,draw=False) for a in cells)+12;ensure(h)
   header=cells[0].tag=='th'
   if header:box(M,y,CW,h,'#edf2f1')
   for i,a in enumerate(cells):text(a.text(),M+cw*i+5,y+6,cw-10,9.5)
   box(M,y+h,CW,.5,'#c8d1d4');y+=h
  y+=8
 else:
  for child in node.children:walk(child)

pages=json.loads((R/'manuscript/sample.json').read_text())
for item in pages:
 section=item['section'];title=Parser(item['title']).root.text();start()
 for node in Parser(item['body']).root.children:walk(node)
 end()
finish(surface);assert status(surface)==0;destroy(surface)
(R/'editorial/print-layout.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('Printed',num,'B5 pages with Cairo/Pango')
