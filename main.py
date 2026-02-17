import os
import requests
import time
from google.cloud import firestore

# 從環境變數讀取 Discord webhook URL
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# 初始化 Firestore（需要 service account JSON）
db = firestore.Client()

# 用來記錄已經推送過的公告 ID
sent_ids = set()

def send_to_discord(message: str):
    """把訊息推送到 Discord webhook"""
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

def listen_announcements():
    """監聽 Firestore 公告 collection"""
    def on_snapshot(col_snapshot, changes, read_time):
        for change in changes:
            if change.type.name == "ADDED":
                doc = change.document.to_dict()
                doc_id = change.document.id
                title = doc.get("title", "未命名公告")

                # 去重機制：只推送一次
                if doc_id not in sent_ids:
                    send_to_discord(f"📢 新公告：{title}")
                    sent_ids.add(doc_id)
                else:
                    print(f"跳過重複公告：{title}")

    # 假設公告存在於 "announcements" collection
    col_query = db.collection("announcements")
    col_query.on_snapshot(on_snapshot)

if __name__ == "__main__":
    print("開始監聽公告...")
    listen_announcements()
    # 保持程式持續運行
    while True:
        time.sleep(60)
