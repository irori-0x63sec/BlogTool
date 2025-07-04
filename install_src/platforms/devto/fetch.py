# platforms/devto/fetch.py

import requests
from utils.token_manager import get_token

def fetch(token=None):
    token = token or get_token("devto")
    headers = {
        "api-key": token
    }

    url = "https://dev.to/api/articles/me"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Fetch failed: {response.status_code} - {response.text}")
    
    articles = response.json()
    result = []

    for article in articles:
        result.append({
            "platform": "devto",
            "title": article.get("title", "Untitled"),
            "date": article.get("published_at", "")[:10],  # YYYY-MM-DD
            "like": article.get("positive_reactions_count", 0),
            "views": article.get("page_views_count", 0),
            "followers": article.get("followers_count", 0)
        })

    return result
