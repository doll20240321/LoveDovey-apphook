import requests
import os
import time
import re
import base64

# --- 設定區 ---
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # GitHub 的 Token
REPO_NAME = os.getenv('doll20240321/LoveDovey-apphook')      # 格式: "你的帳號/你的專案名"
FILE_PATH = "last_id.txt"
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

def clean_html(raw_html):
    return re.sub('<.*?>', '', raw_html)

def get_last_id_from_github():
    """從 GitHub 抓取目前的 ID"""
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = base64.b64decode(res.json()['content']).decode('utf-8')
            return content.strip(), res.json()['sha'] # 回傳 ID 和檔案的 SHA (更新時需要)
    except:
        pass
    return "", None

def update_id_to_github(new_id, sha):
    """把新的 ID 存回 GitHub"""
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    content_b64 = base64.b64encode(new_id.encode('utf-8')).decode('utf-8')
    data = {
        "message": "Update last notice ID",
        "content": content_b64,
        "sha": sha
    }
    requests.put(url, headers=headers, json=data)

def check_loveydovey():
    api_url = "https://www.loveydovey.ai/api/v1/notices?lang=zh_Hant_TW"
    
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 檢查中...")
        # 1. 先去 GitHub 問現在最新的 ID 是什麼
        last_id, sha = get_last_id_from_github()
        
        # 2. 抓取官網 API
        res = requests.get(api_url, timeout=15)
        latest = res.json()['data'][0]
        n_id = str(latest['id'])
        
        # 3. 比對（如果 ID 不同才做事）
        if n_id != last_id:
            print(f"發現新公告！ID: {n_id}")
            title = latest['title']
            clean_content = clean_html(latest.get('content', ''))[:300]
            
            # 發送 Webhook
            payload = {
                "username": "卿我公告搬運工",
                "embeds": [{
                    "title": f"📢 {title}",
                    "description": f"{clean_content}...",
                    "url": "https://www.loveydovey.ai/zh_Hant_TW/notices",
                    "color": 16738740
                }]
            }
            requests.post(WEBHOOK_URL, json=payload)
            
            # 4. 把新 ID 存回 GitHub (下次重啟就不會重複)
            update_id_to_github(n_id, sha)
            print("ID 已同步回 GitHub。")
        else:
            print("沒有新內容。")
            
    except Exception as e:
        print(f"出錯了: {e}")

if __name__ == "__main__":
    while True:
        check_loveydovey()
        time.sleep(3600)
