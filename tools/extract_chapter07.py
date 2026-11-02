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
 # XML part numbers are not presentation-order slide numbers in this deck.
 rels={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
 order=[posixpath.normpath('ppt/'+rels[x.get('{'+NS['r']+'}id')]) for x in E.fromstring(z.read('ppt/presentation.xml')).findall('.//p:sldId',NS)]
 for rec in records:
  part=f"ppt/slides/slide{rec['pptx_slide']}.xml"
  rec['slide_xml_part']=part;rec['slide_number']=order.index(part)+1
  del rec['pptx_slide'];del rec['pdf_page']
 # Additional response excerpts are crops of the supplied slide pictures, never new UI.
 for name,number,crop in [('file-response',120,(20,225,850,380)),('union-response',160,(20,230,400,277)),('error-series-a',168,(20,280,720,325)),('error-series-b',168,(720,280,1435,325))]:
  part=order[number-1];root=E.fromstring(z.read(part));pic=root.find('.//p:pic',NS)
  rid=pic.find('.//a:blip',NS).get('{'+NS['r']+'}embed')
  relpart=posixpath.dirname(part)+'/_rels/'+posixpath.basename(part)+'.rels'
  rel={x.get('Id'):x.get('Target') for x in E.fromstring(z.read(relpart))}
  media=posixpath.normpath(posixpath.dirname(part)+'/'+rel[rid]);blob=z.read(media)
  original=originals/f'deck-slide-{number}.png';original.write_bytes(blob)
  im=Image.open(original);im.crop(crop).save(out/f'{name}.png')
  records.append({'asset':f'assets/screens/chapter07/{name}.png','slide_number':number,'slide_xml_part':part,'media':media,'original':str(original.relative_to(ROOT)).replace('\\','/'),'original_sha256':hashlib.sha256(blob).hexdigest(),'original_size':im.size,'crop_xyxy':crop,'operation':'crop only; source pixels unchanged'})
 data={'source_file':'Module01_Wazuh_위협탐지_DQL.pptx','source_url':'https://docs.google.com/presentation/d/1o0H_2DDHBp8p2HvlSnEPbx6-jdURYzew/edit','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'provenance':'Provided slide evidence dated 2026-10-31; original capture method not independently verified. No new attack execution or UI capture in the 2026-11-02 rewrite. slide_number is presentation order, not the XML part number.','assets':records}
 (out/'provenance.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(len(records),'screen crops')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('source',type=Path);main(ap.parse_args().source)
