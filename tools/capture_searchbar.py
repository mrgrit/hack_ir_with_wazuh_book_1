#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""검색창·시간 범위 영역을 맥락까지 포함해 크게 재캡처."""
import asyncio, os, urllib.parse
from playwright.async_api import async_playwright
BASE="https://192.168.0.189:5601"; USER,PW="admin","SecretPassword"
OUT="/tmp/claude-1000/-home-ccc-kt66/c53501d4-1d92-4fa1-bdc0-1b8aeee2f51a/scratchpad/book/shots"
STATE=os.path.join(OUT,"state.json"); VW,VH=1680,1050

async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--ignore-certificate-errors","--force-device-scale-factor=2"])
        ctx=await b.new_context(viewport={"width":VW,"height":VH},ignore_https_errors=True,device_scale_factor=2,
                                locale="en-US",storage_state=STATE if os.path.exists(STATE) else None)
        pg=await ctx.new_page()
        await pg.goto(BASE,wait_until="domcontentloaded"); await pg.wait_for_timeout(3000)
        if await pg.locator('input[data-test-subj="user-name"]').count():
            await pg.fill('input[data-test-subj="user-name"]',USER); await pg.fill('input[data-test-subj="password"]',PW)
            await pg.click('button[data-test-subj="submit"]'); await pg.wait_for_timeout(8000); await ctx.storage_state(path=STATE)
        a="(discover:(columns:!(agent.name,rule.level,rule.description),isDirty:!f,sort:!(!(timestamp,desc))),metadata:(indexPattern:'wazuh-alerts-*',view:discover))"
        g="(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-24h,to:now))"
        qq="(filters:!(),query:(language:kuery,query:'rule.level%20%3E=%207'))"
        await pg.goto(f"{BASE}/app/data-explorer/discover#?_a={a}&_g={g}&_q={qq}",wait_until="domcontentloaded")
        await pg.wait_for_timeout(9000)
        await pg.mouse.move(6,900); await pg.wait_for_timeout(300)
        # 검색창~히스토그램 상단까지 크게 (맥락 포함)
        await pg.screenshot(path=os.path.join(OUT,"s_searchbar_big.png"),clip={"x":0,"y":64,"width":VW,"height":330})
        print("done")
        await b.close()
asyncio.run(main())
