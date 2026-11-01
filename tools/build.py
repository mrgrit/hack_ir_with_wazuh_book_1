"""Build the book preview only. Never execute learner commands."""
from pathlib import Path
import json
from html import escape
ROOT=Path(__file__).resolve().parents[1]
pages=json.loads((ROOT/'manuscript/sample.json').read_text())
css='''
@page { size: 182mm 257mm; margin: 0; }
* { box-sizing:border-box; }
body { margin:0; background:#d9dedf; color:#263449; font-family:"Noto Sans CJK KR","NanumGothic",sans-serif; }
.sheet { width:182mm; height:257mm; padding:13mm 14mm 15mm; margin:8mm auto; background:#fffdf8; position:relative; break-after:page; }
.sheet:last-child {break-after:auto}
.content { height:224mm; }
.eyebrow { font-size:9pt; color:#287f78; letter-spacing:.04em; margin:0 0 4mm; border-top:3px solid #263449; padding-top:3mm; }
h1 {font-size:21pt; line-height:1.35; margin:0 0 5mm; letter-spacing:-.04em}
h3 {font-size:12pt; margin:4mm 0 2mm}
p,li,td,th {font-size:10.5pt; line-height:1.75; word-break:keep-all; overflow-wrap:anywhere;}
p {margin:3mm 0} ul,ol {padding-left:6mm; margin:3mm 0;} li {margin-bottom:2mm}
pre {white-space:pre-wrap; overflow-wrap:anywhere; word-break:break-all; background:#eef3f4; border-left:3px solid #426b9b; padding:3mm; margin:2mm 0; font-size:10pt; line-height:1.6;}
code {font-family:"DejaVu Sans Mono","Noto Sans CJK KR",monospace; font-size:.93em;}
pre code {font-size:inherit}
aside {font-size:10pt; line-height:1.65; background:#f4ebdd; padding:3mm; border-left:3px solid #b96c24; margin:3mm 0;}
.file {font-size:8pt; color:#5c6976; margin:0 0 2mm;}
figure {margin:4mm 0} .screen {width:100%; overflow:hidden; border:1px solid #c7d0d5; background:white;}
.screen img {width:100%; display:block; max-width:none;}
.screen.detail img {width:250mm;}
figcaption {font-size:9pt; line-height:1.6; margin-top:2mm; color:#4e5b69;}
.diagram {display:block; width:100%; margin:5mm 0; image-rendering:pixelated;}
table {width:100%; border-collapse:collapse; margin:4mm 0;} td,th {text-align:left; border-bottom:1px solid #c8d1d4; padding:2mm; vertical-align:top;} th {background:#edf2f1}
footer {position:absolute; bottom:7mm; left:14mm; right:14mm; display:flex; justify-content:space-between; font-size:8pt; color:#687581;}
a {color:#426b9b}
@media print {body {background:white} .sheet {margin:0; box-shadow:none;}}
'''
text='<!doctype html><html lang="ko"><meta charset="utf-8"><title>해킹·침해대응 실무 with Wazuh — 1권 시범 원고</title><style>'+css+'</style><body>'
for n,page in enumerate(pages,1):
 text+=f'<section class="sheet" id="page-{n}"><div class="content"><div class="eyebrow">{escape(page["section"])}</div><h1>{page["title"]}</h1>{page["body"]}</div><footer><span>해킹·침해대응 실무 with Wazuh · 시범 원고</span><span>{n:02}</span></footer></section>'
text+='</body></html>'
(ROOT/'preview.html').write_text(text)
print('preview.html:',len(pages),'pages')
