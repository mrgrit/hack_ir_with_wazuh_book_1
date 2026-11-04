"""REV03 1장과 설치 부록에서 번호별 복사용 입력과 색인을 갱신한다."""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'examples/rev03/chapter01'
OUT.mkdir(parents=True, exist_ok=True)
rows = {}
for name in ['manuscript/REV02/volume01-appendix-a.json', 'manuscript/REV03/volume01-chapter01.json']:
    data = json.loads((ROOT / name).read_text('utf8'))
    for page in data['pages']:
        for block in page['blocks']:
            if block['type'] == 'command' and block['id'].startswith('C01-'):
                rows[block['id']] = {'document': name, 'section': page['title'], **block}
for ident, row in rows.items():
    row['file'] = 'examples/rev03/chapter01/' + ident + '.txt'
    (ROOT / row['file']).write_text(row['text'] + '\n', 'utf8')
ordered = [rows[key] for key in sorted(rows)]
(OUT / 'input-index.json').write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + '\n', 'utf8')
with (OUT / 'input-index.csv').open('w', encoding='utf-8-sig', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=['id', 'document', 'section', 'where', 'file'], extrasaction='ignore')
    writer.writeheader()
    writer.writerows(ordered)
print(len(ordered), 'inputs synchronized')
