"""REV03 1장의 본문·복사용 입력·DOCX 자산·렌더를 정적으로 대조한다.

실습 명령은 실행하지 않는다. Bash에는 -n으로 구문만 검사하도록 전달한다.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import shutil
import zipfile
from docx import Document
from docx.oxml.ns import qn
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('render', nargs='?', default='build/REV03/chapter01/render-styled2')
parser.add_argument('--check-baseline', action='store_true', help='교정 당시 로컬 작업 파일의 보존 여부도 검사한다.')
args = parser.parse_args()
RENDER = ROOT / args.render
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
norm = lambda s: re.sub(r'\s+', '', s.replace('**', ''))
source = ROOT / 'manuscript/REV03/volume01-chapter01.json'
docpath = source.with_suffix('.docx')
data = json.loads(source.read_text('utf8'))
blocks = [b for page in data['pages'] for b in page['blocks']]
doc = Document(docpath)
xmltext = ''.join(doc.element.body.xpath('.//w:t/text()'))
flat = norm(xmltext)
checks = {}
for page in data['pages']:
    assert norm(page['title']) in flat, page['title']
    for b in page['blocks']:
        atoms = []
        for key in ['text', 'caption', 'title', 'purpose', 'syntax', 'result', 'where', 'url']:
            value = b.get(key)
            if isinstance(value, str): atoms.append(value)
            elif isinstance(value, list): atoms.extend(value)
        atoms.extend(b.get('items', []))
        atoms.extend(b.get('head', []))
        atoms.extend(str(v) for row in b.get('rows', []) for v in row)
        for atom in atoms: assert norm(atom) in flat, atom
checks['source_text_in_docx'] = True

sections = [p['title'].split()[0] for p in data['pages'] if re.match(r'^1\.\d+ ', p['title'])]
assert sections == ['1.' + str(i) for i in range(1, 10)]
checks['sections'] = sections
inputs = json.loads((ROOT / 'examples/rev03/chapter01/input-index.json').read_text('utf8'))
assert [r['id'] for r in inputs] == [f'C01-{i:02}' for i in range(1, 29)]
bash = shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe'
for row in inputs:
    text = (ROOT / row['file']).read_text('utf8')
    assert text == row['text'] + '\n', row['id']
    origin = json.loads((ROOT / row['document']).read_text('utf8'))
    matches = [b for p in origin['pages'] for b in p['blocks'] if b.get('id') == row['id']]
    assert len(matches) == 1 and matches[0]['text'] == row['text'], row['id']
    assert row['where'] and row['result'] and (row.get('purpose') or row.get('why'))
    result = subprocess.run([str(bash), '-n'], input=text, text=True, encoding='utf8', capture_output=True)
    assert result.returncode == 0, (row['id'], result.stderr)
checks['copy_inputs_and_bash_syntax'] = len(inputs)

with zipfile.ZipFile(docpath) as z:
    embedded = {hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')}
images = [b for b in blocks if b['type'] == 'image']
for b in images: assert sha(ROOT / b['path']) in embedded, b['path']
assert len(doc.inline_shapes) == len(images) == 16
checks['embedded_image_hashes'] = [{'path': b['path'], 'sha256': sha(ROOT / b['path'])} for b in images]
screens = 0
for shape, b in zip(doc.inline_shapes, images):
    if b['path'].startswith('assets/screens/') or b.get('role') == 'screenshot':
        outline = shape._inline.xpath('.//pic:spPr/a:ln')
        assert len(outline) == 1 and outline[0].get('w') == '6350', b['path']
        assert outline[0].find(qn('a:solidFill')).find(qn('a:srgbClr')).get('val') == '666666'
        screens += 1
checks['outlined_screenshots'] = screens
assert screens == 4

styled_inputs = []
for p in doc.paragraphs:
    shade = p._p.xpath('./w:pPr/w:shd')
    if shade and shade[0].get(qn('w:fill')) == 'F4F4F4':
        left = p._p.xpath('./w:pPr/w:pBdr/w:left')
        assert len(left) == 1 and left[0].get(qn('w:sz')) == '16'
        assert round(p.paragraph_format.left_indent.mm) == 3
        assert round(p.paragraph_format.right_indent.mm) == 3
        assert all(r.font.name == 'Consolas' and r.font.size.pt == 10 for r in p.runs if r.text)
        styled_inputs.append(p.text)
assert len(styled_inputs) == sum(b['type'] in ('command', 'query') for b in blocks)
checks['styled_command_query_blocks'] = len(styled_inputs)

tables = [t for t in doc.tables if len(t.columns) > 1]
assert len(tables) == sum(b['type'] == 'table' for b in blocks)
for t in tables:
    for c in t.rows[0].cells:
        assert c._tc.get_or_add_tcPr().find(qn('w:shd')).get(qn('w:fill')) == 'E7E7E7'
        assert int(c.vertical_alignment) == 1
        assert all(int(p.alignment) == 1 for p in c.paragraphs)
        assert all(r.bold is True for p in c.paragraphs for r in p.runs if r.text)
checks['shaded_centered_bold_table_headers'] = len(tables)
section = doc.sections[0]
assert round(section.page_width.mm) == 188 and round(section.page_height.mm) == 263
checks['page_mm'] = [round(section.page_width.mm), round(section.page_height.mm)]
checks['body_mm'] = [round(section.page_width.mm - section.left_margin.mm - section.right_margin.mm - section.gutter.mm), round(section.page_height.mm - section.top_margin.mm - section.bottom_margin.mm)]
assert checks['body_mm'] == [127, 192]

if args.check_baseline:
    baseline = json.loads((ROOT / 'editorial/REV03/chapter01-baseline.json').read_text('utf8'))
    for f in baseline['files']: assert sha(ROOT / f['path']) == f['sha256'], f['path']
    checks['preserved_baseline_files'] = len(baseline['files'])
render_index = json.loads((RENDER / 'render-index.json').read_text('utf8'))[0]
assert not render_index['overflow'], render_index
pages = json.loads((RENDER / 'volume01-chapter01/page-text.json').read_text('utf8'))
# PDFium은 Word PDF의 줄 끝 하이픈을 U+FFFE로 추출할 수 있다.
# 실제 인쇄 문자열 대조에는 하이픈을 보존하는 pypdf를 사용한다.
render_text = norm(''.join(p.extract_text() for p in PdfReader(RENDER / 'volume01-chapter01.pdf').pages))
urls = [b['url'] for b in blocks if b['type'] == 'link']
for url in urls: assert norm(url) in render_text, url
checks['printed_full_reference_urls'] = urls
checks['render_pages'] = len(pages)
checks['lateral_overflow_pages'] = 0
checks['docx_sha256'] = sha(docpath)
checks['source_sha256'] = sha(source)
assert not list((ROOT / 'manuscript/REV03').glob('*.pdf'))
(ROOT / 'editorial/REV03/chapter01-validation.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2) + '\n', 'utf8')
print(json.dumps({k: v for k, v in checks.items() if k != 'embedded_image_hashes'}, ensure_ascii=False, indent=2))
