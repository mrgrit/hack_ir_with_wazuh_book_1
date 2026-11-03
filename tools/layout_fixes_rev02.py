"""지면 검사에서 발견한 부록 참조와 장말의 외톨이 문단을 수정한다."""
import json,re,csv
from pathlib import Path
from revise_volume01_rev02 import ROOT,OUT,ED,P,H,write,strings
from refine_volume01_rev02 import findpage
def main():
    ap=OUT/'volume01-appendix-a.json';a=json.loads(ap.read_text('utf8'))
    refs=[p for p in a['pages'] if '참고 자료' in p['title']]
    a['pages']=[p for p in a['pages'] if '참고 자료' not in p['title']]+refs
    a=strings(a,lambda s:s.replace("1.3의 ‘설치 전 상태 보존’", "A.12의 ‘설치 전 상태 보존’"))
    t=next(b for b in a['pages'][0]['blocks'] if b['type']=='table')
    t['rows'] += [['A.7~A.11','환경·실행 위치·주소·수집 점검','전 장'],['A.12','Ubuntu 확인과 기본 도구 설치','1.3'],['A.13','kt66 코드와 환경 설정','1.4'],['A.14','Docker와 메모리 매핑 설정','1.5'],['A.15','공격자 VM 도구 설치','1.9']]
    write(ap,a)
    # 더 읽을거리는 읽을 이유와 자료명만 남기고 전체 URL은 권말의 해당 장에 모은다.
    rp=OUT/'volume01-references.json';refs=json.loads(rp.read_text('utf8'))
    for c in range(1,12):
        src=OUT/f'volume01-chapter{c:02}.json';d=json.loads(src.read_text('utf8'));p=d['pages'][-1]
        rb=findpage(refs,f'{c}장 참고문헌')['blocks'];known={b['url'] for b in rb if b['type']=='link'}
        keep=[]
        for b in p['blocks']:
            if b['type']=='link':
                if b['url'] not in known:rb += [H('더 읽을거리'),b];known.add(b['url'])
                keep.append(P(b['text']+f' — 전체 주소는 권말 참고문헌 {c}장에 있다.'))
            elif b['type']=='p' and b['text'].startswith('이 장의 전체 출처는 권말 참고문헌'):continue
            else:keep.append(b)
        p['blocks']=keep;write(src,d)
    write(rp,refs)
    # 마지막 표의 위치 표기를 절 번호로 줄이고 잘못 잡힌 ssh 설명의 입력 번호를 고친다.
    bp=OUT/'volume01-appendix-b.json';b=json.loads(bp.read_text('utf8'))
    b=strings(b,lambda s:re.sub(r'examples/(chapter\d\d)(?![\w/])',r'examples/rev02/\1',s).replace('examples/rev02/appendices/example-index.csv','examples/rev02/input-index.csv'))
    q=findpage(b,'B.7');q['blocks'][0]=P('기본 구문은 아래 입력에서, 전체 입력 목록은 examples/rev02/input-index.csv에서 찾는다.')
    for row in q['blocks'][1]['rows']:
        if row[0]=='ssh':row[1]='C02-01';row[2]='2.2'
        elif row[0]=='docker':row[1]='C02-P1';row[2]='2.2'
        else:
            m=re.match(r'([A-Z]|\d+)\.\d+',row[2]);row[2]=m[0] if m else {'C04-23':'4.7','C06-12':'6.2','C09-28':'9.6','C10-13':'10.3','C10-05':'10.2','C10-17':'10.4','C08-08':'8.1','C06-01':'6.2'}.get(row[1],row[2])
    write(bp,b)
    # 절 번호를 포함한 최종 입력 위치를 다시 추출한다.
    index=[]
    for src in sorted(OUT.glob('*.json')):
        d=json.loads(src.read_text('utf8'));section=''
        for p in d['pages']:
            m=re.match(r'((?:[A-F]|\d+)\.\d+)\s',p['title'])
            if m:section=m[1]
            for x in p['blocks']:
                if x['type'] not in ('command','query'):continue
                folder='appendix-a' if x['id'].startswith('CA-') else f'chapter{x["id"][1:3]}'
                target=ROOT/'examples/rev02'/folder/(x['id']+'.txt');target.write_text(x['text']+'\n','utf8')
                index.append({'document':src.name,'section':p['title'] if m else section+' '+p['title'],'id':x['id'],'where':x['where'],'file':target.relative_to(ROOT).as_posix(),'text':x['text']})
    write(ROOT/'examples/rev02/input-index.json',index)
    with (ROOT/'examples/rev02/input-index.csv').open('w',encoding='utf-8-sig',newline='') as h:
        w=csv.DictWriter(h,fieldnames=['document','section','id','where','file']);w.writeheader();w.writerows({k:x[k] for k in w.fieldnames} for x in index)
    print('Layout refinements applied')
if __name__=='__main__':main()
