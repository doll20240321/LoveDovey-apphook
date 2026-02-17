import requests
import os
import re # 用來洗掉 HTML 標籤的工具

def clean_html(raw_html):
    # 這個正則表達式會把 <...> 這種標籤都刪掉，只留下純文字
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def check_loveydovey():
    # 這裡就是你撿到的那個寶藏網址
    api_url = "https://www.loveydovey.ai/api/v1/notices?lang=zh_Hant_TW"
    webhook_url = os.getenv('WEBHOOK_URL_2')
    last_id_file = "last_id_loveydovey.txt"

    try:
        response = requests.get(api_url, timeout=15)
        data = response.json()
        
        # 抓取第一則（最新）公告
        latest = data['data'][0]
        n_id = str(latest['id'])
        title = latest['title']
        
        # 抓取內容並清洗 HTML 標籤
        raw_content = latest.get('content', '')
        clean_content = clean_html(raw_content)
        
        # Discord 訊息不能太長，我們取前 300 個字
        summary = clean_content[:300] + ("..." if len(clean_content) > 300 else "")

        # 讀取舊 ID 做比對
        last_id = ""
        if os.path.exists(last_id_file):
            with open(last_id_file, "r") as f:
                last_id = f.read().strip()

        if n_id != last_id:
            print(f"發現新公告：{title}")
            payload = {
                "username": "卿卿我我情報官",
                "embeds": [{
                    "title": f"📢 {title}",
                    "description": summary,
                    "url": "https://www.loveydovey.ai/zh_Hant_TW/notices",
                    "color": 16738740, # 粉紅色
                    "footer": {"text": f"公告發布日期: {latest.get('created_at', '未知')}"}
                }]
            }
            requests.post(webhook_url, json=payload)
            
            # 存下新 ID
            with open(last_id_file, "w") as f:
                f.write(n_id)
        else:
            print("目前沒有新公告。")
            
    except Exception as e:
        print(f"執行失敗: {e}")

if __name__ == "__main__":
    check_loveydovey()
