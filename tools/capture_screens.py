#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kt66 Wazuh Discover/Dev Tools 실제 화면을 책용으로 캡처. 영역을 나눠 글자가 읽히게."""
import asyncio, os, urllib.parse
from playwright.async_api import async_playwright

BASE = "https://192.168.0.189:5601"
USER, PW = "admin", "SecretPassword"
OUT = "/tmp/claude-1000/-home-ccc-kt66/c53501d4-1d92-4fa1-bdc0-1b8aeee2f51a/scratchpad/book/shots"
STATE = os.path.join(OUT, "state.json")
os.makedirs(OUT, exist_ok=True)
VW, VH = 1680, 1050


async def ensure_login(pg, ctx):
    await pg.goto(BASE, wait_until="domcontentloaded"); await pg.wait_for_timeout(3500)
    if await pg.locator('input[data-test-subj="user-name"]').count():
        await pg.fill('input[data-test-subj="user-name"]', USER)
        await pg.fill('input[data-test-subj="password"]', PW)
        await pg.click('button[data-test-subj="submit"]'); await pg.wait_for_timeout(8000)
        await ctx.storage_state(path=STATE)


async def clip(pg, name, x, y, w, h):
    await pg.screenshot(path=os.path.join(OUT, name), clip={"x": x, "y": y, "width": w, "height": h})
    print("clip", name)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--ignore-certificate-errors", "--force-device-scale-factor=2"])
        ctx = await b.new_context(viewport={"width": VW, "height": VH}, ignore_https_errors=True,
                                  device_scale_factor=2, locale="en-US",
                                  storage_state=STATE if os.path.exists(STATE) else None)
        pg = await ctx.new_page()
        await ensure_login(pg, ctx)

        # Discover: 쿼리 rule.level>=7 + 열 지정 (URL 상태로)
        q = urllib.parse.quote("rule.level >= 7")
        a = "(discover:(columns:!(agent.name,rule.level,rule.description),isDirty:!f,sort:!(!(timestamp,desc)))," \
            "metadata:(indexPattern:'wazuh-alerts-*',view:discover))"
        g = "(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-24h,to:now))"
        qq = "(filters:!(),query:(language:kuery,query:'rule.level%20%3E=%207'))"
        url = f"{BASE}/app/data-explorer/discover#?_a={a}&_g={g}&_q={qq}"
        await pg.goto(url, wait_until="domcontentloaded"); await pg.wait_for_timeout(9000)
        await pg.screenshot(path=os.path.join(OUT, "s_overview.png"))
        # 영역 분할 캡처 (CSS px)
        await clip(pg, "s_topbar.png", 0, 64, VW, 60)          # 인덱스패턴·검색·DQL·시간범위
        await clip(pg, "s_fields.png", 0, 168, 398, 760)        # 필드 목록
        await clip(pg, "s_table.png", 356, 170, VW - 356, 650)  # 문서 표(열 지정됨, Time 포함)

        # 시간 범위 퀵메뉴 열기
        try:
            await pg.click('[data-test-subj="superDatePickerToggleQuickMenuButton"]'); await pg.wait_for_timeout(1500)
            await clip(pg, "s_time.png", 980, 64, 700, 560)
            await pg.keyboard.press("Escape")
        except Exception as e:
            print("time err", e)

        # 문서 한 건 펼치기
        try:
            await pg.locator('[data-test-subj="docTableExpandToggleColumn"] button').first.click()
            await pg.wait_for_timeout(2500)
            shot_done = False
            for sel in ['.osdDocViewer', '[data-test-subj="osdDocViewer"]', '[data-test-subj="docViewer"]',
                        'div:has(> [data-test-subj="docViewerTab-table"])']:
                loc = pg.locator(sel)
                if await loc.count():
                    try:
                        await loc.first.scroll_into_view_if_needed()
                        await loc.first.screenshot(path=os.path.join(OUT, "s_doc.png"))
                        print("doc shot via", sel); shot_done = True; break
                    except Exception:
                        pass
            if not shot_done:
                await clip(pg, "s_doc.png", 0, 628, VW, 418)
        except Exception as e:
            print("expand err", e)

        # Dev Tools
        try:
            await pg.goto(BASE + "/app/dev_tools#/console", wait_until="domcontentloaded"); await pg.wait_for_timeout(6000)
            dm = pg.locator('button:has-text("Dismiss"):visible')
            if await dm.count(): await dm.first.click(); await pg.wait_for_timeout(800)
            await pg.wait_for_function("() => { const e=document.querySelector('[data-test-subj=request-editor]'); return e && e.env && e.env.editor; }", timeout=20000)
            body = 'GET wazuh-alerts-*/_search\n{\n  "size": 2,\n  "query": { "range": { "rule.level": { "gte": 7 } } },\n  "sort": [{ "timestamp": "desc" }]\n}'
            await pg.evaluate("""(t)=>{const ed=document.querySelector('[data-test-subj=request-editor]').env.editor;
                ed.setOptions({enableLiveAutocompletion:false,enableBasicAutocompletion:false});
                ed.setValue(t,-1); ed.setFontSize(16); ed.resize(true); ed.blur();
                document.querySelectorAll('.ace_tooltip,.ace_autocomplete').forEach(e=>e.style.display='none');}""", body)
            await pg.wait_for_timeout(600)
            # 실행
            for sel in ['[data-test-subj="sendRequestButton"]', 'button[aria-label="Click to send request"]', '.conApp__editorActionButton']:
                if await pg.locator(sel).count():
                    await pg.locator(sel).first.click(); break
            await pg.wait_for_timeout(5000)
            await pg.keyboard.press("Escape")
            await pg.mouse.move(6, 700)                 # 툴팁 제거
            await pg.wait_for_timeout(600)
            await clip(pg, "s_devtools.png", 0, 150, VW, 980)
            print("devtools shot")
        except Exception as e:
            print("devtools err", e)

        await b.close()

asyncio.run(main())
