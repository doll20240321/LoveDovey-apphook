import requests
import os
import time
import re
import redis

# --- 初始化 Redis ---
# Railway 會自動把 REDIS_URL 注入環境變數，直接讀取即可
redis_url = os.getenv('REDIS_URL')
r = redis.from_url(redis_url)

def clean_html(raw_html):
    return re.sub('<.*?>', '', raw_html)

def check_loveydovey():
    api_url = "https://www.loveydovey.ai/api/v1/notices?lang=zh_Hant_TW"
    webhook_url = os.getenv('WEBHOOK_URL')

    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 正在透過 Redis 檢查公告...")
        response = requests.get(api_url, timeout=15)
        data = response.json()
        latest = data['data'][0]
        n_id = str(latest['id'])
        
        # 1. 從 Redis 讀取上次存的 ID (Key 叫 'last_notice_id')
        last_id = r.get('last_notice_id')
        if last_id:
            last_id = last_id.decode('utf-8')

        # 2. 比對
        if n_id != last_id:
            print(f"發現新公告：{latest['title']}")
            clean_content = clean_html(latest.get('content', ''))[:300]
            
            payload = {
                "username": "卿我公告搬運工",
                "embeds": [{
                    "title": f"📢 {latest['title']}",
                    "description": f"{clean_content}...",
                    "url": "https://www.loveydovey.ai/zh_Hant_TW/notices",
                    "color": 16738740
                }]
            }
            requests.post(webhook_url, json=payload)
            
            # 3. 把新 ID 存入 Redis，下次重啟也會在
            r.set('last_notice_id', n_id)
            print("ID 已同步至 Redis。")
        else:
            print("Redis 比對結果：無更新。")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    while True:
        check_loveydovey()
        time.sleep(3600)
