"""8장 원고·복사용 예제·실제 화면·B5 조판 검사. 네트워크 실행 없음."""
import argparse,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from docx import Document
from pypdf import PdfReader
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
def check(docx,pdf,bash=None):
 data=json.loads((ROOT/'manuscript/volume01-chapter08.json').read_text(encoding='utf-8'))
 blocks=[b for p in data['pages'] for b in p['blocks']]
 doc=Document(docx);base=Document(ROOT/'tools/assets/bookk-B5.docx')
 geo=['page_width','page_height','left_margin','right_margin','top_margin','bottom_margin','gutter']
 assert all(getattr(doc.sections[0],k)==getattr(base.sections[0],k) for k in geo)
 with zipfile.ZipFile(docx) as z,zipfile.ZipFile(ROOT/'tools/assets/bookk-B5.docx') as b:
  assert z.read('word/theme/theme1.xml')==b.read('word/theme/theme1.xml')
  assert not re.search(rb'ghp_[A-Za-z0-9]{20,}',z.read('word/document.xml'))
 for b in blocks:
  if b['type'] in ('command','query'):
   assert (ROOT/'examples/chapter08'/f"{b['id']}.txt").read_text(encoding='utf-8').rstrip('\n')==b['text'],b['id']
   if b['type']=='command' and bash:
    r=subprocess.run([str(bash),'--noprofile','--norc','-n'],input=b['text'],capture_output=True,text=True,encoding='utf-8');assert r.returncode==0,(b['id'],r.stderr)
  if b['type']=='image':assert (ROOT/b['path']).exists()
 assert len(doc.inline_shapes)==sum(b['type']=='image' for b in blocks)
 prov=json.loads((ROOT/'assets/screens/chapter08/provenance.json').read_text(encoding='utf-8'))
 for a in prov['assets']:
  orig=ROOT/a['original'];assert hashlib.sha256(orig.read_bytes()).hexdigest()==a['original_sha256']
  im=Image.open(orig).crop(a['crop_xyxy']).convert('RGB');actual=Image.open(ROOT/a['asset']).convert('RGB')
  assert im.size==actual.size and ImageChops.difference(im,actual).getbbox() is None,a['asset']
 proof=json.loads((ROOT/'editorial/evidence/chapter08/2026-11-02/query-proof.json').read_text(encoding='utf-8'))
 qs={b['id']:b['text'] for b in blocks if b['type']=='query'}
 assert {x['id']:x['text'] for x in proof}==qs
 assert all(x.get('hits') is not None or x.get('noResults') for x in proof)
 r=PdfReader(pdf);text='\n'.join(p.extract_text() for p in r.pages);compact=re.sub(r'\s+','',text)
 for b in blocks:
  if b['type']=='link':assert re.sub(r'\s+','',b['url']) in compact,b['url']
 fonts=sorted({str(v.get_object().get('/BaseFont')) for p in r.pages for v in p['/Resources'].get('/Font',{}).values()})
 for f in ['BookkMyungjo-Lt','BookkGothic-Lt','Consolas']:assert any(f in x for x in fonts),f
 result={'pages':len(r.pages),'geometry_mm':{k:round(getattr(doc.sections[0],k).mm,2) for k in geo},'commands':sum(b['type']=='command' for b in blocks),'DQL':len(qs),'screens':len(prov['assets']),'images_inserted':len(doc.inline_shapes),'copy_parity':True,'bash_syntax_only':bool(bash),'actual_DQL_results':{x['id']:x.get('hits') for x in proof},'source_pixel_integrity':True,'template_theme_equal':True,'full_reference_urls':True,'fonts':fonts}
 print(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('docx',type=Path);ap.add_argument('pdf',type=Path);ap.add_argument('--bash',type=Path);ap.add_argument('--output',type=Path);a=ap.parse_args();r=check(a.docx,a.pdf,a.bash)
 if a.output:a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
