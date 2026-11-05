"""REV01 정적 검사. 사용: python3 tools/check_rev01.py volume01-chapter05:chapter05:<렌더한 PDF> ...
명령↔예제 파일 일치, bash -n, 줄 길이 60, 판형·테마·글꼴·색, 빈 쪽, 금지 표현을 확인한다."""
import json,re,subprocess,sys
from pathlib import Path
from zipfile import ZipFile
from docx import Document
from docx.oxml.ns import qn
import pymupdf
R=Path(__file__).resolve().parents[1]
for name,ex,pdf in [(a.split(':')[0],a.split(':')[1],a.split(':')[2]) for a in sys.argv[1:]]:
    data=json.loads((R/f'manuscript/REV01/{name}.json').read_text())
    cmds=[b for pg in data['pages'] for b in pg['blocks'] if b['type']=='command']
    mf=R/f'examples/rev01/{ex}/manifest.json';man=json.loads(mf.read_text()) if mf.exists() else []
    assert cmds==man,name
    for b in cmds:
        assert (R/f'examples/rev01/{ex}/{b["id"]}.txt').read_text()==b['text']+'\n',b['id']
        subprocess.run(['bash','-n'],input=b['text'],text=True,check=True,capture_output=True)
        assert not re.search(r'docker\s+exec\s+(?!-it)',b['text'])
        assert max(len(l) for l in b['text'].splitlines())<=60,(b['id'],b['text'])
    d=Document(R/f'manuscript/REV01/{name}.docx');src=Document(R/'tools/assets/bookk-B5.docx')
    for tag in ['w:pgSz','w:pgMar']:
        assert dict(d.sections[0]._sectPr.find(qn(tag)).attrib)==dict(src.sections[0]._sectPr.find(qn(tag)).attrib)
    with ZipFile(R/f'manuscript/REV01/{name}.docx') as z, ZipFile(R/'tools/assets/bookk-B5.docx') as base:
        assert z.read('word/theme/theme1.xml')==base.read('word/theme/theme1.xml')
        xml=z.read('word/document.xml').decode()
        for f in ['부크크 명조 Light','부크크 고딕 Light','Consolas']:assert f in xml
        assert all(c=='000000' for c in re.findall(r'<w:color w:val="([^"]+)"',xml))
    doc=pymupdf.open(pdf);sparse=[]
    for i,pg in enumerate(doc,1):
        t=pg.get_text().strip();imgs=len(pg.get_images())
        if len(t)<150 and imgs==0: sparse.append((i,len(t),t[:40].replace('\n',' ')))
    # forbidden phrasing per AGENTS.md
    txt=' '.join(b.get('text','') if isinstance(b.get('text',''),str) else '' for pg in data['pages'] for b in pg['blocks'])
    bad=[w for w in ['이 장은','이 장에서는','마치 ','처럼 생각'] if w in txt]
    print(name,'cmds',len(cmds),'pages',len(doc),'sparse',sparse,'banned',bad)
print('OK')
