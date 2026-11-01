"""부크크 원본 DOCX에서 첫 구역의 판형·여백·테마를 상속하는 저자용 조판기."""
import argparse
import json
from copy import deepcopy
from pathlib import Path
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT=Path(__file__).resolve().parents[1]
BODY='부크크 명조 Light'
HEAD='부크크 고딕 Light'
MONO='Consolas'

def font(r,name=BODY,size=10.5):
    r.font.name=name; r.font.size=Pt(size);r.font.color.rgb=RGBColor(0,0,0)
    rf=r._r.get_or_add_rPr().get_or_add_rFonts()
    for x in ['ascii','hAnsi','cs']:rf.set(qn('w:'+x),name)
    rf.set(qn('w:eastAsia'),BODY if name==MONO else name)
    return r

def para(parent,text='',size=10.5,name=BODY,after=6,keep=False,align=None):
    p=parent.add_paragraph()
    pf=p.paragraph_format;pf.space_before=Pt(0);pf.space_after=Pt(after);pf.line_spacing=1.35
    pf.first_line_indent=Mm(0);pf.left_indent=Mm(0);pf.right_indent=Mm(0)
    pf.keep_with_next=keep;pf.keep_together=True;pf.widow_control=True
    p.alignment=align or WD_ALIGN_PARAGRAPH.LEFT
    snap=OxmlElement('w:snapToGrid');snap.set(qn('w:val'),'0');p._p.get_or_add_pPr().append(snap)
    font(p.add_run(text),name,size)
    return p

def border(pr,tag='w:pBdr'):
    b=OxmlElement(tag)
    for side in ['top','left','bottom','right']:
        el=OxmlElement('w:'+side)
        for k,v in [('val','single'),('sz','4'),('space','4'),('color','000000')]:el.set(qn('w:'+k),v)
        b.append(el)
    pr.append(b)

def table(doc,block):
    widths=block.get('widths') or [40,87]
    t=doc.add_table(rows=1,cols=len(block['head']));t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.style='Normal Table'
    for col,w in zip(t.columns,widths):col.width=Mm(w)
    for n,vals in enumerate([block['head']]+block['rows']):
        row=t.rows[0] if n==0 else t.add_row()
        trpr=row._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
        if n==0:trpr.append(OxmlElement('w:tblHeader'))
        for cell,txt,w in zip(row.cells,vals,widths):
            cell.width=Mm(w);pr=cell._tc.get_or_add_tcPr();border(pr,'w:tcBorders')
            mar=OxmlElement('w:tcMar')
            for k,v in [('top',55),('bottom',55),('left',85),('right',85)]:
                e=OxmlElement('w:'+k);e.set(qn('w:w'),str(v));e.set(qn('w:type'),'dxa');mar.append(e)
            pr.append(mar)
            old=cell.paragraphs[0]
            cell._tc.remove(old._p)
            para(cell,txt,size=10,name=HEAD if n==0 else BODY,after=0)
    para(doc,'',size=1,after=3).paragraph_format.line_spacing=1

