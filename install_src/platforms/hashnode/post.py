import requests
from utils.token_manager import get_token, get_publication_id

def post(payload):
    token = get_token("hashnode")
    publication_id = get_publication_id("hashnode")

    content = payload.get_platform_markdown("hashnode")
    title = content["title"]
    tags_str = content.get("tags", "")
    tags_list = [{"name": tag.strip(), "slug": tag.strip()} for tag in tags_str.split()] if tags_str else []
    body_md = content["body_md"]

    print(f"[DEBUG] hashnode - Markdown set: title='{title}', tags={tags_list!r}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 1: Create draft
    draft_query = """
    mutation CreateDraft($input: CreateDraftInput!) {
      createDraft(input: $input) {
        draft {
          id
          slug
          title
        }
      }
    }
    """
    draft_variables = {
        "input": {
            "title": title,
            "contentMarkdown": body_md,
            "publicationId": publication_id,
            "tags": tags_list
        }
    }

    res = requests.post("https://gql.hashnode.com/", json={
        "query": draft_query,
        "variables": draft_variables
    }, headers=headers)
    print("[DEBUG] Draft creation response:", res.text)
    res.raise_for_status()
    data = res.json()
    if "errors" in data:
        raise RuntimeError(f"下書き作成失敗: {data['errors']}")

    draft_id = data["data"]["createDraft"]["draft"]["id"]

    # Step 2: Publish draft
    publish_query = """
    mutation PublishDraft($input: PublishDraftInput!) {
      publishDraft(input: $input) {
        post {
          slug
          url
        }
      }
    }
    """
    publish_variables = {
        "input": {
            "draftId": draft_id
        }
    }

    res = requests.post("https://gql.hashnode.com/", json={
        "query": publish_query,
        "variables": publish_variables
    }, headers=headers)
    print("[DEBUG] Publish response:", res.text)
    res.raise_for_status()
    data = res.json()
    if "errors" in data:
        raise RuntimeError(f"公開失敗: {data['errors']}")

    url = data["data"]["publishDraft"]["post"]["url"]
    print("✅ Hashnode 投稿成功:", url)
    return url
