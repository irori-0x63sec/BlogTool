from abc import ABC, abstractmethod

class BasePublisher(ABC):
    """
    投稿プラグイン共通のインターフェース。
    すべてのプラットフォームプラグインはこれを継承すること。
    """

    @abstractmethod
    def post(self, title: str, tags: str, body: str):
        """
        各プラットフォームに記事を投稿する。

        :param title: 記事タイトル
        :param tags: カンマ区切りのタグ文字列
        :param body: Markdown本文
        """
        pass
