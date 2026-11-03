"""기존 B5 조판과 10장 후처리를 11장·부록에 적용한다."""
import argparse,json
from pathlib import Path
from docx import Document
from docx.shared import RGBColor
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from build_chapter01 import build,ROOT
def main(name,output_dir):
 source=ROOT/f'manuscript/volume01-{name}.json';data=json.loads(source.read_text('utf8'))
 tmp=ROOT/f'build/volume01-final/{name}-base.docx';build(tmp,source);doc=Document(tmp)
 for name_ in ('Title','Heading 1','Heading 2'):
  if name_ not in doc.styles:doc.styles.add_style(name_,WD_STYLE_TYPE.PARAGRAPH)
  doc.styles[name_].font.color.rgb=RGBColor(0,0,0)
 titles={pg['title']:('Title' if i==0 else 'Heading 1' if pg.get('major') else 'Heading 2') for i,pg in enumerate(data['pages'])}
 for para in doc.paragraphs:
  if para.text in titles:para.style=doc.styles[titles[para.text]]
 for t in doc.tables:
  pr=t._tbl.tblPr;b=OxmlElement('w:tblBorders')
  for side in ('top','left','bottom','right','insideH','insideV'):
   e=OxmlElement('w:'+side)
   for k,v in [('val','single'),('sz','4'),('color','000000')]:e.set(qn('w:'+k),v)
   b.append(e)
  pr.append(b)
  for node in t._tbl.xpath('.//w:tcBorders'):
   for e in node:e.attrib.pop(qn('w:space'),None)
 for shape,cap in zip(doc.inline_shapes,[b['caption'] for pg in data['pages'] for b in pg['blocks'] if b['type']=='image']):shape._inline.docPr.set('descr',cap)
 for link in doc.element.body.xpath('.//w:hyperlink'):
  value=''.join(link.xpath('.//w:t/text()'))
  if not value.startswith('https://') or len(value)<=58:continue
  parts=[];remain=value
  while len(remain)>58:
   cut=remain.rfind('/',8,58)+1
   if cut<=8:break
   parts.append(remain[:cut]);remain=remain[cut:]
  parts.append(remain);run=link.find(qn('w:r'))
  for el in list(run):
   if el.tag!=qn('w:rPr'):run.remove(el)
  for i,part in enumerate(parts):
   if i:run.append(OxmlElement('w:br'))
   t=OxmlElement('w:t');t.text=part;run.append(t)
 output_dir.mkdir(parents=True,exist_ok=True)
 out=output_dir/f'volume01-{name}.docx';doc.save(out);print(out)
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('names',nargs='*',choices=['chapter11','appendices'])
 parser.add_argument('--output-dir',type=Path,default=ROOT/'build/volume01-final')
 args=parser.parse_args()
 for n in args.names or ['chapter11','appendices']:main(n,args.output_dir)
