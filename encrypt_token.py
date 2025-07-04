from cryptography.fernet import Fernet

key_path = "/home/kali/.BlogTool/Tokens/fernet.key"
token_path = "/home/kali/.BlogTool/Tokens/key"

# Qiita APIトークン（文字列）をここに貼る
plaintext_token = b""

# キー読み込み（存在しなければエラー）
with open(key_path, "rb") as f:
    key = f.read()

fernet = Fernet(key)
encrypted = fernet.encrypt(plaintext_token)

# 暗号化トークンを保存
with open(token_path, "wb") as f:
    f.write(encrypted)

print("[INFO] 暗号化済みトークンを上書き保存しました！")
