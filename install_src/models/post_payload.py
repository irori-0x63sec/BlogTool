class PostPayload:
    def __init__(self, default_title: str, default_tags: str, default_body_md: str):
        self.default_title = default_title
        self.default_tags = default_tags
        self.default_body_md = default_body_md

        # 編集対象（Markdown）
        self.per_platform_md = {}  # platform_name → {title, tags, body_md}

        # 投稿用（HTML）
        self.per_platform_html = {}  # platform_name → {title, tags, body}

    def _normalize_name(self, platform: str) -> str:
        return platform.split(".")[-2] if "." in platform else platform

    def set_platform_markdown(self, platform: str, title: str, tags: str, body_md: str):
        """プラットフォーム別の編集Markdownを保存"""
        norm = self._normalize_name(platform)
        self.per_platform_md[norm] = {
            "title": title,
            "tags": tags,
            "body_md": body_md
        }

    def get_platform_markdown(self, platform: str):
        """Markdown取得（未編集ならデフォルトを返す）"""
        norm = self._normalize_name(platform)
        return self.per_platform_md.get(norm, {
            "title": self.default_title,
            "tags": self.default_tags,
            "body_md": self.default_body_md
        })

    def set_platform_html(self, platform: str, title: str, tags: str, body_html: str):
        """変換後のHTMLを保存（投稿時に使う）"""
        norm = self._normalize_name(platform)
        self.per_platform_html[norm] = {
            "title": title,
            "tags": tags,
            "body": body_html
        }

    def get_platform_html(self, platform: str):
        """HTML取得（投稿時用）"""
        norm = self._normalize_name(platform)
        return self.per_platform_html.get(norm, {
            "title": self.default_title,
            "tags": self.default_tags,
            "body": "⚠️ no converted content"
        })

    def to_dict(self):
        """CSV保存やログ出力用の汎用dict形式（HTMLベース）"""
        return self.per_platform_html.copy()
