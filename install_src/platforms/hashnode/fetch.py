import requests
from utils.token_manager import get_token
from utils.platform_date import normalize_date

API_URL = "https://gql.hashnode.com/"

def fetch(_=None) -> list[dict]:
    """Hashnode の記事データを取得して整形"""

    token = get_token("hashnode")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    query = """
    query {
      me {
        username
        followersCount
        publications(first: 1) {
          edges {
            node {
              posts(first: 20) {
                edges {
                  node {
                    title
                    slug
                    views
                    reactionCount
                    publishedAt
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    res = requests.post(API_URL, json={"query": query}, headers=headers)
    res.raise_for_status()
    data = res.json()

    if "errors" in data:
        raise Exception(f"Fetch失敗: {data['errors']}")

    username = data["data"]["me"]["username"]
    try:
        followers = int(float(data["data"]["me"].get("followersCount", 0)))
    except (ValueError, TypeError):
        followers = 0

    post_edges = data["data"]["me"]["publications"]["edges"][0]["node"]["posts"]["edges"]

    return [
        {
            "platform": "hashnode",
            "title": post["node"]["title"],
            "views": post["node"].get("views", 0),
            "like": post["node"].get("reactionCount", 0),
            "url": f"https://{username}.hashnode.dev/{post['node']['slug']}",
            "date": normalize_date(post["node"].get("publishedAt", "")),
            "followers": followers
        }
        for post in post_edges
    ]
