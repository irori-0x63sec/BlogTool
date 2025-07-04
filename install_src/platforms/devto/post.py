import requests
from utils.token_manager import get_token

def post(payload):
    token = get_token("devto")
    headers = {
        "Content-Type": "application/json",
        "api-key": token
    }

    content = payload.get_platform_html("devto")
    title = content["title"]
    tags = content["tags"]
    body_markdown = content["body"]  # ここは変換後のMarkdown

    print("[DEBUG][Devto] title:", title)
    print("[DEBUG][Devto] tags:", tags)
    print("[DEBUG][Devto] body_markdown repr:", repr(body_markdown))

    if not body_markdown.strip():
        raise ValueError("Dev.to投稿用のMarkdownが空です")

    data = {
        "article": {
            "title": title,
            "published": False,
            "tags": tags.split(),
            "body_markdown": body_markdown
        }
    }

    response = requests.post("https://dev.to/api/articles", json=data, headers=headers)
    if response.status_code != 201:
        raise Exception(f"投稿失敗: {response.status_code} - {response.text}")

    url = response.json().get("url")
    print("✅ dev.to 投稿成功:", url)
    return url
