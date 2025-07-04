import requests
import time

def fetch_qiita_items(token):
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "https://qiita.com/api/v2"

    # ユーザーの記事一覧を取得（最大20件）
    res = requests.get(f"{base_url}/authenticated_user/items", headers=headers)
    res.raise_for_status()
    items = res.json()

    detailed_items = []

    for item in items:
        item_id = item["id"]
        detail_url = f"{base_url}/items/{item_id}"
        detail_res = requests.get(detail_url, headers=headers)
        print(detail_res.headers)
        
        # レート制限の残量チェック（900以下で警告）
        remaining = int(detail_res.headers.get("Rate-Remaining", "1000"))
        print(f"[INFO] API残量: {remaining}")
        if remaining < 100:
            raise RuntimeError("API使用量が残り100を切りました。しばらく待ってください。")

        detail_res.raise_for_status()
        detail = detail_res.json()

        # View数を追加（なければ0）
        item["page_views_count"] = detail.get("page_views_count", 0)
        detailed_items.append(item)

        # 念のため少し待つ（0.3秒） ← API連打回避
        time.sleep(0.3)

    return detailed_items

