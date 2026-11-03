"""REV02 전용 연속 조판기. 공통 조판기와 REV01 산출물은 변경하지 않는다."""
from pathlib import Path
from copy import deepcopy
import json,re
from docx import Document
from PIL import Image
from docx.shared import Mm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from build_chapter01 import font,runs,table,box,items,border,fit_existing_frame,BODY,HEAD,MONO

ROOT=Path(__file__).resolve().parents[1]

def para(parent,text='',name=BODY,size=10.5,after=6,keep=False,style=None):
    p=parent.add_paragraph(style=style)
    f=p.paragraph_format;f.space_before=Pt(0);f.space_after=Pt(after);f.line_spacing=1.35
    f.keep_with_next=keep;f.keep_together=False;f.widow_control=True
    f.left_indent=Mm(0);f.right_indent=Mm(0);f.first_line_indent=Mm(0)
    pr=p._p.get_or_add_pPr()
    for tag,val in [('snapToGrid','0'),('wordWrap','0')]:
        e=OxmlElement('w:'+tag);e.set(qn('w:val'),val);pr.append(e)
    runs(p,text,name,size)
    return p

def heading(doc,text,level=1):
    p=para(doc,text,name=HEAD,size={0:20,1:13.5,2:11.5}[level],after=8,keep=True,style='Title' if level==0 else 'Heading '+str(level))
    p.paragraph_format.space_before=Pt(0 if level==0 else 12)
    return p

