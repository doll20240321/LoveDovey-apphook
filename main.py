import asyncio
import time
import os
import requests
from playwright.async_api import async_playwright

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# 用來記錄已推送過的公告
sent_notices = set()

async def fetch_announcements():
    """用 Playwright 抓取公告頁面渲染後的文字"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.loveydovey.ai/zh_Hant_TW/notices")

        # 等待公告元素渲染出來 (需依實際 DOM 結構調整 selector)
        await page.wait_for_selector("div.notice-item")

        notices = await page.query_selector_all("div.notice-item")
        results = []
        for n in notices:
            text = await n.inner_text()
            results.append(text.strip())

        await browser.close()
        return results

def send_to_discord(message: str):
    """推送訊息到 Discord webhook"""
    if not WEBHOOK_URL:
        print("WEBHOOK_URL 未設定")
        return
    payload = {"content": message}
    try:
        r = requests.post(WEBHOOK_URL, json=payload)
        if r.status_code == 204:
            print("成功推送到 Discord")
        else:
            print(f"推送失敗: {r.status_code}, {r.text}")
    except Exception as e:
        print(f"推送錯誤: {e}")

async def main():
    """循環抓公告並推送到 Discord"""
    while True:
        notices = await fetch_announcements()
        for n in notices:
            if n not in sent_notices:   # 去重機制
                send_to_discord(f"📢 公告：{n}")
                sent_notices.add(n)
            else:
                print(f"跳過重複公告：{n}")
        print("等待 1 小時後再次抓取...")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
