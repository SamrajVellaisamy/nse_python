import asyncio
import sys
import json
from playwright.async_api import async_playwright

# Fix event loop for Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def fetch_nse_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # show browser
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.nseindia.com/get-quotes/equity?symbol=SBIN", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)
        cookies = await context.cookies()
        cookie_dict = {} 
        with open('cookies','w') as line:
            for cookie in cookies:
                cookie_dict[cookie["name"]] = cookie["value"]
            line.write(json.dumps(cookie_dict)) 
        return cookie_dict
        await browser.close()


