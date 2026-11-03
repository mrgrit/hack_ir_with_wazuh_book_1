from pathlib import Path
import json,sys
import pypdfium2 as pdfium
root=Path(sys.argv[1]);summary=[]
for f in sorted(root.glob('*.pdf')):
    doc=pdfium.PdfDocument(str(f));out=root/f.stem;out.mkdir(exist_ok=True)
    pages=[]
    for i in range(len(doc)):
        p=doc[i];tp=p.get_textpage();text=tp.get_text_range()
        image=p.render(scale=1.5).to_pil();image.save(out/f'page-{i+1}.png')
        # Body rectangle of inherited first B5 section. Header/footer excluded.
        overflow=[]
        for j in range(tp.count_chars()):
            ch=tp.get_text_range(j,1)
            if not ch.strip():continue
            left,bottom,right,top=tp.get_charbox(j)
            if right>473 or left<77:overflow.append(ch)
        pages.append({'page':i+1,'characters':len(text),'lateral_overflow':''.join(overflow),'text':text})
    (out/'page-text.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),'utf8')
    summary.append({'file':f.name,'pages':len(doc),'sparse':[x['page'] for x in pages if x['characters']<160],'overflow':[{'page':x['page'],'text':x['lateral_overflow']} for x in pages if x['lateral_overflow']]})
    print(f.stem,len(doc),flush=True)
(root/'render-index.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),'utf8')
