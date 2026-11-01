from pathlib import Path
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':900,'height':1100},device_scale_factor=1)
 page.goto((ROOT/'preview.html').as_uri())
 page.evaluate('document.fonts.ready')
 page.emulate_media(media='print')
 checks=page.evaluate('''() => Array.from(document.querySelectorAll('.sheet')).map((s,i)=>{ const c=s.querySelector('.content');return {page:i+1,overflow:c.scrollHeight-c.clientHeight,images:Array.from(s.querySelectorAll('img')).every(x=>x.complete&&x.naturalWidth>0)};})''')
 (ROOT/'editorial/layout-check.json').write_text(json.dumps(checks,indent=2))
 bad=[c for c in checks if c['overflow']>2 or not c['images']]
 if bad: print('LAYOUT ISSUES',bad)
 page.pdf(path=str(ROOT/'build/volume01-sample.pdf'),print_background=True,prefer_css_page_size=True)
 for n in [8,9,13,18,20]:
  page.locator(f'#page-{n}').screenshot(path=str(ROOT/f'build/page-{n:02}.png'))
 browser.close()
 print('PDF rendered; pages:',len(checks))
 if bad: raise SystemExit(1)
