import markdown2

def convert(md: str) -> str:
    """MarkdownをHTMLに変換（Hashnode用）"""
    return markdown2.markdown(md, extras=["fenced-code-blocks", "code-friendly"])
