"""저자용: 기존 Wazuh 기록을 조회하고 실제 UI 영역을 촬영한다."""
import json,hashlib,urllib.parse,os
from pathlib import Path
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/screens/chapter05';EVID=ROOT/'editorial/evidence/chapter05'
HOST=os.environ.get('KT66_HOST','192.168.0.189');DOMAIN=os.environ.get('KT66_DVWA','dvwa.ccc.com');captures=[]
def main():
 with sync_playwright() as p:
  b=p.chromium.launch(args=['--host-resolver-rules=MAP '+DOMAIN+' '+HOST])
  c=b.new_context(ignore_https_errors=True,viewport={'width':1000,'height':1000},device_scale_factor=2,timezone_id='Asia/Seoul')
  page=c.new_page();page.goto(f'https://{HOST}:5601/',wait_until='networkidle')
  page.locator('[data-test-subj="user-name"]').fill('admin');page.locator('[data-test-subj="password"]').fill(os.environ.get('KT66_PASSWORD','SecretPassword'));page.locator('[data-test-subj="submit"]').click();page.wait_for_timeout(3500)
  def shot(name,clip,min_font=12):
   page.screenshot(path=str(OUT/(name+'.png')),clip=clip)
   captures.append({'file':name+'.png','url':page.url,'clip_css':clip,'device_scale_factor':2,'print_width_mm':110 if name=='dvwa-login' else 127,'minimum_css_font_px':min_font,'estimated_text_pt':round(min_font*(110 if name=='dvwa-login' else 127)*72/25.4/clip['width'],2),'sha256':hashlib.sha256((OUT/(name+'.png')).read_bytes()).hexdigest()})
  def rows(name,first,last=None):
   trs=page.locator('table.osdDocViewerTable tr')
   def row(field):return trs.filter(has=page.locator('td',has_text=field)).filter(has_text=field)
   # Crop the empty action-button gutter; retain the original field labels and values.
   # Match the field cell exactly to distinguish id from rule.id etc.
   def exact(field):
    for i in range(trs.count()):
     cells=trs.nth(i).locator('td,th').all_text_contents()
     if any(t.replace('\u200b','').replace('String field','').replace('Date field','').replace('Number field','').replace('Boolean field','').strip()==field for t in cells):return trs.nth(i)
    print(trs.all_text_contents()[:12],flush=True);raise RuntimeError('Missing field '+field)
   one=exact(first);two=exact(last or first);one.scroll_into_view_if_needed();page.wait_for_timeout(200)
   a=one.bounding_box();z=two.bounding_box();a['x']+=140;a['width']-=140;clip={'x':a['x'],'y':a['y'],'width':a['width'],'height':z['y']+z['height']-a['y']}
   if clip['y']+clip['height']>1000:page.mouse.wheel(0,clip['y']+clip['height']-980);page.wait_for_timeout(200);a=one.bounding_box();z=two.bounding_box();clip.update(y=a['y'],height=z['y']+z['height']-a['y'])
   shot(name,clip)
  cases=[('normal','wazuh-archives-*','agent.name: "web" AND data.url: *book05-normal*'),('sqli','wazuh-alerts-*','agent.name: "web" AND data.url: *book05-sqli*'),('xss','wazuh-alerts-*','agent.name: "web" AND data.url: *book05-xss*'),('path','wazuh-alerts-*','agent.name: "web" AND data.url: *book05-path*'),('waf','wazuh-archives-*','agent.name: "web" AND location: "/var/log/apache2/modsec_audit.log" AND full_log: "book05-sqli"')]
  patterns=c.request.get(f'https://{HOST}:5601/api/saved_objects/_find?type=index-pattern&per_page=100').json()['saved_objects']
  pattern_ids={v['attributes']['title']:v['id'] for v in patterns}
  results=[]
  for name,index,query in cases:
   page.set_viewport_size({'width':700,'height':1000})
   url=f"https://{HOST}:5601/app/data-explorer/discover#?_a=(discover:(columns:!(data.srcip,rule.id,data.id),isDirty:!f,sort:!()),metadata:(indexPattern:'{pattern_ids[index]}',view:discover))&_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-24h,to:now))&_q=(filters:!(),query:(language:kuery,query:'"+urllib.parse.quote(query,safe='')+"'))"
   page.goto(url,wait_until='networkidle');page.wait_for_timeout(1000)
   hits=page.locator('[data-test-subj="discoverQueryHits"]').inner_text();results.append({'name':name,'index':index,'DQL':query,'hits':hits});print(name,hits,flush=True)
   assert int(hits)>0
   page.get_by_role('button',name='Toggle row details',exact=True).first.click();page.locator('table.osdDocViewerTable').wait_for();page.wait_for_timeout(400)
   if name=='waf':rows('waf-action','data.audit_data.action.intercepted','data.audit_data.action.phase');rows('waf-response','data.response.status','data.transaction.transaction_id')
   else:
    rows(name+'-data','data.id','data.url')
    if name=='sqli':rows('sqli-rule','rule.description','rule.firedtimes')
    if name=='path':
     # Separate record images, each with its actual rule/result saved below.
     pass
   page.get_by_role('tab',name='JSON',exact=True).click();data=json.loads(page.get_by_role('tabpanel',name='JSON',exact=True).inner_text());(EVID/(name+'-ui-document.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
  # Evidence API is author-only; reader follows Discover UI steps.
  for index in ['wazuh-alerts-*','wazuh-archives-*']:
   payload={'size':30,'query':{'bool':{'filter':[{'term':{'agent.name':'web'}},{'wildcard':{'data.url':'*book05-*'}}]}},'sort':[{'timestamp':'asc'}]}
   r=c.request.post(f'https://{HOST}:5601/api/console/proxy?path='+index+'/_search&method=POST',headers={'osd-xsrf':'true'},data=payload);(EVID/(index.replace('*','all')+'.json')).write_text(json.dumps(r.json(),ensure_ascii=False,indent=2)+'\n')
  page.set_viewport_size({'width':500,'height':700});page.goto('http://'+DOMAIN+'/login.php',wait_until='networkidle');shot('dvwa-login',{'x':25,'y':15,'width':450,'height':370},14)
  (OUT/'provenance.json').write_text(json.dumps({'captured_at':datetime.now(timezone.utc).isoformat(),'captures':captures,'DQL_verified':results,'source':'Actual running kt66 UI; viewport resize/crop only; no field values altered'},ensure_ascii=False,indent=2)+'\n')
  b.close()
if __name__=='__main__':main()
