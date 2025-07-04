import requests
import re
from utils.token_manager import get_token

DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"

def extract_code_blocks(text: str):
    """コードブロックを退避して、プレースホルダに置換"""
    code_blocks = re.findall(r"```[\s\S]*?```", text)
    placeholders = [f"__CODE_BLOCK_{i}__" for i in range(len(code_blocks))]
    for i, code in enumerate(code_blocks):
        text = text.replace(code, placeholders[i], 1)
    return text, code_blocks, placeholders

def restore_code_blocks(text: str, code_blocks: list, placeholders: list):
    for placeholder, code in zip(placeholders, code_blocks):
        text = text.replace(placeholder, code)
    return text

def translate_text_preserve_code(text: str, source_lang="JA", target_lang="EN"):
    stripped, code_blocks, placeholders = extract_code_blocks(text)
    translated = translate_text(stripped, source_lang, target_lang)
    return restore_code_blocks(translated, code_blocks, placeholders)

def translate_text(text: str, source_lang: str = "JA", target_lang: str = "EN") -> str:
    """
    DeepL APIを使用してテキストを翻訳する。
    source_lang: 元の言語（JAなど）
    target_lang: 翻訳先の言語（ENなど）
    """
    if not text.strip():
        return ""
    
    try:
        auth_key = get_token("deepl")
    except Exception as e:
        raise RuntimeError(f"[DeepL] APIキー取得エラー: {e}")

    params = {
        "auth_key": auth_key,
        "text": text,
        "source_lang": source_lang.upper(),
        "target_lang": target_lang.upper()
    }

    try:
        res = requests.post(DEEPL_API_URL, data=params)
        res.raise_for_status()
        result = res.json()
        return result["translations"][0]["text"]
    except Exception as e:
        raise RuntimeError(f"[DeepL] 翻訳に失敗しました: {e}")
