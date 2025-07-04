# platforms/qiita/convert.py

import markdown2

def convert(md: str) -> str:
    """
    Qiita用のMarkdown → HTML変換処理
    """
    html = markdown2.markdown(md, extras=["fenced-code-blocks", "break-on-newline"])
    return html