def build(output,source=None):
    data=json.loads((source or ROOT/'manuscript/volume01-chapter01.json').read_text())
    doc=Document(ROOT/'tools/assets/bookk-B5.docx')
    sect=deepcopy(doc.sections[0]._sectPr)
    for x in list(doc.element.body):doc.element.body.remove(x)
    doc.element.body.append(sect)
    for tag in ['w:type','w:docGrid']:
        e=sect.find(qn(tag))
        if e is not None:sect.remove(e)
    # 테마와 판면은 보존하고 예시 본문·머리말 내용은 제거한다.
    s=doc.sections[0]
    for container in [s.header,s.even_page_header,s.first_page_header,s.footer,s.even_page_footer,s.first_page_footer]:
        for e in list(container._element):container._element.remove(e)
    for foot in [s.footer,s.even_page_footer]:
        p=para(foot,'',name=HEAD,size=9,align=WD_ALIGN_PARAGRAPH.CENTER)
        field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');p._p.append(field)
    normal=doc.styles['Normal'];normal.font.name=BODY;normal.font.size=Pt(10.5)
    normal.paragraph_format.space_after=Pt(6)
    for idx,pg in enumerate(data['pages']):
        title=para(doc,pg['title'],size=25 if pg['kind']=='cover' else 16,name=HEAD,after=13,keep=True)
        title.paragraph_format.page_break_before=idx>0
        if pg['kind']=='cover':
            title.paragraph_format.space_before=Pt(120)
            title.alignment=WD_ALIGN_PARAGRAPH.CENTER
        for b in pg['blocks']:
            typ=b['type']
            if typ=='p':para(doc,b['text'],align=WD_ALIGN_PARAGRAPH.CENTER if pg['kind']=='cover' else None)
            elif typ=='h':para(doc,b['text'],size=11.5,name=HEAD,after=5,keep=True)
            elif typ in ('command','query'):
                para(doc,b['id']+'  |  '+b['where'],size=9,name=HEAD,after=2,keep=True)
                # 역할·기호 → 입력 → 판정 순서. 한 명령 블록은 같은 쪽에 둔다.
                para(doc,b['why'],after=3,keep=True)
                p=para(doc,b['text'],size=10,name=MONO,after=4,keep=True)
                p.paragraph_format.line_spacing=1.15
                border(p._p.get_or_add_pPr())
                para(doc,'확인  '+b['result'],after=9)
            elif typ=='code':
                para(doc,b['text'],name=MONO,size=10,after=6)
            elif typ=='table':table(doc,b)
            elif typ=='image':
                p=para(doc,'',after=3,keep=True,align=WD_ALIGN_PARAGRAPH.RIGHT if b.get('align')=='right' else WD_ALIGN_PARAGRAPH.CENTER)
                p.paragraph_format.line_spacing=1
                p.add_run().add_picture(str(ROOT/b['path']),width=Mm(b.get('width_mm',127)))
                para(doc,b['caption'],size=9,after=7,align=WD_ALIGN_PARAGRAPH.RIGHT if b.get('align')=='right' else None)
            elif typ=='capture_slot':
                t=doc.add_table(rows=1,cols=1);t.autofit=False;t.columns[0].width=Mm(127)
                cell=t.cell(0,0);cell.width=Mm(127);border(cell._tc.get_or_add_tcPr(),'w:tcBorders')
                cell._tc.remove(cell.paragraphs[0]._p)
                para(cell,b['title'],name=HEAD,size=10,after=4)
                para(cell,b['text'],size=9.5,after=4)
                para(doc,'',size=1,after=3)
            elif typ=='link':
                p=para(doc,'',size=10,after=7)
                link=OxmlElement('w:hyperlink');link.set(qn('r:id'),p.part.relate_to(b['url'],RT.HYPERLINK,is_external=True))
                r=font(p.add_run(b['text']),BODY,10);p._p.remove(r._r);link.append(r._r);p._p.append(link)
                p.paragraph_format.keep_with_next=True
                urlpara=para(doc,'',name=MONO,size=10,after=9)
                url_link=OxmlElement('w:hyperlink');url_link.set(qn('r:id'),p.part.relate_to(b['url'],RT.HYPERLINK,is_external=True))
                r=font(urlpara.add_run(b['url']),MONO,10);urlpara._p.remove(r._r);url_link.append(r._r);urlpara._p.append(url_link)
            else:raise ValueError(typ)
    doc.core_properties.title=data['title'];doc.core_properties.subject=data['series'];doc.core_properties.language='ko-KR'
    doc.core_properties.author='';doc.core_properties.comments='신규 원고. 설치 절차는 문서·코드 대조 상태. 실제 UI는 기존 가동 환경에서 촬영.'
    output.parent.mkdir(parents=True,exist_ok=True);doc.save(output)
    print(output)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'build/volume01-chapter01.docx')
    ap.add_argument('--source',type=Path)
    args=ap.parse_args();build(args.output,args.source)
