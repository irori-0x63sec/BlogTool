import importlib
import os

def discover_plugins():
    plugins = []
    base_path = os.path.join(os.path.dirname(__file__), "..", "platforms")
    base_path = os.path.abspath(base_path)

    for name in os.listdir(base_path):
        if name.startswith("__") or name == "base":
            continue

        post_path = os.path.join(base_path, name, "post.py")
        if os.path.isfile(post_path):
            try:
                module = importlib.import_module(f"platforms.{name}.post")
                plugins.append(module)
                print(f"[INFO] プラグイン読み込み成功: {name}")
            except Exception as e:
                print(f"[ERROR] プラグイン読み込み失敗: {name} - {e}")
    return plugins
