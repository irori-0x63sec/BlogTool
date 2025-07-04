import requests
from utils.token_manager import get_token

def post(payload):
    token = get_token("qiita")

    # ✅ Markdownのまま取得
    content = payload.get_platform_markdown("qiita")
    title = content["title"]
    tags = content["tags"]
    body = content["body_md"]  # ← 変換しない！

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    tag_list = [{"name": tag.strip(), "versions": ["1.0.0"]} for tag in tags.split()]

    data = {
        "title": title,
        "body": body,       # ✅ Markdownをそのまま渡す
        "private": False,
        "tags": tag_list
    }

    res = requests.post("https://qiita.com/api/v2/items", json=data, headers=headers)

    if res.status_code != 201:
        raise Exception(f"投稿失敗: {res.status_code} - {res.text}")

    url = res.json().get("url")
    print(f"✅ Qiita 投稿成功: {url}")
    return url
