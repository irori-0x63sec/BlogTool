import importlib.util
import os

def discover_fetchers():
    fetchers = {}
    platform_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "platforms"))

    print(f"[DEBUG] プラットフォームディレクトリ: {platform_dir}")

    for platform_name in os.listdir(platform_dir):
        platform_path = os.path.join(platform_dir, platform_name)

        if platform_name in ["base", "__pycache__"] or platform_name.startswith("."):
            print(f"[SKIP] 除外ディレクトリ: {platform_name}")
            continue
        if not os.path.isdir(platform_path):
            continue

        fetch_path = os.path.join(platform_path, "fetch.py")
        if not os.path.isfile(fetch_path):
            print(f"[SKIP] fetch.py が見つからない: {fetch_path}")
            continue

        print(f"[TRY] {platform_name} の fetch.py を読み込み中...")

        spec = importlib.util.spec_from_file_location(f"{platform_name}_fetch", fetch_path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            if hasattr(module, "fetch") and callable(module.fetch):
                # base を意図的に弾くチェック
                if "base" not in module.fetch.__code__.co_filename:
                    fetchers[platform_name] = module
                    print(f"[INFO] Fetch モジュール読込成功: {platform_name}")
                else:
                    print(f"[SKIP] fetch.py は base ディレクトリ: {platform_name}")
            else:
                print(f"[WARN] fetch 関数なし: {platform_name}")
        except Exception as e:
            print(f"[ERROR] {platform_name}/fetch.py 読み込み失敗: {e}")

    return fetchers