def build(src):
    data=json.loads(src.read_text('utf8'))
    doc=Document(ROOT/'tools/assets/bookk-B5.docx')
    sect=deepcopy(doc.sections[0]._sectPr)
    for el in list(doc.element.body):doc.element.body.remove(el)
    doc.element.body.append(sect)
    for tag in ['w:type','w:docGrid']:
        e=sect.find(qn(tag))
        if e is not None:sect.remove(e)
    sec=doc.sections[0]
    for container in [sec.header,sec.even_page_header,sec.first_page_header,sec.footer,sec.even_page_footer,sec.first_page_footer]:
        for e in list(container._element):container._element.remove(e)
    for header in [sec.header,sec.even_page_header]:
        p=para(header,data['title'].replace('\n',' '),name=HEAD,size=8,after=0)
    for footer in [sec.footer,sec.even_page_footer]:
        p=para(footer,'',name=HEAD,size=9,after=0);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        el=OxmlElement('w:fldSimple');el.set(qn('w:instr'),'PAGE');p._p.append(el)
    for name in ['Normal','Title','Heading 1','Heading 2','Heading 3']:
        if name not in doc.styles:doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
        st=doc.styles[name];st.font.name=BODY if name=='Normal' else HEAD;st.font.color.rgb=RGBColor(0,0,0)
        st.font.size=Pt(10.5 if name=='Normal' else 13.5)
        for b in st.element.xpath('./w:pPr/w:pBdr'):b.getparent().remove(b)
    for ix,pg in enumerate(data['pages']):
        title=pg['title'];level=pg.get('level','section')
        if pg['kind']=='cover':
            p=heading(doc,title,0);p.paragraph_format.space_before=Pt(115);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        else:
            p=heading(doc,title,0 if ix==0 or level=='chapter' else 2 if level=='subsection' else 1)
        p.paragraph_format.page_break_before=ix>0 and pg.get('break',False)
        for b in pg['blocks']:
            typ=b['type']
            if typ=='p':
                p=para(doc,b['text'])
                if pg['kind']=='cover':p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            elif typ=='h':heading(doc,b['text'],2)
            elif typ in ('command','query'):
                p=para(doc,b['id']+'  |  '+b['where'],name=HEAD,size=9,after=3,keep=True)
                if 'purpose' in b:
                    para(doc,'**목적**  '+b['purpose'],after=3,keep=True)
                    if b.get('syntax'):para(doc,'**구문**  '+b['syntax'],after=4,keep=True)
                else:para(doc,b['why'],after=4,keep=True)
                p=para(doc,b['text'],name=MONO,size=10,after=5,keep=True)
                p.paragraph_format.line_spacing=1.15;p.paragraph_format.keep_together=True
                border(p._p.get_or_add_pPr())
                para(doc,'**확인**  '+b['result'],after=10)
            elif typ=='code':
                p=para(doc,b['text'],name=MONO,size=10,after=6)
                p.paragraph_format.line_spacing=1.15;p.paragraph_format.keep_together=True
            elif typ=='table':
                clean=deepcopy(b);clean['keep']=False
                table(doc,clean)
                tbl=doc.tables[-1]
                pr=tbl._tbl.tblPr
                spacing=OxmlElement('w:tblCellSpacing');spacing.set(qn('w:w'),'0');spacing.set(qn('w:type'),'dxa');pr.append(spacing)
                borders=OxmlElement('w:tblBorders')
                for side in ['top','left','bottom','right','insideH','insideV']:
                    edge=OxmlElement('w:'+side)
                    for k,v in [('val','single'),('sz','4'),('color','000000'),('space','0')]:edge.set(qn('w:'+k),v)
                    borders.append(edge)
                pr.append(borders)
                for cell in tbl.rows[0].cells:
                    tcpr=cell._tc.get_or_add_tcPr()
                    for node in tcpr.findall(qn('w:shd')):tcpr.remove(node)
                    shading=OxmlElement('w:shd')
                    shading.set(qn('w:val'),'clear');shading.set(qn('w:color'),'auto');shading.set(qn('w:fill'),'E7E7E7')
                    tcpr.append(shading)
                    cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    for p in cell.paragraphs:p.alignment=WD_ALIGN_PARAGRAPH.CENTER
                for row in tbl.rows:
                    for cell in row.cells:
                        for node in cell._tc.xpath('./w:tcPr/w:tcBorders'):node.getparent().remove(node)
                        for p in cell.paragraphs:
                            p.paragraph_format.keep_with_next=False
                            p.paragraph_format.keep_together=True
                if len(tbl.rows)>2:
                    for cell in tbl.rows[-2].cells:
                        for p in cell.paragraphs:p.paragraph_format.keep_with_next=True
            elif typ=='box':box(doc,b)
            elif typ=='list':items(doc,b)
            elif typ=='image':
                p=para(doc,'',after=3,keep=True);p.alignment=WD_ALIGN_PARAGRAPH.RIGHT if b.get('align')=='right' else WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.line_spacing=1
                s=p.add_run().add_picture(str(ROOT/b['path']),width=Mm(b.get('width_mm',127)))
                fit_existing_frame(s,b['path'])
                if b.get('crop_px'):
                    # Word의 비파괴 자르기. 화면 원본 픽셀과 증거 파일은 보존한다.
                    iw,ih=Image.open(ROOT/b['path']).size
                    left,top,right,bottom=b['crop_px']
                    assert 0<=left<right<=iw and 0<=top<bottom<=ih
                    fill=s._inline.graphic.graphicData.pic.blipFill
                    for old in fill.findall(qn('a:srcRect')):fill.remove(old)
                    rect=OxmlElement('a:srcRect')
                    for k,v in [('l',left/iw),('t',top/ih),('r',(iw-right)/iw),('b',(ih-bottom)/ih)]:rect.set(k,str(round(v*100000)))
                    fill.insert(1,rect)
                    s.height=int(s.width*(bottom-top)/(right-left))
                p=para(doc,b['caption'],size=9,after=8)
                if b.get('align')=='right':p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
            elif typ=='capture_slot':
                para(doc,b['title'],name=HEAD,size=10,keep=True)
                para(doc,b['text'],size=10)
            elif typ=='link':
                para(doc,b['text'],size=10,after=3,keep=True)
                p=para(doc,'',name=MONO,size=10,after=9)
                h=OxmlElement('w:hyperlink');h.set(qn('r:id'),p.part.relate_to(b['url'],RT.HYPERLINK,is_external=True))
                r=font(p.add_run(b['url']),MONO,10);p._p.remove(r._r);h.append(r._r);p._p.append(h)
            else:raise ValueError(typ)
    doc.core_properties.title=data['title'];doc.core_properties.subject=data['series'];doc.core_properties.language='ko-KR'
    doc.core_properties.author='';doc.core_properties.comments='REV02. 검증 범위는 editorial/REV02의 검토 기록을 참조한다.'
    out=src.with_suffix('.docx');doc.save(out);print(out.name)

if __name__=='__main__':
    import sys
    paths=[Path(x) for x in sys.argv[1:]] or sorted((ROOT/'manuscript/REV02').glob('*.json'))
    for p in paths:build(p)
