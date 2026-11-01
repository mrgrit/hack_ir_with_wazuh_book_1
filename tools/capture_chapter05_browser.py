"""저자용: DVWA의 실제 폼 입력·클릭·주소 이동과 Chromium Network 화면 촬영.
기존 DB 초기화는 수행하지 않는다. 준비된 학습 DB에서 로그인하고 요청을 보낸다.
"""
import hashlib,json,os,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/screens/chapter05/browser';OUT.mkdir(parents=True,exist_ok=True)
EVID=ROOT/'editorial/evidence/chapter05/browser';EVID.mkdir(parents=True,exist_ok=True)
HOST=os.environ.get('KT66_HOST','192.168.0.189');DOMAIN=os.environ.get('KT66_DVWA','dvwa.ccc.com');BASE='http://'+DOMAIN
captures=[];events=[]
def main():
 with sync_playwright() as p:
  b=p.chromium.launch(channel='chromium',args=['--host-resolver-rules=MAP '+DOMAIN+' '+HOST,'--remote-debugging-port=9228','--remote-allow-origins=*'])
  ctx=b.new_context(viewport={'width':1000,'height':900},device_scale_factor=2,timezone_id='Asia/Seoul')
  page=ctx.new_page()
  def shot(name,pg,clip,minfont=12,width=127):
   pg.screenshot(path=str(OUT/(name+'.png')),clip=clip)
   captures.append({'file':name+'.png','url':pg.url.split('?ws=')[0] if pg.url.startswith('devtools:') else pg.url,'clip_css':clip,'print_width_mm':width,'minimum_css_font_px':minfont,'estimated_text_pt':round(minfont*width*72/25.4/clip['width'],2),'sha256':hashlib.sha256((OUT/(name+'.png')).read_bytes()).hexdigest()})
  def response(r,case):
   events.append({'case':case,'time_utc':datetime.now(timezone.utc).isoformat(),'method':r.request.method,'url':r.url,'status':r.status,'location':r.headers.get('location'),'browser':b.version})
   print(case,r.status,r.url,flush=True)
  page.goto(BASE+'/setup.php');page.locator('input[name=create_db]').scroll_into_view_if_needed()
  box=page.locator('input[name=create_db]').bounding_box();shot('setup-button',page,{'x':box['x']-10,'y':box['y']-15,'width':510,'height':85})
  page.goto(BASE+'/login.php');page.locator('input[name=username]').fill('admin');page.locator('input[name=password]').fill('password')
  box=page.locator('form').bounding_box();shot('login-filled',page,{'x':box['x']-10,'y':box['y']-15,'width':400,'height':190},12,105)
  page.locator('input[name=Login]').click();page.wait_for_load_state('networkidle');assert page.url==BASE+'/index.php','DVWA must already be initialized'
  shot('menu',page,{'x':60,'y':100,'width':185,'height':620},12,43)
  page.get_by_role('link',name='DVWA Security',exact=True).click()
  original=page.locator('select[name=security]').input_value()
  page.locator('select[name=security]').select_option('low');page.locator('input[name=seclev_submit]').click()
  assert 'Security level is currently: low.' in page.locator('#main_body').inner_text()
  shot('security-current',page,{'x':270,'y':100,'width':510,'height':125})
  box=page.locator('select[name=security]').bounding_box();shot('security-select',page,{'x':box['x']-10,'y':box['y']-12,'width':510,'height':65})
  # The real DevTools frontend connects to the real page; no simulated UI or network data.
  target=next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:9228/json')) if t['url'].startswith(BASE))
  dev=ctx.new_page();dev.set_viewport_size({'width':650,'height':900});dev.goto('devtools://devtools/bundled/inspector.html?ws=127.0.0.1:9228/devtools/page/'+target['id']+'&panel=network')
  dev.get_by_role('button',name='Toggle screencast',exact=True).click();dev.get_by_role('tab',name='Network',exact=True).click()
  # Keep log retains redirects; label differs by Chromium version.
  keep=dev.get_by_role('checkbox',name='Keep log',exact=True)
  if keep.count():keep.check()
  else:dev.get_by_role('checkbox',name='Preserve log',exact=True).check()
  def clear():dev.get_by_role('button',name='Clear network log',exact=False).click()
  page.get_by_role('link',name='SQL Injection',exact=True).click();page.locator('input[name=id]').fill('1')
  shot('normal-input',page,{'x':270,'y':100,'width':510,'height':145})
  clear()
  with page.expect_response(lambda r:'/vulnerabilities/sqli/?id=1&' in r.url and r.request.resource_type=='document') as got:page.locator('input[name=Submit]').click()
  response(got.value,'normal');assert 'First name: admin' in page.locator('#main_body').inner_text()
  shot('normal-result',page,{'x':270,'y':100,'width':510,'height':205})
  dev.wait_for_timeout(500)
  hr=dev.get_by_role('row').first.bounding_box();rr=dev.get_by_role('row').filter(has_text='?id=1').first.bounding_box()
  shot('network-list',dev,{'x':0,'y':hr['y'],'width':385,'height':rr['y']+rr['height']-hr['y']},12)
  def headers(name,needle):
   row=dev.get_by_role('row').filter(has_text=needle).first;row.locator('td').first.click();dev.get_by_role('tab',name='Headers',exact=True).click(timeout=3000);dev.wait_for_timeout(250)
   # Capture the actual detail pane, including tab labels and General fields.
   shot(name,dev,{'x':200,'y':185,'width':450,'height':205 if name=='sqli-headers' else 185},12)
  headers('normal-headers','?id=1')
  # Click the real page form for SQL and XSS.
  page.get_by_role('link',name='SQL Injection',exact=True).click()
  page.locator('input[name=id]').fill("1' UNION SELECT user,password FROM users-- ");page.locator('input[name=id]').press('Home')
  shot('sqli-input',page,{'x':270,'y':100,'width':510,'height':155})
  clear()
  with page.expect_response(lambda r:'/vulnerabilities/sqli/?' in r.url and r.request.resource_type=='document') as got:page.locator('input[name=Submit]').click()
  response(got.value,'sqli');assert got.value.status==403
  shot('sqli-blocked',page,{'x':0,'y':0,'width':560,'height':170},16)
  dev.wait_for_timeout(400);headers('sqli-headers','?id=')
  page.goto(BASE+'/vulnerabilities/xss_r/');page.locator('input[name=name]').fill('<script>alert(1)</script>')
  shot('xss-input',page,{'x':270,'y':147,'width':510,'height':105})
  with page.expect_response(lambda r:'/vulnerabilities/xss_r/?' in r.url and r.request.resource_type=='document') as got:page.locator('input[type=submit]').click()
  response(got.value,'xss');assert got.value.status==403
  shot('xss-blocked',page,{'x':0,'y':0,'width':560,'height':170},16)
  page.goto(BASE+'/vulnerabilities/fi/');shot('file-menu',page,{'x':270,'y':100,'width':540,'height':175},12)
  page.get_by_role('link',name='file1.php',exact=True).click();shot('file-normal',page,{'x':270,'y':100,'width':540,'height':230},12)
  r=page.goto(BASE+'/vulnerabilities/fi/?page=../../../../../etc/passwd&bookcase=book05-browser-path-raw');response(r,'path-raw');assert r.status==403
  shot('path-blocked',page,{'x':0,'y':0,'width':560,'height':170},16)
  r=page.goto(BASE+'/vulnerabilities/fi/?page=..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd&bookcase=book05-browser-path');response(r,'path');assert r.status==403
  shot('path-encoded-blocked',page,{'x':0,'y':0,'width':560,'height':170},16)
  page.goto(BASE+'/security.php');page.locator('select[name=security]').select_option(original);page.locator('input[name=seclev_submit]').click()
  assert page.locator('select[name=security]').input_value()==original
  page.get_by_role('link',name='Logout',exact=True).click();assert page.url.endswith('/login.php')
  (EVID/'execution.json').write_text(json.dumps({'captured_at':datetime.now(timezone.utc).isoformat(),'original_security':original,'restored_security':original,'logged_out':True,'events':events,'notes':'Browser UI interaction. Address-bar equivalent navigation for the two file-path requests. Response records omit cookies and tokens. Author browser on Linux; Windows setup instructions are document-checked, not executed on Windows.'},ensure_ascii=False,indent=2)+'\n')
  previous=json.loads((OUT/'provenance.json').read_text()) if (OUT/'provenance.json').exists() else {}
  captures.extend(x for x in previous.get('captures',[]) if x['file']=='setup-success.png')
  (OUT/'provenance.json').write_text(json.dumps({'captured_at':datetime.now(timezone.utc).isoformat(),'browser':b.version,'mode':'actual Chromium and its DevTools; viewport and crop only','device_scale_factor':2,'captures':captures},ensure_ascii=False,indent=2)+'\n')
  b.close()
if __name__=='__main__':main()
