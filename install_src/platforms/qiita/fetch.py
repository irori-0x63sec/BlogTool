from datetime import datetime
import requests
import time
from utils.token_manager import get_token

def fetch(token):
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "https://qiita.com/api/v2"

    res = requests.get(f"{base_url}/authenticated_user/items", headers=headers)
    res.raise_for_status()
    items = res.json()

    unified = []

    for item in items:
        item_id = item["id"]
        detail_res = requests.get(f"{base_url}/items/{item_id}", headers=headers)
        detail = detail_res.json()

        # 統一書式に変換
        unified.append({
            "platform" : "qiita",
            "title": item["title"],
            "date": item["created_at"].split("T")[0],  # ISO日付を整形
            "like": item.get("likes_count", 0),
            "views": detail.get("page_views_count", 0),
            "followers": item.get("followers_count", 0)
        })

        time.sleep(0.3)

    return unified

