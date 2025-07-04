# token_loader.py の中身（確認済ならOK）
from utils.token_manager import get_token

def load_token(platform: str) -> str:
    return get_token(platform)
