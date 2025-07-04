from cryptography.fernet import Fernet
import os

# パス設定
key_path = os.path.expanduser("~/.BlogTool/Tokens/fernet.key")

# ディレクトリが無ければ作る
os.makedirs(os.path.dirname(key_path), exist_ok=True)

# 新しい鍵を生成
key = Fernet.generate_key()

# 保存
with open(key_path, "wb") as f:
    f.write(key)

print("[INFO] 新しいFernetキーを生成して保存しました！")

