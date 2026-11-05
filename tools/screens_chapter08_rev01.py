"""REV01 8장 화면 자르기. 2026-11-02 실제 Discover 화면(editorial/evidence/chapter08/2026-11-02)에서 영역만 잘라 낸다."""
import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'editorial/evidence/chapter08/2026-11-02'
OUT=ROOT/'assets/screens/chapter08'
CROPS={'rev01-histogram':('Q08-01-query.png',(275,140,1295,405)),
       'rev01-pivot':('Q08-05-query.png',(275,140,1295,880))}
prov=[]
for name,(src,box) in CROPS.items():
    p=SRC/src;Image.open(p).crop(box).save(OUT/(name+'.png'))
    prov.append({'asset':f'assets/screens/chapter08/{name}.png','original':str(p.relative_to(ROOT)),
                 'original_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'crop_xyxy':list(box)})
(OUT/'rev01-provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=1)+'\n')
print(len(prov),'crops')
