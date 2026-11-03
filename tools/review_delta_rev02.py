"""이전 검수 렌더와 동일한 지면을 구분하고 변경 지면을 원래 크기로 배치한다."""
from pathlib import Path
import json,sys,hashlib
from PIL import Image,ImageDraw
prior,current=map(Path,sys.argv[1:3]);out=current/'delta-sheets';out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
delta=[];pages=[];manifest=[]
for folder in sorted(current.glob('volume01-*')):
 if not folder.is_dir():continue
 same=[];changed=[]
 for p in sorted(folder.glob('page-*.png'),key=lambda p:int(p.stem[5:])):
  n=int(p.stem[5:]);old=prior/folder.name/p.name
  if old.exists() and sha(old)==sha(p):same.append(n)
  else:changed.append(n);pages.append(p)
 delta.append({'document':folder.name,'unchanged':same,'changed':changed})
for i in range(0,len(pages),4):
 group=pages[i:i+4];w,h=Image.open(group[0]).size
 sheet=Image.new('RGB',(w*2,(h+24)*2),'#b8b8b8');draw=ImageDraw.Draw(sheet)
 for j,p in enumerate(group):
  x,y=w*(j%2),(h+24)*(j//2);draw.text((x+6,y+5),p.parent.name+' '+p.stem,fill='black');sheet.paste(Image.open(p),(x,y+24))
 name=f'{i//4+1:03}.png';sheet.save(out/name)
 manifest.append({'sheet':name,'pages':[p.relative_to(current).as_posix() for p in group]})
(current/'visual-delta.json').write_text(json.dumps(delta,indent=2),'utf8')
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),'utf8')
print('unchanged',sum(len(x['unchanged']) for x in delta),'changed',len(pages),'sheets',len(manifest))
