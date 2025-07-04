import os
import json
from datetime import datetime
from typing import Optional
import requests
from cryptography.fernet import Fernet

CONFIG_DIR = os.path.expanduser("~/.BlogTool/Config")
KEY_PATH = os.path.join(CONFIG_DIR, "fernet.key")


def get_token(platform: str) -> str:
    token_path = os.path.join(CONFIG_DIR, f"{platform}.token")
    if not os.path.exists(KEY_PATH):
        raise FileNotFoundError(f"[ERROR] 暗号鍵が存在しません: {KEY_PATH}")
    with open(KEY_PATH, "rb") as f:
        key = f.read()
    fernet = Fernet(key)
    if not os.path.exists(token_path):
        raise FileNotFoundError(f"[ERROR] {platform} のトークンが存在しません: {token_path}")
    with open(token_path, "rb") as f:
        encrypted = f.read()
    try:
        return fernet.decrypt(encrypted).decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"[ERROR] {platform} トークンの復号に失敗しました: {e}")


def set_token(platform: str, raw_token: str, expires_at: Optional[datetime] = None):
    os.makedirs(CONFIG_DIR, exist_ok=True)

    # 暗号鍵の準備
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
    else:
        with open(KEY_PATH, "rb") as f:
            key = f.read()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(raw_token.encode("utf-8"))
    with open(os.path.join(CONFIG_DIR, f"{platform}.token"), "wb") as f:
        f.write(encrypted)

    # メタ情報も保存
    meta = {"created_at": datetime.now().isoformat()}
    if expires_at:
        meta["expires_at"] = expires_at.isoformat()
    with open(os.path.join(CONFIG_DIR, f"{platform}.meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Hashnode用 publication_id の保存処理を追加
    if platform == "hashnode":
        _fetch_and_save_hashnode_publication_id(raw_token)


import os
import requests
from cryptography.fernet import Fernet

CONFIG_DIR = os.path.expanduser("~/.BlogTool/Config")
KEY_PATH = os.path.join(CONFIG_DIR, "fernet.key")

import os
import requests
from cryptography.fernet import Fernet

CONFIG_DIR = os.path.expanduser("~/.BlogTool/Config")
KEY_PATH = os.path.join(CONFIG_DIR, "fernet.key")

def _fetch_and_save_hashnode_publication_id(token: str):
    """Hashnodeのpublication_idを取得して暗号化保存"""
    query = """
    query {
      me {
        publications(first: 1) {
          edges {
            node {
              id
              title
            }
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post("https://gql.hashnode.com/", json={"query": query}, headers=headers)
        res.raise_for_status()
        data = res.json()

        print("[DEBUG] GraphQL Response:", data)

        if "errors" in data:
            raise Exception(data["errors"])

        edges = data["data"]["me"]["publications"]["edges"]
        if not edges:
            raise Exception("Hashnodeのpublicationが見つかりません")

        pub = edges[0]["node"]
        pub_id = pub["id"]
        pub_title = pub["title"]

        # IDのみ暗号化して保存
        with open(KEY_PATH, "rb") as f:
            key = f.read()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(pub_id.encode("utf-8"))

        with open(os.path.join(CONFIG_DIR, "hashnode.publication.id"), "wb") as f:
            f.write(encrypted)

        # 表示だけに title を使う
        print(f"[INFO] Hashnode publication_id を保存しました: {pub_title} ({pub_id})")

    except Exception as e:
        print(f"[ERROR] Hashnode publication_id の取得に失敗: {e}")




def get_publication_id(platform: str) -> Optional[str]:
    """保存済みのpublication_idを復号して返す"""
    path = os.path.join(CONFIG_DIR, f"{platform}.publication.id")
    if not os.path.exists(path):
        print(f"[INFO] publication_id が見つかりません: {path}")
        return None
    try:
        with open(KEY_PATH, "rb") as f:
            key = f.read()
        fernet = Fernet(key)
        with open(path, "rb") as f:
            decrypted = fernet.decrypt(f.read()).decode("utf-8")
        print(f"[DEBUG] 復号された publication_id: {decrypted}")
        return decrypted
    except Exception as e:
        print(f"[WARN] publication_id の復号に失敗: {e}")
        return None


def get_token_expiry(platform: str) -> datetime | None:
    meta_path = os.path.join(CONFIG_DIR, f"{platform}.meta.json")
    if not os.path.exists(meta_path):
        return None
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "expires_at" in data:
                return datetime.fromisoformat(data["expires_at"])
    except Exception as e:
        print(f"[WARN] トークン期限情報の読み取りに失敗: {e}")
    return None


def token_exists(platform: str) -> bool:
    return os.path.exists(os.path.join(CONFIG_DIR, f"{platform}.token"))


def delete_token(platform: str):
    """指定プラットフォームのトークンファイルを削除"""
    for ext in [".token", ".meta.json", ".publication.id"]:
        path = os.path.join(CONFIG_DIR, f"{platform}{ext}")
        if os.path.exists(path):
            os.remove(path)
