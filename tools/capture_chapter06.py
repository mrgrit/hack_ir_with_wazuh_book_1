"""저자용: 실제 DVWA·Chromium 개발자 도구 조작과 화면 촬영. DB 초기화 없음."""
import hashlib,json,os,urllib.request
from datetime import datetime,timezone
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/screens/chapter06';EV=ROOT/'editorial/evidence/chapter06'
HOST=os.environ.get('KT66_HOST','192.168.0.189');DOMAIN=os.environ.get('KT66_DVWA','dvwa.ccc.com');BASE='http://'+DOMAIN
for d in (OUT,EV):d.mkdir(parents=True,exist_ok=True)
def main():
 captures=[];events=[]
 with sync_playwright() as p:
  b=p.chromium.launch(channel='chromium',args=['--host-resolver-rules=MAP '+DOMAIN+' '+HOST,'--remote-debugging-port=9229','--remote-allow-origins=*'])
  c=b.new_context(viewport={'width':1000,'height':900},device_scale_factor=2,timezone_id='Asia/Seoul');page=c.new_page()
  def shot(name,pg,clip,font=12,width=127):
   pg.screenshot(path=str(OUT/(name+'.png')),clip=clip)
   captures.append({'file':name+'.png','clip_css':clip,'device_scale_factor':2,'print_width_mm':width,'minimum_css_font_px':font,'estimated_text_pt':round(font*width*72/25.4/clip['width'],2),'sha256':hashlib.sha256((OUT/(name+'.png')).read_bytes()).hexdigest()})
  def record(r,name):
   events.append({'case':name,'time_utc':datetime.now(timezone.utc).isoformat(),'url':r.url,'method':r.request.method,'status':r.status,'location':r.headers.get('location')});print(name,r.status,r.url[:130],flush=True)
  page.goto(BASE+'/login.php')
  target=next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:9229/json')) if t['url'].startswith(BASE))
  dev=c.new_page();dev.set_viewport_size({'width':650,'height':900});dev.goto('devtools://devtools/bundled/inspector.html?ws=127.0.0.1:9229/devtools/page/'+target['id']+'&panel=network')
  dev.get_by_role('button',name='Toggle screencast',exact=True).click();dev.wait_for_timeout(1200)
  dev.get_by_role('checkbox',name='Keep log',exact=True).check()
  def clear():dev.get_by_role('tab',name='Network',exact=True).click();dev.get_by_role('button',name='Clear network log',exact=False).click()
  def headers(name,needle):
   dev.wait_for_timeout(400);dev.get_by_role('row').filter(has_text=needle).first.locator('td').first.click();dev.get_by_role('tab',name='Headers',exact=True).click();dev.wait_for_timeout(250)
   shot(name,dev,{'x':200,'y':185,'width':450,'height':185})
  # Login fails and succeeds with the same POST 302 code.
  for case,pw in [('login-wrong1','book06-wrong1'),('login-wrong2','book06-wrong2'),('login-correct','password')]:
   page.locator('input[name=username]').fill('admin');page.locator('input[name=password]').fill(pw)
   if case=='login-wrong1':
    a=page.locator('form').bounding_box();shot('login-input',page,{'x':a['x']-10,'y':a['y']-15,'width':400,'height':190},12,105)
   clear()
   with page.expect_response(lambda r:r.request.method=='POST' and r.url.endswith('/login.php')) as got:page.locator('input[name=Login]').click()
   page.wait_for_load_state('networkidle');record(got.value,case)
   if case=='login-wrong1':
    assert 'Login failed' in page.locator('body').inner_text();a=page.locator('form').bounding_box();shot('login-failed',page,{'x':a['x']-10,'y':a['y']-15,'width':400,'height':260},12,105);headers('login-failed-headers','login.php')
   if case=='login-correct':
    assert page.url.endswith('/index.php');shot('login-success',page,{'x':270,'y':100,'width':510,'height':150});headers('login-success-headers','login.php')
  page.get_by_role('link',name='DVWA Security',exact=True).click();original=page.locator('select[name=security]').input_value();page.locator('select[name=security]').select_option('low');page.locator('input[name=seclev_submit]').click();shot('security',page,{'x':270,'y':100,'width':510,'height':125})
  # Brute Force practice form: three manual candidate submissions.
  page.get_by_role('link',name='Brute Force',exact=True).click()
  for case,pw in [('brute-wrong1','book06-wrong1'),('brute-wrong2','book06-wrong2'),('brute-correct','password')]:
   page.locator('input[name=username]').fill('admin');page.locator('input[name=password]').fill(pw)
   if case=='brute-wrong1':shot('brute-input',page,{'x':270,'y':100,'width':510,'height':200})
   clear()
   with page.expect_response(lambda r:'/vulnerabilities/brute/?' in r.url and r.request.resource_type=='document') as got:page.locator('input[name=Login]').click()
   page.wait_for_load_state('networkidle');record(got.value,case)
   if case=='brute-wrong1':shot('brute-failed',page,{'x':270,'y':100,'width':510,'height':260});headers('brute-failed-headers','?username=')
   if case=='brute-correct':shot('brute-success',page,{'x':270,'y':100,'width':510,'height':280});headers('brute-success-headers','?username=')
  # Individual path navigation; no directory scanner substitutes for the reader's first observations.
  for case,path in [('path-known','/login.php?book06=known'),('path-missing','/book06-missing'),('admin','/admin/'),('phpmyadmin','/phpmyadmin/'),('wpadmin','/wp-admin/'),('manager','/manager/html')]:
   clear();r=page.goto(BASE+path);record(r,case)
   if case in ('path-missing','admin'):
    shot(case,page,{'x':0,'y':0,'width':560,'height':180},16);headers(case+'-headers',path.strip('/').split('/')[0])
  # Actual Network conditions UI edits the user-agent string.
  dev.get_by_role('button',name='More network conditions',exact=False).click();dev.wait_for_timeout(300)
  default=dev.get_by_role('checkbox',name='Use browser default',exact=True);default.uncheck()
  custom=dev.get_by_role('textbox',name='Enter a custom user agent',exact=True);custom.fill('sqlmap/1.0 book06-ua');custom.press('Tab');dev.wait_for_timeout(300)
  a=custom.bounding_box();shot('ua-settings',dev,{'x':max(0,a['x']-10),'y':a['y']-80,'width':530,'height':130})
  r=page.goto(BASE+'/book06-ua');record(r,'ua');assert r.request.headers.get('user-agent')=='sqlmap/1.0 book06-ua'
  events[-1]['user_agent']=r.request.headers['user-agent'];shot('ua-response',page,{'x':0,'y':0,'width':560,'height':180},16)
  default.check();assert default.is_checked()
  # Close drawer so Network panels use stable layout.
  dev.get_by_role('button',name='Close drawer',exact=False).click()
  page.goto(BASE+'/login.php');clear();dev.get_by_role('tab',name='Console',exact=True).click();dev.wait_for_timeout(400)
  # Enter and execute one request in the real DevTools Console.
  prompt=dev.get_by_role('textbox',name='Console prompt',exact=True);prompt.click()
  method="fetch('/book06-method', {method: 'PROPFIND'})\n  .then(r => console.log(r.status));"
  dev.keyboard.insert_text(method)
  with page.expect_response(lambda r:'/book06-method' in r.url) as got:dev.keyboard.press('Enter')
  record(got.value,'method');dev.wait_for_timeout(600)
  shot('method-console',dev,{'x':0,'y':55,'width':600,'height':195})
  dev.get_by_role('tab',name='Network',exact=True).click();headers('method-headers','book06-method')
  # A single long navigation from Console; literal input and returned code remain reproducible.
  clear();dev.get_by_role('tab',name='Console',exact=True).click();dev.get_by_role('textbox',name='Console prompt',exact=True).click()
  longcmd="location.href = '/?book06-long=' + 'A'.repeat(8000);"
  dev.keyboard.insert_text(longcmd)
  with page.expect_response(lambda r:'book06-long=' in r.url and r.request.resource_type=='document') as got:dev.keyboard.press('Enter')
  record(got.value,'long');events[-1]['url_length']=len(got.value.url);dev.wait_for_timeout(500)
  # Restore only the setting changed by this capture run.
  page.goto(BASE+'/security.php');page.locator('select[name=security]').select_option(original);page.locator('input[name=seclev_submit]').click();assert page.locator('select[name=security]').input_value()==original
  page.get_by_role('link',name='Logout',exact=True).click();assert page.url.endswith('/login.php')
  (EV/'execution.json').write_text(json.dumps({'browser':b.version,'events':events,'original_security':original,'restored_security':original,'user_agent_restored':True,'logged_out':True,'db_reset':False,'notes':'Real Chromium on Linux, Windows UI instructions follow equivalent controls. No cookies or CSRF tokens persisted.'},ensure_ascii=False,indent=2)+'\n')
  (OUT/'provenance.json').write_text(json.dumps({'source':'Actual DVWA and Chromium DevTools; crop only','captures':captures},ensure_ascii=False,indent=2)+'\n')
  b.close()
if __name__=='__main__':main()
