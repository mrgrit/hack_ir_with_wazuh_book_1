"""저자용: 작은 지면에 맞춘 Console과 긴 URL Network 목록 추가 촬영."""
import json,urllib.request,hashlib
from datetime import datetime,timezone
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'assets/screens/chapter06';E=R/'editorial/evidence/chapter06'
def main():
 with sync_playwright() as p:
  b=p.chromium.launch(channel='chromium',args=['--host-resolver-rules=MAP dvwa.ccc.com 192.168.0.189','--remote-debugging-port=9230','--remote-allow-origins=*']);c=b.new_context(viewport={'width':1000,'height':900},device_scale_factor=2);page=c.new_page();page.goto('http://dvwa.ccc.com/login.php')
  target=next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:9230/json')) if 'dvwa.ccc.com' in t['url']);dev=c.new_page();dev.set_viewport_size({'width':530,'height':900});dev.goto('devtools://devtools/bundled/inspector.html?ws=127.0.0.1:9230/devtools/page/'+target['id']+'&panel=network');dev.get_by_role('button',name='Toggle screencast',exact=True).click();dev.wait_for_timeout(1000);dev.get_by_role('checkbox',name='Keep log',exact=True).check()
  captures=[];events=[]
  page.locator('input[name=username]').fill('admin');page.locator('input[name=password]').fill('password');page.locator('input[name=Login]').click();page.wait_for_load_state('networkidle');assert page.url.endswith('/index.php')
  def shot(name,clip):
   dev.screenshot(path=str(O/(name+'.png')),clip=clip);captures.append({'file':name+'.png','clip_css':clip,'device_scale_factor':2,'print_width_mm':127,'minimum_css_font_px':12,'estimated_text_pt':round(12*127*72/25.4/clip['width'],2),'sha256':hashlib.sha256((O/(name+'.png')).read_bytes()).hexdigest()})
  def rec(r,case):events.append({'case':case,'time_utc':datetime.now(timezone.utc).isoformat(),'method':r.request.method,'url':r.url,'status':r.status,'location':r.headers.get('location')})
  title=page.locator('#main_body h1').first;box=title.bounding_box();page.screenshot(path=str(O/'login-success.png'),clip={'x':box['x']-3,'y':box['y']-3,'width':box['width']+6,'height':box['height']+6});captures.append({'file':'login-success.png','clip_css':{'x':box['x']-3,'y':box['y']-3,'width':box['width']+6,'height':box['height']+6},'device_scale_factor':2,'print_width_mm':127,'minimum_css_font_px':24,'estimated_text_pt':round(24*127*72/25.4/(box['width']+6),2),'sha256':hashlib.sha256((O/'login-success.png').read_bytes()).hexdigest()})
  dev.get_by_role('tab',name='Console',exact=True).click();dev.get_by_role('textbox',name='Console prompt',exact=True).click();dev.keyboard.insert_text("fetch('/book06-method', {method: 'PROPFIND'})\n  .then(r => console.log(r.status));")
  with page.expect_response(lambda r:'/book06-method' in r.url) as got:dev.keyboard.press('Enter')
  rec(got.value,'method');dev.wait_for_timeout(500);shot('method-console',{'x':0,'y':55,'width':530,'height':190})
  dev.set_viewport_size({'width':650,'height':900});dev.get_by_role('tab',name='Network',exact=True).click();dev.get_by_role('button',name='Clear network log',exact=False).click();dev.get_by_role('tab',name='Console',exact=True).click();dev.get_by_role('textbox',name='Console prompt',exact=True).click();dev.keyboard.insert_text("location.href = '/?book06-long=' + 'A'.repeat(8000);")
  with page.expect_response(lambda r:'book06-long=' in r.url and r.request.resource_type=='document') as got:dev.keyboard.press('Enter')
  rec(got.value,'long');assert got.value.status==200;dev.get_by_role('tab',name='Network',exact=True).click();dev.wait_for_timeout(700)
  a=dev.get_by_role('row').first.bounding_box();z=dev.get_by_role('row').filter(has_text='book06-long').first.bounding_box();shot('long-network',{'x':0,'y':a['y'],'width':385,'height':z['y']+z['height']-a['y']})
  page.goto('http://dvwa.ccc.com/logout.php');assert page.url.endswith('/login.php')
  primary_path=O/'provenance.json'
  if primary_path.exists():
   primary=json.loads(primary_path.read_text());updated={v['file'] for v in captures};primary['captures']=[v for v in primary['captures'] if v['file'] not in updated];primary['supplement']='detail-provenance.json';primary_path.write_text(json.dumps(primary,ensure_ascii=False,indent=2)+'\n')
  (E/'detail-execution.json').write_text(json.dumps({'events':events,'source':'Additional actual browser requests for layout; no application changes or DB reset'},indent=2)+'\n');(O/'detail-provenance.json').write_text(json.dumps({'source':'Actual Chromium DevTools; crop only','captures':captures},indent=2)+'\n');b.close()
if __name__=='__main__':main()
