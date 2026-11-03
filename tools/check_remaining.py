"""11장·부록 원고와 복사용 자료의 정적 검사. 실습 입력을 실행하지 않는다."""
import argparse,csv,hashlib,json,re,subprocess,zipfile
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
def norm(t):return re.sub(r'\s+','',t)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(path.read_text('utf-8-sig'))
def validate(name,pdf_path):
    path=ROOT/f'manuscript/volume01-{name}.docx'
    doc=Document(path);data=load(path.with_suffix('.json'))
    body=norm(''.join(doc.element.body.xpath('.//w:t/text()')))
    pdf=PdfReader(pdf_path);pdf_text=norm('\n'.join(p.extract_text() or '' for p in pdf.pages))
    assets=[];urls=[];ids=[]
    for pg in data['pages']:
        assert norm(pg['title']) in body,pg['title']
        for b in pg['blocks']:
            if b['type']=='image':
                assets.append(sha(ROOT/b['path']))
                assert norm(b['caption']) in body,b['caption']
            elif b['type']=='table':
                for row in [b['head']]+b['rows']:
                    for cell in row:assert norm(str(cell)) in body,cell
            else:
                assert norm(b['text']) in body,b['text'][:90]
            if b['type']=='link':
                urls.append(b['url']);assert norm(b['url']) in pdf_text,b['url']
            if b.get('id'):
                ids.append(b['id'])
                assert (ROOT/'examples/chapter11'/(b['id']+'.txt')).read_text('utf8').rstrip('\n')==b['text'],b['id']
    embedded=[hashlib.sha256(doc.part.related_parts[n.get(qn('r:embed'))].blob).hexdigest() for n in doc.element.body.xpath('.//a:blip')]
    assert embedded==assets,'image bytes/order mismatch'
    for node in doc.element.body.iter():
        for k,v in node.attrib.items():
            if k in (qn('r:id'),qn('r:embed'),qn('r:link')):assert v in doc.part.rels,v
    template=Document(ROOT/'tools/assets/bookk-B5.docx').sections[0]
    dimensions=['page_width','page_height','top_margin','bottom_margin','left_margin','right_margin','gutter']
    for sec in doc.sections:
        for key in dimensions:assert getattr(sec,key)==getattr(template,key),key
    fonts=sorted({v for n in doc.element.body.xpath('.//w:rFonts') for k,v in n.attrib.items() if k in (qn('w:ascii'),qn('w:hAnsi'),qn('w:eastAsia'))})
    assert set(fonts)<={'Consolas','부크크 명조 Light','부크크 고딕 Light'},fonts
    assert doc.paragraphs[0].style.name=='Title'
    colors={n.get(qn('w:val')) for n in doc.element.body.xpath('.//w:color')}
    assert colors<={'000000','auto'},colors
    with zipfile.ZipFile(path) as z,zipfile.ZipFile(ROOT/'tools/assets/bookk-B5.docx') as base:
        assert z.read('word/theme/theme1.xml')==base.read('word/theme/theme1.xml')
    return {'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'pages':len(pdf.pages),'images':len(assets),'input_ids':ids,'full_urls':urls,'fonts':fonts,'geometry_mm':{k:round(getattr(doc.sections[0],k).mm,2) for k in dimensions},'template_theme_matches':True,'text_images_links_pass':True}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chapter11_pdf',type=Path);parser.add_argument('appendices_pdf',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'build/volume01-final/remaining-validation.json')
    args=parser.parse_args();docs=[validate('chapter11',args.chapter11_pdf),validate('appendices',args.appendices_pdf)]
    queries=[]
    for i,(ch,q) in enumerate([(8,5),(9,3),(9,4),(10,2),(10,4),(10,5)],1):
        a=ROOT/f'examples/chapter11/Q11-{i:02}.txt';b=ROOT/f'examples/chapter{ch:02}/Q{ch:02}-{q:02}.txt'
        assert a.read_text('utf8')==b.read_text('utf8'),(a,b)
        queries.append({'current':a.name,'source':b.relative_to(ROOT).as_posix()})
    manifest=load(ROOT/'examples/chapter11/evidence/manifest.json')
    for row in manifest['files']:
        current=ROOT/'examples/chapter11/evidence'/row['file'];source=ROOT/row['source']
        assert sha(current)==row['sha256']
        original_blob=subprocess.run(['git','show',row['source_commit']+':'+row['source']],cwd=ROOT,capture_output=True,check=True).stdout
        assert hashlib.sha256(original_blob).hexdigest()==row['source_sha256']
        assert source.read_text('utf8').replace('\r\n','\n')==original_blob.decode('utf8').replace('\r\n','\n')
        originals=load(source)
        for event in load(current):assert {k:v for k,v in event.items() if k not in ('evidence_id','source_chapter')} in originals
    with (ROOT/'examples/appendices/example-index.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    expected={}
    for chapter in range(1,12):
        for pg in load(ROOT/f'manuscript/volume01-chapter{chapter:02}.json')['pages']:
            for b in pg['blocks']:
                if b.get('id'):expected[(str(chapter),b['id'])]=b
    assert len(rows)==len(expected)==451
    for row in rows:
        b=expected[(row['장'],row['번호'])];assert row['입력']==b.get('text','')
        assert row['입력 위치']==b.get('where','')
        file=row['복사용 파일']
        if file!='각 장 README 참조':assert (ROOT/file).is_file(),file
        else:assert (ROOT/f"examples/chapter{int(row['장']):02}/README.md").is_file()
    appendix=load(ROOT/'manuscript/volume01-appendices.json')
    coverage=[]
    for pg in appendix['pages']:
        if pg['title'].startswith(('F.1','F.2')):
            for b in pg['blocks']:
                if b['type']=='table':coverage.extend(int(row[0].split(' · ')[0]) for row in b['rows'])
    assert sorted(coverage)==list(range(1,31))+[62]
    checks=load(ROOT/'editorial/evidence/chapter11/2026-11-03/powershell-checks.json')
    assert len(checks)==5
    for item in checks:
        assert item['input'].replace('\r\n','\n')==(ROOT/'examples/chapter11'/(item['id']+'.txt')).read_text('utf8')
    assert re.search(r'srcport\s+: 42688',checks[-1]['result'])
    prior=[f'manuscript/volume01-chapter{n:02}.{ext}' for n in range(1,11) for ext in ('docx','json')]
    tracked=subprocess.run(['git','ls-files','-z'],cwd=ROOT,check=True,capture_output=True).stdout.decode('utf8').split('\0')
    rev01=[p for p in tracked if 'rev01' in p.lower()]
    subprocess.run(['git','diff','--exit-code','HEAD','--',*prior,*rev01],cwd=ROOT,check=True,capture_output=True)
    result={'date':'2026-11-03','scope':'11장과 부록의 별도 DOCX. 합본 제외.','documents':docs,'reused_queries':queries,'local_powershell_verified_inputs':len(checks),'evidence_records':[x['records'] for x in manifest['files']],'example_index_rows':len(rows),'module01_exercises':sorted(coverage),'existing_chapters_and_REV01_unchanged':True}
    args.output.parent.mkdir(exist_ok=True,parents=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
