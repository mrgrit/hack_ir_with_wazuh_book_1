"""7장 문서·예제·화면 출처의 정적 검사. 공격 요청이나 DQL을 실행하지 않는다."""
import argparse,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from docx import Document
from PIL import Image,ImageChops
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
def check(docx,pdf,bash=None):
    data=json.loads((ROOT/'manuscript/volume01-chapter07.json').read_text(encoding='utf-8'))
    blocks=[b for p in data['pages'] for b in p['blocks']]
    doc=Document(docx);base=Document(ROOT/'tools/assets/bookk-B5.docx')
    geometry=['page_width','page_height','left_margin','right_margin','top_margin','bottom_margin','gutter']
    assert all(getattr(doc.sections[0],k)==getattr(base.sections[0],k) for k in geometry)
    with zipfile.ZipFile(docx) as z,zipfile.ZipFile(ROOT/'tools/assets/bookk-B5.docx') as ref:
        assert z.read('word/theme/theme1.xml')==ref.read('word/theme/theme1.xml')
        assert b'ghp_' not in z.read('word/document.xml')
    manifest=[]
    for b in blocks:
        if b['type'] in ('command','query'):
            raw=(ROOT/'examples/chapter07'/f"{b['id']}.txt").read_text(encoding='utf-8').rstrip('\n')
            assert raw==b['text'],b['id']
            if b['type']=='command' and bash:
                r=subprocess.run([str(bash),'--noprofile','--norc','-n'],input=raw,text=True,capture_output=True)
                assert r.returncode==0,(b['id'],r.stderr)
            manifest.append(b['id'])
        if b['type']=='image': assert (ROOT/b['path']).is_file(),b['path']
    inputs=json.loads((ROOT/'examples/chapter07/browser-inputs.json').read_text(encoding='utf-8'))
    for b in inputs:
        assert (ROOT/'examples/chapter07'/b['file']).read_text(encoding='utf-8')==b['text'].rstrip('\n')+'\n',b['file']
        assert any(x['type']=='code' and x['text']==b['text'] for x in blocks),b['file']
    assert len(doc.inline_shapes)==sum(b['type']=='image' for b in blocks)
    provenance=json.loads((ROOT/'assets/screens/chapter07/provenance.json').read_text(encoding='utf-8'))
    for b in provenance['assets']:
        original=ROOT/b['original'];assert hashlib.sha256(original.read_bytes()).hexdigest()==b['original_sha256']
        expected=Image.open(original).crop(b['crop_xyxy']).convert('RGB');actual=Image.open(ROOT/b['asset']).convert('RGB')
        assert expected.size==actual.size and ImageChops.difference(expected,actual).getbbox() is None,b['asset']
    r=PdfReader(pdf);text='\n'.join(pg.extract_text() for pg in r.pages);compact=re.sub(r'\s+','',text)
    for b in blocks:
        if b['type']=='link':assert re.sub(r'\s+','',b['url']) in compact,b['url']
    font_names=sorted({str(v.get_object().get('/BaseFont')) for p in r.pages for v in p['/Resources'].get('/Font',{}).values()})
    assert any('BookkMyungjo-Lt' in x for x in font_names)
    assert any('BookkGothic-Lt' in x for x in font_names)
    assert any('Consolas' in x for x in font_names)
    result={'pages':len(r.pages),'geometry_mm':{k:round(getattr(doc.sections[0],k).mm,2) for k in geometry},'commands':sum(b['type']=='command' for b in blocks),'DQL':sum(b['type']=='query' for b in blocks),'screens':len(provenance['assets']),'images_inserted':len(doc.inline_shapes),'source_pixel_integrity':True,'template_theme_equal':True,'copy_parity':True,'browser_file_input_parity':True,'full_reference_urls':True,'bash_syntax_only':bool(bash),'fonts':font_names,'page_text_lengths':[len(p.extract_text()) for p in r.pages],'live_attacks_executed':False,'live_DQL_executed':False}
    print(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('docx',type=Path);ap.add_argument('pdf',type=Path);ap.add_argument('--bash',type=Path);ap.add_argument('--output',type=Path);a=ap.parse_args();result=check(a.docx,a.pdf,a.bash)
    if a.output:a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
