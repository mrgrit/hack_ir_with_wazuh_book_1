#!/usr/bin/env python3
"""Author-only DOCX typesetting. Does not connect to kt66 or run lab commands."""
import argparse
import json
from pathlib import Path
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ROW_HEIGHT_RULE, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
ROOT = Path(__file__).resolve().parents[1]
INK='21364C'; TEAL='24767C'; MUTED='516475'; LIGHT='F1F5F6'

def font(style,name,size,color=INK):
    style.font.name=name; style.font.size=Pt(size); style.font.color.rgb=RGBColor.from_string(color)
    rpr=style.element.get_or_add_rPr()
    fonts=rpr.find(qn('w:rFonts'))
    if fonts is None: fonts=OxmlElement('w:rFonts');rpr.append(fonts)
    for k in ('ascii','hAnsi','eastAsia','cs'):fonts.set(qn('w:'+k),name)
    lang=OxmlElement('w:lang');lang.set(qn('w:val'),'en-US');lang.set(qn('w:eastAsia'),'ko-KR');rpr.append(lang)

def shade(cell,fill):
    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),fill);cell._tc.get_or_add_tcPr().append(sh)

def set_cell_text(cell,text,style):
    cell.text='';p=cell.paragraphs[0];p.style=style;p.add_run(text)
    cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER

def no_split(row):
    x=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(x)

def link(p,title,url):
    h=OxmlElement('w:hyperlink');h.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True))
    r=OxmlElement('w:r');pr=OxmlElement('w:rPr')
    col=OxmlElement('w:color');col.set(qn('w:val'),TEAL);pr.append(col)
    u=OxmlElement('w:u');u.set(qn('w:val'),'single');pr.append(u)
    r.append(pr);t=OxmlElement('w:t');t.text=title;r.append(t);h.append(r);p._p.append(h)

def field(p,name):
    r=p.add_run(); f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),name);r._r.addnext(f)

