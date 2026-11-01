"""저자용: 기존 kt66 웹 UI를 조회·촬영한다. 설치·설정 변경은 하지 않는다."""
import asyncio
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/screens/chapter01'

async def main():
    host=os.environ.get('KT66_HOST','192.168.0.189')
    captures=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch()
        ctx=await browser.new_context(viewport={'width':560,'height':900},device_scale_factor=2,ignore_https_errors=True)
        page=await ctx.new_page()
        async def snap(name,clip,width_mm,min_css_px):
            await page.screenshot(path=str(OUT/name),clip=clip)
            captures.append({'file':name,'url':page.url,'clip_css_px':clip,'viewport_css_px':page.viewport_size,'width_mm':width_mm,'smallest_required_text_css_px':min_css_px,'estimated_text_pt':round(min_css_px*width_mm*72/25.4/clip['width'],2),'sha256':hashlib.sha256((OUT/name).read_bytes()).hexdigest()})
        await page.goto(f'http://{host}/',wait_until='networkidle')
        await snap('web.png',{'x':0,'y':0,'width':560,'height':265},127,14)
        await page.set_viewport_size({'width':1040,'height':800})
        await page.goto(f'https://{host}:5601/',wait_until='networkidle')
        await snap('login.png',{'x':260,'y':160,'width':520,'height':430},110,16)
        await page.locator('[data-test-subj="user-name"]').fill('admin')
        await page.locator('[data-test-subj="password"]').fill(os.environ.get('KT66_PASSWORD','SecretPassword'))
        await page.locator('[data-test-subj="submit"]').click()
        await page.wait_for_timeout(10000)
        await snap('home.png',{'x':0,'y':0,'width':480,'height':315},127,14)
        await page.get_by_text('Active (',exact=False).first.click()
        await page.get_by_text('kt66-host',exact=True).wait_for(timeout=30000)
        await page.get_by_text('kt66-host',exact=True).click()
        await page.wait_for_timeout(3500)
        await page.set_viewport_size({'width':480,'height':900})
        await page.wait_for_timeout(1000)
        status=page.get_by_text('Status',exact=True).first.locator('xpath=../..')
        observed=await status.locator('.hide-agent-status').inner_text()
        assert observed=='active',observed
        await status.locator('.euiHealth').hover()
        await page.wait_for_timeout(1200)
        await snap('agents.png',{'x':0,'y':0,'width':480,'height':260},127,12)
        data={'captured_at':datetime.now(timezone.utc).isoformat(),'host':host,'kind':'existing-running-environment','fresh_install_verified':False,'observed_host_agent_status':observed,'note':'기존 환경의 웹 응답·admin 로그인·에이전트 연결을 새로 확인. 신규 VMware 설치와 구분한다.','device_scale_factor':2,'captures':captures}
        (OUT/'provenance.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
        await browser.close()
        print('Captured',len(captures),'screens; kt66-host:',observed)

if __name__=='__main__':asyncio.run(main())
