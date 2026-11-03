"""렌더된 지면을 축소하지 않고 2×2 검사 판에 배치한다."""
from PIL import Image
from pathlib import Path
import sys
root=Path(sys.argv[1]); dest=root/'sheets'; dest.mkdir(exist_ok=True)
for folder in sorted(root.glob('volume01-*')):
    if not folder.is_dir(): continue
    pages=sorted(folder.glob('page-*.png'),key=lambda p:int(p.stem[5:]))
    for i in range(0,len(pages),4):
        chosen=pages[i:i+4];w,h=Image.open(chosen[0]).size
        sheet=Image.new('RGB',(w*2,h*2),'#b8b8b8')
        for j,p in enumerate(chosen):sheet.paste(Image.open(p),(w*(j%2),h*(j//2)))
        sheet.save(dest/f'{folder.name}_{i+1:03}-{i+len(chosen):03}.png')
print(len(list(dest.glob('*.png'))),'unscaled sheets')
