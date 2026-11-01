"""저자용 무실행 검사: 복사용 명령·DOCX 판형·조판 결과를 검증한다."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile
from docx import Document
from docx.oxml.ns import qn
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
def compact(s):return re.sub(r'\s+','',s)
def main(pdf):
    data=json.loads((ROOT/'manuscript/volume01-chapter01.json').read_text())
    cmds=[b for pg in data['pages'] for b in pg['blocks'] if b['type']=='command']
    assert cmds==json.loads((ROOT/'examples/chapter01/manifest.json').read_text())
    assert len(list((ROOT/'examples/chapter01').glob('C01-*.txt')))==len(cmds)
    for b in cmds:
        assert (ROOT/'examples/chapter01'/f"{b['id']}.txt").read_text()==b['text']+'\n', b['id']
        subprocess.run(['bash','-n'],input=b['text'],text=True,check=True,capture_output=True)
        assert not re.search(r'docker\s+exec\s+(?!-it)',b['text'])
    d=Document(ROOT/'manuscript/volume01-chapter01.docx')
    src=Document(ROOT/'tools/assets/bookk-B5.docx')
    assert len(d.sections)==1
    for tag in ['w:pgSz','w:pgMar']:
        assert dict(d.sections[0]._sectPr.find(qn(tag)).attrib)==dict(src.sections[0]._sectPr.find(qn(tag)).attrib)
    with ZipFile(ROOT/'manuscript/volume01-chapter01.docx') as z, ZipFile(ROOT/'tools/assets/bookk-B5.docx') as base:
        assert z.read('word/theme/theme1.xml')==base.read('word/theme/theme1.xml')
        xml=z.read('word/document.xml').decode()
        for f in ['부크크 명조 Light','부크크 고딕 Light','Consolas']:assert f in xml
        assert all(c=='000000' for c in re.findall(r'<w:color w:val="([^"]+)"',xml))
    rendered=pymupdf.open(pdf)
    assert len(rendered)==len(data['pages']),f"Unexpected pagination: {len(rendered)} vs {len(data['pages'])}"
    for page,pg in zip(rendered,data['pages']):
        txt=compact(page.get_text())
        assert compact(pg['title']) in txt,pg['title']
        for b in pg['blocks']:
            if b['type']=='command':
                for key in ['id','text','why','result']:
                    assert compact(b[key]) in txt,(b['id'],key,'not wholly on expected page')
        # 본문 영역의 넘침을 검사한다. 좌우 여백은 맞쪽에서 뒤바뀐다.
        for block in page.get_text('dict')['blocks']:
            if block['type']!=0:continue
            for line in block['lines']:
                for span in line['spans']:
                    if span['bbox'][1]>660:continue # footer
                    assert span['bbox'][1]>=77 and span['bbox'][3]<=625,span
                    assert span['bbox'][0]>=75 and span['bbox'][2]<=460,span
    report={'docx_pages':len(rendered),'command_files':len(cmds),'command_syntax':'bash -n only; not executed','template_page_size_and_margins_inherited':True,'template_theme_identical':True,'all_primary_commands_and_explanations_on_same_page':True,'body_text_within_page_bounds':True}
    (ROOT/'editorial/chapter01-layout-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('pdf',type=Path);main(ap.parse_args().pdf)
