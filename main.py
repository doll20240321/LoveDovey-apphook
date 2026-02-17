def check_loveydovey():
    api_url = "https://firestore.googleapis.com/google.firestore.v1.Firestore/Listen/channel?database=projects/reelso-prod/databases/(default)&...
"
    webhook_url = os.getenv('WEBHOOK_URL')
    
    # 偽裝成一般的 Chrome 瀏覽器，防止被防火牆擋掉
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 正在檢查公告...")
        response = requests.get(api_url, headers=headers, timeout=15)
        
        # 檢查 HTTP 狀態碼
        if response.status_code != 200:
            print(f"伺服器回報錯誤碼: {response.status_code}")
            return

        # 嘗試解析 JSON
        try:
            data = response.json()
        except Exception:
            print("抓到的內容不是 JSON 格式！內容如下：")
            print(response.text[:200]) # 印出前 200 個字看看它是什麼
            return

        latest = data['data'][0]
        n_id = str(latest['id'])
        
        # --- 底下邏輯不變 ---
        last_id = r.get('last_notice_id')
        if last_id:
            last_id = last_id.decode('utf-8')

        if n_id != last_id:
            print(f"發現新公告：{latest['title']}")
            clean_content = clean_html(latest.get('content', ''))[:300]
            
            payload = {
                "username": "卿卿我我情報官",
                "embeds": [{
                    "title": f"📢 {latest['title']}",
                    "description": f"{clean_content}...",
                    "url": "https://www.loveydovey.ai/zh_Hant_TW/notices",
                    "color": 16738740
                }]
            }
            requests.post(webhook_url, json=payload)
            r.set('last_notice_id', n_id)
            print("ID 已同步至 Redis。")
        else:
            print("目前無新公告。")

    except Exception as e:
        print(f"網路請求發生異常: {e}")
