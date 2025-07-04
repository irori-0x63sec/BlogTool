import os
import json
from datetime import datetime

CACHE_DIR = os.path.expanduser("~/.BlogTool/Cache")
CACHE_FILE = os.path.join(CACHE_DIR, "analyze_qiita.json")


def load_cached_data():
    """キャッシュが存在し、当日のものであれば読み込んで返す"""
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("last_updated") == datetime.now().strftime("%Y-%m-%d"):
            print("[INFO] キャッシュからデータを読み込みます")
            return data.get("items", [])
        else:
            print("[INFO] キャッシュは古いため無視します")
    except Exception as e:
        print(f"[ERROR] キャッシュ読み込みエラー: {e}")

    return None


def save_cached_data(items):
    """データをキャッシュとして保存する"""
    os.makedirs(CACHE_DIR, exist_ok=True)

    data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "items": items
    }

    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("[INFO] キャッシュに保存しました")
    except Exception as e:
        print(f"[ERROR] キャッシュ保存エラー: {e}")

