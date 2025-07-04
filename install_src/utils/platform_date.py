from datetime import datetime

def normalize_date(date_str: str) -> str:
    """
    ISO8601などの形式の日付文字列を 'YYYY-MM-DD' に整形。
    無効な値は空文字列のまま返す。
    """
    if not date_str:
        return ""

    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"[WARN] 日付パース失敗: {date_str} / {e}")
        return date_str
