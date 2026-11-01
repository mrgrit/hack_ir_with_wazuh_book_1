"""저자용: 원고 검색식과 촬영 시 사용한 DQL을 대조하고 선택 curl 검색식을 UI에서 검증한다."""
import json,re,os,urllib.parse,subprocess,shlex
from datetime import datetime,timezone
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];E=R/'editorial/evidence/chapter06';HOST=os.environ.get('KT66_HOST','192.168.0.189')
def main():
 queries=json.loads((R/'examples/chapter06/queries.json').read_text());proof=json.loads((R/'assets/screens/chapter06/wazuh-provenance.json').read_text());verified=[]
 for q,got in zip(queries[:11],proof['DQL_verified']):
  assert re.sub(r'\s+',' ',q['text'])==got['DQL'];assert int(got['hits'])>0
  verified.append({'id':q['id'],'query':q['text'],'hits':int(got['hits']),'index':got['index'],'range':proof['time_range'],'method':'Actual Discover UI; capture_chapter06_wazuh.py'})
 with sync_playwright() as p:
  b=p.chromium.launch();c=b.new_context(ignore_https_errors=True);pg=c.new_page();pg.goto(f'https://{HOST}:5601/',wait_until='networkidle');pg.locator('[data-test-subj=user-name]').fill('admin');pg.locator('[data-test-subj=password]').fill(os.environ.get('KT66_PASSWORD','SecretPassword'));pg.locator('[data-test-subj=submit]').click();pg.wait_for_timeout(2500)
  start=proof['time_range']['from'];end=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
  for q in queries[11:]:
   url=f"https://{HOST}:5601/app/data-explorer/discover#?_a=(discover:(columns:!(data.srcip,rule.id,data.id),isDirty:!f,sort:!()),metadata:(indexPattern:'wazuh-alerts-*',view:discover))&_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:'{start}',to:'{end}'))&_q=(filters:!(),query:(language:kuery,query:'"+urllib.parse.quote(q['text'],safe='')+"'))"
   pg.goto(url,wait_until='networkidle');pg.wait_for_timeout(700);hits=int(pg.locator('[data-test-subj=discoverQueryHits]').inner_text());assert hits>0;verified.append({'id':q['id'],'query':q['text'],'hits':hits,'index':'wazuh-alerts-*','range':{'from':start,'to':end},'method':'Actual Discover UI'});print(q['id'],hits,flush=True)
  b.close()
 (E/'queries-verified.json').write_text(json.dumps(verified,ensure_ascii=False,indent=2)+'\n')
 # Execute the three read-only source expressions in their actual containers.
 commands=json.loads((R/'examples/chapter06/manifest.json').read_text());results=[]
 base=['ssh','-i','/home/ccc/kt66/keys/id_rsa','-o','BatchMode=yes','-o','UserKnownHostsFile=/tmp/book-ch04-known-hosts','ccc@10.20.30.201']
 for cmd in commands:
  if cmd['id'] not in ['C06-12','C06-20','C06-21']:continue
  container='kt66-siem' if cmd['id']=='C06-12' else 'kt66-dvwa';directory='/var/ossec/ruleset/rules' if container=='kt66-siem' else '/var/www/html'
  remote='docker exec -w '+shlex.quote(directory)+' '+container+' bash -c '+shlex.quote(cmd['text']);r=subprocess.run(base+[remote],capture_output=True,text=True,check=True);results.append({'id':cmd['id'],'container':container,'directory':directory,'command':cmd['text'],'stdout':r.stdout,'returncode':r.returncode})
 (E/'source-commands.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('13 DQL and 3 source-read commands verified')
if __name__=='__main__':main()
