"""이동한 설치 절의 참조와 UI 표기를 맞춘다. finalize 다음에 실행한다."""
import json,re
from pathlib import Path
from revise_volume01_rev02 import ROOT,OUT,ED,P,H,write,strings
from refine_volume01_rev02 import findpage

UI=['Create / Reset Database','Network conditions','Use browser default','Ruleset Test','Clear session','DVWA Security','Request Headers','Response Headers','Query String Parameters','Request URL','Request Method','Status Code','Preserve log','Disable cache','Keep log','Search field names','Selected fields','Commonly used','Last 24 hours','Last 15 minutes','Show dates','Start date','End date','Time field','Next step','Security Level','SQL Injection','XSS (Reflected)','File Inclusion','Brute Force','Command Injection','Discover','Network','Payload','Headers','Response','Absolute','Refresh','Submit','Login','Logout','Confirm']
pattern=re.compile(r'(?<![A-Za-z0-9_])('+'|'.join(re.escape(s) for s in sorted(UI,key=len,reverse=True))+r')(?![A-Za-z0-9_])')
def ui(s):
    pieces=s.split('**')
    for i in range(0,len(pieces),2):pieces[i]=pattern.sub(lambda m:'**'+m[0]+'**',pieces[i])
    return '**'.join(pieces)

def main():
    corrections={
     '1.9의 도구 설치':'부록 A.15의 도구 설치',
     '1.9의 일괄 설치':'부록 A.15의 일괄 설치',
     '1.9의 공격자 VM hosts 설정':'5.13의 공격자 VM hosts 설정',
     '1.9의 공격자 도구 준비':'부록 A.15의 공격자 도구 준비',
     '도구 준비는 1.9':'도구 준비는 부록 A.15',
     '1.9의 표':'A.15의 표',
     '도구 설치는 1.9로 돌아가 진행한다.':'도구 설치는 A.15에서 진행한다.',
     '1.3의 표':'A.12의 표',
     'kt66가':'kt66이',
     '이후 장에서는 시스템 권한 확대와 그에 따른 조사 범위를 이어 다룬다.':'10장에서는 현재 포트와 공개 키 상태를 조회해 변경 기록과 대조한다.',
     '11장에서는 앞 장들의 경보를 시간순으로 연결해 사건을 재구성하고 대응 범위를 결정한다.':'11장에서는 8~10장의 사례를 각각 재구성하고 확인한 근거에 따라 대응 범위를 정한다.'}
    for src in OUT.glob('*.json'):
        d=json.loads(src.read_text('utf8'))
        d=strings(d,lambda s:next((s.replace(a,b) for a,b in corrections.items() if a in s),s))
        # 한 문장에 둘 이상의 옛 참조가 있는 경우도 모두 처리한다.
        for old,new in corrections.items():d=strings(d,lambda s:s.replace(old,new))
        for p in d['pages']:
            for b in p['blocks']:
                if b['type'] in ['p','box','list']:b.update(strings(b,ui))
                if b['type'] in ['command','query']:
                    for k in ['why','purpose','syntax','result']:
                        if k in b:b[k]=ui(b[k].replace('검증 환경은','사례 환경은').replace('검증 환경의','사례의'))
        if src.name=='volume01-chapter01.json':
            p=findpage(d,'1.8')
            for i,b in enumerate(p['blocks']):
                if b['type']=='table' and b['head'][0]=='실행 일지의 동작':
                    p['blocks'][i]={'type':'image','path':'assets/figures/rev02/casebook-path.png','caption':'도식 1-8. 실행 일지와 단계별 조사 근거의 대조.','width_mm':127}
                    break
        if src.name=='volume01-appendix-b.json':
            idx=json.loads((ROOT/'examples/rev02/input-index.json').read_text('utf8'));p=findpage(d,'B.7')
            for row in p['blocks'][1]['rows']:
                found=next((r for r in idx if r['id']==row[1]),None)
                if found:row[2]=found['section']
        write(src,d)
    print('UI labels and moved-section references updated')

if __name__=='__main__':main()
