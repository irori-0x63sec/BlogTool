import requests
from PySide6.QtWidgets import QMessageBox
from utils.token_manager import get_token

def post_to_platform(platform: str, title: str, tags: str, body: str, endpoint: str, tag_formatter=None, private=True):
    if not title.strip() or not body.strip():
        raise ValueError("タイトルまたは本文が空です")
    if not tags.strip():
        raise ValueError("タグが空です")

    token = get_token(platform)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    tag_data = tag_formatter(tags) if tag_formatter else tags.split()

    data = {
        "title": title,
        "tags": tag_data,
        "body": body,
        "private": private
    }

    res = requests.post(endpoint, headers=headers, json=data)
    if res.status_code == 201:
        print(f"[POST] {platform} 投稿成功")
        print("[POST] URL:", res.json().get("url", "(URLなし)"))
        QMessageBox.information(None, f"{platform} 投稿成功", f"投稿に成功しました：\n{res.json().get('url', '(URLなし)')}")
    else:
        raise RuntimeError(f"{platform} 投稿失敗: {res.status_code} {res.text}")
