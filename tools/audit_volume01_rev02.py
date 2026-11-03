from pathlib import Path
import json,re,hashlib,zipfile,collections
from lxml import etree as E
from revise_volume01_rev02 import ROOT,OUT,ED
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
def audit():
    issues=[];counts={};media={};ids=[];texts=[]
    for src in sorted(OUT.glob('*.json')):
        d=json.loads(src.read_text('utf8'));bs=[b for p in d['pages'] for b in p['blocks']]
        counts[src.name]=dict(collections.Counter(b['type'] for b in bs))
        z=zipfile.ZipFile(src.with_suffix('.docx'));x=E.fromstring(z.read('word/document.xml'));flat=''.join(x.xpath('//w:t/text()',namespaces=ns))
        # Original byte strings remain in XML even when Word wraps the display.
        for b in bs:
            if b['type'] in ['command','query']:
                ids.append(b['id']);folder='appendix-a' if b['id'].startswith('CA-') else f'chapter{b["id"][1:3]}'
                f=ROOT/'examples/rev02'/folder/(b['id']+'.txt')
                if not f.exists() or f.read_text('utf8').rstrip('\n')!=b['text']:issues.append([src.name,'input mismatch',b['id']])
            if b['type']=='image':
                p=ROOT/b['path']
                if not p.exists():issues.append([src.name,'missing image',str(p)]);continue
                sha=hashlib.sha256(p.read_bytes()).hexdigest()
                hashes=[hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')]
                if sha not in hashes:issues.append([src.name,'unmatched media',b['path']])
                media[b['path']]=sha
            if b['type']=='link' and b['url'] not in flat:issues.append([src.name,'incomplete URL',b['url']])
            for k in ['text','why','purpose','syntax','result','caption']:
                v=b.get(k)
                if isinstance(v,str) and v.replace('**','').replace('\n','') not in flat.replace('\n',''):issues.append([src.name,'missing text',k,v[:60]])
            if b['type']=='p':
                for word in ['슬라이드','촬영','Module 01','검증 환경','다음 페이지','다음 쪽','1.12','1.11의','이 장은','원고']:
                    if word in b['text']:issues.append([src.name,'editorial wording',b['text']])
        for sect in x.findall('.//w:sectPr',ns):
            size=sect.find('w:pgSz',ns)
            if size.get('{'+ns['w']+'}w')!='10660' or size.get('{'+ns['w']+'}h')!='14912':issues.append([src.name,'page size'])
    baseline=json.loads((ED/'source-baseline.json').read_text('utf8'))
    for f in baseline:
        if hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()!=f['sha256']:issues.append(['baseline modified',f['path']])
    r={'documents':len(counts),'inputs':len(ids),'duplicate_ids':[k for k,v in collections.Counter(ids).items() if v>1],'media':len(media),'counts':counts,'issues':issues}
    (ED/'structural-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf8');print(json.dumps({k:v for k,v in r.items() if k!='counts'},ensure_ascii=False,indent=2))
if __name__=='__main__':audit()
