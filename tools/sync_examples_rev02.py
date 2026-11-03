"""최종 원고의 입력과 해설을 REV02 예제 색인에 동기화한다.

관찰 데이터와 chapter11/evidence/manifest.json은 변경하지 않는다.
"""
from pathlib import Path
import json, csv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'examples/rev02'

def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

def main():
    previous = {row['id']:row for row in json.loads((OUT / 'input-index.json').read_text('utf8'))}
    blocks = {}
    locations = {}
    for src in sorted((ROOT / 'manuscript/REV02').glob('*.json')):
        for page in json.loads(src.read_text('utf8'))['pages']:
            for block in page['blocks']:
                if block['type'] in ('command', 'query'):
                    if block['id'] in blocks:
                        raise ValueError('duplicate input id: '+block['id'])
                    blocks[block['id']] = block
                    locations[block['id']] = (src.name, page['title'])
    index = []
    for ident, block in blocks.items():
        folder = 'appendix-a' if ident.startswith('CA-') else 'chapter'+ident[1:3]
        item = dict(previous.get(ident, {'id':ident, 'file':f'examples/rev02/{folder}/{ident}.txt'}))
        item['where'] = block['where']
        item['document'], item['section'] = locations[ident]
        (ROOT/item['file']).parent.mkdir(parents=True,exist_ok=True)
        index.append(item)
    groups = {}
    for item in index:
        item['text']=blocks[item['id']]['text']
        item['document'], item['section'] = locations[item['id']]
        (ROOT/item['file']).write_text(item['text']+'\n',encoding='utf8')
        folder = Path(item['file']).parent.name
        groups.setdefault(folder, []).append(item)
    for folder, rows in groups.items():
        base = OUT / folder
        write(base / 'rev02-inputs.json', rows)
        final = [blocks[row['id']] for row in rows]
        if (base / 'manifest.json').exists():
            write(base / 'manifest.json', final)
        if (base / 'queries.json').exists():
            write(base / 'queries.json', [b for b in final if b['type'] == 'query'])
        if (base / 'commands.txt').exists():
            chunks = ['REV02 복사용 입력 — 본문의 선행 조건과 원상복구 절차를 확인하고 한 블록씩 사용한다.']
            for b in final:
                chunks.append('\n'.join([
                    f"[{b['id']}] {b['where']}",
                    b.get('purpose', b.get('why', '')),
                    b.get('syntax', ''), b['text'], '확인: ' + b['result']
                ]))
            (base / 'commands.txt').write_text('\n\n'.join(chunks) + '\n', 'utf8')
    write(OUT/'input-index.json',index)
    with (OUT/'input-index.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['document','section','id','where','file'],extrasaction='ignore')
        writer.writeheader();writer.writerows(index)
    for browser in OUT.glob('*/browser-inputs.json'):
        rows=json.loads(browser.read_text('utf8'))
        for row in rows:
            target=browser.parent/row['file']
            if target.exists():row['text']=target.read_text('utf8').rstrip('\n')
        write(browser,rows)
    (OUT / 'appendices/example-index.csv').write_bytes((OUT / 'input-index.csv').read_bytes())
    print(f'{len(index)} inputs; {len(groups)} directories synchronized')

if __name__ == '__main__':
    main()
