"""제공된 PPTX의 기존 화면을 추출·분할한다. 새 UI를 생성하지 않는다."""
import argparse,hashlib,json,posixpath,zipfile
from pathlib import Path
from xml.etree import ElementTree as E
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
# crop coordinates are in the unchanged embedded image's pixels.
SPECS=[
 ('fim-event',227,(0,0,450,116)),('fim-path',227,(0,120,390,236)),
 ('log4-rule',238,(0,0,445,120)),('log4-raw',238,(170,126,750,242)),
 ('shell-rules',249,(290,0,861,182)),('shell-raw',249,(165,190,735,366)),
 ('exec-rule',259,(0,0,440,116)),('exec-status',259,(0,120,380,236)),('exec-url',259,(380,120,735,236)),
 ('ok-rule',267,(0,0,430,116)),('ok-status',267,(100,120,475,236)),('ok-url',267,(475,120,815,236)),
 ('error-rule',275,(0,0,460,116)),('error-status',275,(0,120,175,236)),('error-url',275,(175,120,740,236))]
def main(source):
 out=ROOT/'assets/screens/chapter07';out.mkdir(parents=True,exist_ok=True)
 originals=out/'source';originals.mkdir(exist_ok=True);z=zipfile.ZipFile(source);records=[]
 for name,n,crop in SPECS:
  root=E.fromstring(z.read(f'ppt/slides/slide{n}.xml'));pic=root.find('.//p:pic',NS);rid=pic.find('.//a:blip',NS).get('{'+NS['r']+'}embed')
  rel={x.get('Id'):x.get('Target') for x in E.fromstring(z.read(f'ppt/slides/_rels/slide{n}.xml.rels'))}
  media=posixpath.normpath('ppt/slides/'+rel[rid]);blob=z.read(media);original=originals/f'slide-{n}.png';original.write_bytes(blob)
  im=Image.open(original);im.crop(crop).save(out/f'{name}.png')
  records.append({'asset':f'assets/screens/chapter07/{name}.png','pptx_slide':n,'pdf_page':n-103,'media':media,'original':str(original.relative_to(ROOT)),'original_sha256':hashlib.sha256(blob).hexdigest(),'original_size':im.size,'crop_xyxy':crop,'operation':'crop only; source pixels and existing highlights unchanged'})
 data={'source_file':source.name,'source_repository':'mrgrit/hack_ir_with_wazuh','source_directory':'slides','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'provenance':'User-supplied slide images; capture method/date not independently verified. Visible records dated 2026-10-31. No new chapter07 screenshots or live experiment results.','assets':records}
 (out/'provenance.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(len(records),'screen crops')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);main(ap.parse_args().source)