def build(source,target):
    data=json.loads(source.read_text());doc=Document();sec=doc.sections[0]
    chapter=data.get('chapter',1)
    sec.page_width=Mm(182);sec.page_height=Mm(257)
    sec.top_margin=Mm(16);sec.bottom_margin=Mm(17);sec.left_margin=Mm(18);sec.right_margin=Mm(18)
    sec.header_distance=Mm(7);sec.footer_distance=Mm(8)
    font(doc.styles['Normal'],'Noto Sans CJK KR',10.5)
    wrap=OxmlElement('w:wordWrap');wrap.set(qn('w:val'),'0');doc.styles['Normal'].element.get_or_add_pPr().append(wrap)
    pf=doc.styles['Normal'].paragraph_format;pf.line_spacing=1.22;pf.space_after=Pt(5);pf.widow_control=True
    for name,size,color in [('Title',27,INK),('Subtitle',12,TEAL),('Heading 1',19,INK),('Heading 2',12,TEAL)]:
        font(doc.styles[name],'Noto Sans CJK KR',size,color)
        doc.styles[name].paragraph_format.space_after=Pt(9)
    for name,size,color in [('BookSmall',8.5,MUTED),('BookTable',9.5,INK),('BookNote',9.4,MUTED),('BookCode',9.3,INK),('BookCaption',9.2,TEAL)]:
        st=doc.styles.add_style(name,1);st.base_style=doc.styles['Normal'];font(st,'Noto Sans Mono CJK KR' if name=='BookCode' else 'Noto Sans CJK KR',size,color)
        st.paragraph_format.space_after=Pt(4);st.paragraph_format.line_spacing=1.16
    doc.styles['BookCode'].paragraph_format.left_indent=Mm(2)
    doc.styles['BookCode'].paragraph_format.keep_together=True
    doc.styles['BookCaption'].paragraph_format.keep_with_next=True
    hp=sec.header.paragraphs[0];hp.style=doc.styles['BookSmall'];hp.text='해킹·침해대응 실무 with Wazuh  |  1권 집필 초안'
    fp=sec.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.CENTER;fp.style=doc.styles['BookSmall'];field(fp,'PAGE')
    for n,page in enumerate(data['pages']):
        if page['kind']=='cover':
            doc.add_paragraph('VOLUME 01',style='Subtitle');doc.add_paragraph(page['subtitle'],style='Subtitle')
            doc.add_paragraph(page['title'],style='Title');doc.add_paragraph('')
        else:
            title_p=doc.add_paragraph(page['title'],style='Heading 1')
            title_p.paragraph_format.page_break_before=bool(n)
            if page['subtitle']:doc.add_paragraph(page['subtitle'],style='Subtitle')
        for b in page['blocks']:
            typ=b['type']
            if typ=='p':doc.add_paragraph(b['text'])
            elif typ=='h':doc.add_paragraph(b['text'],style='Heading 2')
            elif typ=='note':
                t=doc.add_table(rows=1,cols=1);t.autofit=False;t.columns[0].width=Mm(146)
                shade(t.cell(0,0),LIGHT);set_cell_text(t.cell(0,0),b['text'],'BookNote');no_split(t.rows[0]);doc.add_paragraph().paragraph_format.space_after=Pt(0)
            elif typ=='table':
                t=doc.add_table(rows=1,cols=len(b['head']));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
                widths=b.get('widths', [48,98] if len(b['head'])==2 else [146/len(b['head'])]*len(b['head']))
                for col,w in zip(t.columns,widths):col.width=Mm(w)
                for i,v in enumerate(b['head']):set_cell_text(t.rows[0].cells[i],v,'BookTable');shade(t.rows[0].cells[i],'DAE8EC');t.rows[0].cells[i].paragraphs[0].runs[0].bold=True
                repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
                for j,row in enumerate(b['rows']):
                    rr=t.add_row();no_split(rr)
                    for i,v in enumerate(row):set_cell_text(rr.cells[i],v,'BookTable');shade(rr.cells[i],'F3F6F7' if j%2==0 else 'FFFFFF')
                doc.add_paragraph().paragraph_format.space_after=Pt(0)
            elif typ in ('cmd','code'):
                if typ=='cmd':
                    pp=doc.add_paragraph(f'C{chapter:02}-'+b['id']+'  |  '+b['where'],style='BookSmall');pp.paragraph_format.keep_with_next=True
                else:
                    pp=doc.add_paragraph(b['label'],style='BookSmall');pp.paragraph_format.keep_with_next=True
                cp=doc.add_paragraph(b['text'],style='BookCode')
                pp=cp._p.get_or_add_pPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),LIGHT);pp.append(sh)
                if typ=='cmd':
                    cp.paragraph_format.keep_with_next=True
                    doc.add_paragraph(b['why'])
                    pp=doc.add_paragraph();r=pp.add_run('확인  ');r.bold=True;pp.add_run(b['result'])
            elif typ=='shot':
                cap=f'그림 {chapter}-{b["id"]}  {b["title"]}'
                doc.add_paragraph(cap,style='BookCaption')
                t=doc.add_table(rows=1,cols=1);t.autofit=False;t.columns[0].width=Mm(146)
                row=t.rows[0];row.height=Mm(b.get('height_mm',60));row.height_rule=WD_ROW_HEIGHT_RULE.AT_LEAST;no_split(row)
                c=t.cell(0,0);shade(c,'F4F5F7');c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                pp=c.paragraphs[0];pp.style=doc.styles['BookNote'];pp.alignment=WD_ALIGN_PARAGRAPH.CENTER
                pp.paragraph_format.keep_with_next=True
                pp.add_run('[실제 화면 삽입 자리]\n').bold=True;pp.add_run('촬영 후 이 문구를 지우고 그림을 삽입합니다.\n최종 크기에서 글자가 읽히도록 화면을 나누어 사용합니다.')
                pp=c.add_paragraph('촬영 메모 · '+b['text'],style='BookSmall')
            elif typ=='source':
                pp=doc.add_paragraph(style='BookNote');link(pp,b['text'],b['url'])
            elif typ=='image':
                pp=doc.add_paragraph();pp.paragraph_format.keep_with_next=True
                pp.add_run().add_picture(str(ROOT/b['path']),width=Mm(b.get('width_mm',146)))
                pp=doc.add_paragraph(b['caption'],style='BookSmall')
            elif typ=='flow':
                doc.add_paragraph(b['title'],style='BookCaption')
                count=len(b['nodes']);arrow_width=5;node_width=(146-arrow_width*(count-1))/count
                t=doc.add_table(rows=1,cols=count*2-1);t.autofit=False
                row=t.rows[0];no_split(row)
                for i,col in enumerate(t.columns):
                    width=node_width if i%2==0 else arrow_width
                    col.width=Mm(width);row.cells[i].width=Mm(width)
                    if i%2:
                        set_cell_text(row.cells[i],'→','BookTable')
                        row.cells[i].paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER
                    else:
                        title,detail=b['nodes'][i//2]
                        set_cell_text(row.cells[i],title+'\n'+detail,'BookTable')
                        row.cells[i].paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER
                        shade(row.cells[i],'DAE8EC' if i==0 else LIGHT)
                doc.add_paragraph().paragraph_format.space_after=Pt(0)
            else:raise ValueError(typ)
    doc.core_properties.title=data['title']+' — '+data.get('document_label','목차·머리말·1장')
    doc.core_properties.subject=data['series'];doc.core_properties.author='집필팀';doc.core_properties.language='ko-KR'
    doc.core_properties.comments=data.get('verification_note','저장소 기반 집필 초안. 실제 설치·화면 촬영 검증 대기.')
    target.parent.mkdir(parents=True,exist_ok=True);doc.save(target)
    print(target)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=ROOT/'manuscript/volume01-opening.json');ap.add_argument('--output',type=Path,default=ROOT/'build/docx/volume01-opening.generated.docx');args=ap.parse_args();build(args.source,args.output)
