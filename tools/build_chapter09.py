"""기존 B5 조판기를 사용하고 9장의 제목 의미와 그림 대체 텍스트를 지정한다."""
import argparse,json,io
from pathlib import Path
from docx import Document
from docx.shared import RGBColor
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from build_chapter01 import build,ROOT
def main(output):
    source=ROOT/'manuscript/volume01-chapter09.json'
    intermediate=ROOT/'build/chapter09/layout-base.docx';build(intermediate,source)
    data=json.loads(source.read_text(encoding='utf-8'));doc=Document(intermediate)
    for name in ('Title','Heading 1','Heading 2'):
        if name not in doc.styles:
            style=doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
            style.base_style=doc.styles['Normal']
    titles={p['title']:('Title' if i==0 else 'Heading 1' if p.get('major') or p.get('break') else 'Heading 2') for i,p in enumerate(data['pages'])}
    for p in doc.paragraphs:
        if p.text in titles:p.style=doc.styles[titles[p.text]]
    for name in ('Title','Heading 1','Heading 2'):
        doc.styles[name].font.color.rgb=RGBColor(0,0,0)
    for t in doc.tables:
        pr=t._tbl.tblPr
        spacing=OxmlElement('w:tblCellSpacing');spacing.set(qn('w:w'),'0');spacing.set(qn('w:type'),'dxa');pr.append(spacing)
        borders=OxmlElement('w:tblBorders')
        for side in ('top','left','bottom','right','insideH','insideV'):
            e=OxmlElement('w:'+side)
            for k,v in [('val','single'),('sz','4'),('color','000000')]:e.set(qn('w:'+k),v)
            borders.append(e)
        pr.append(borders)
        for node in t._tbl.xpath('.//w:tcBorders'):
            for e in node:
                if qn('w:space') in e.attrib:del e.attrib[qn('w:space')]
    captions=[b['caption'] for p in data['pages'] for b in p['blocks'] if b['type']=='image']
    for shape,caption in zip(doc.inline_shapes,captions):shape._inline.docPr.set('descr',caption)
    # 긴 URL은 글자 크기와 주소를 유지하고 경로 구분자 뒤에서 나눈다.
    for link in doc.element.body.xpath('.//w:hyperlink'):
        value=''.join(link.xpath('.//w:t/text()'))
        if not value.startswith('https://') or len(value)<=58:continue
        parts=[];remain=value
        while len(remain)>58:
            cut=remain.rfind('/',8,58)+1
            if cut<=8:break
            parts.append(remain[:cut]);remain=remain[cut:]
        parts.append(remain)
        run=link.find(qn('w:r'))
        for el in list(run):
            if el.tag!=qn('w:rPr'):run.remove(el)
        for i,part in enumerate(parts):
            if i:run.append(OxmlElement('w:br'))
            t=OxmlElement('w:t');t.text=part;run.append(t)
    stream=io.BytesIO();doc.save(stream)
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(stream.getvalue())
    print(output)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'build/volume01-chapter09.docx');main(ap.parse_args().output)
