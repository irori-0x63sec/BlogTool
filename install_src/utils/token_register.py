import os
from PySide6.QtWidgets import QInputDialog, QMessageBox, QLineEdit
from utils.token_manager import set_token, token_exists, delete_token

PLATFORM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "platforms"))

def register_tokens(parent=None):
    """
    各プラットフォームのAPIトークンを登録 or 再登録。
    """
    if not os.path.exists(PLATFORM_DIR):
        QMessageBox.critical(parent, "エラー", f"platforms ディレクトリが見つかりません:\n{PLATFORM_DIR}")
        return

    for name in os.listdir(PLATFORM_DIR):
        path = os.path.join(PLATFORM_DIR, name)
        if not os.path.isdir(path) or name.lower() == "base":
            continue

        # トークンが存在する場合：削除確認
        if token_exists(name):
            if QMessageBox.question(
                parent,
                f"{name} トークン管理",
                f"プラットフォーム '{name}' のトークンは既に登録されています。\n削除して再登録しますか？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            ) == QMessageBox.No:
                continue
            delete_token(name)

        # トークンの新規入力
        token, ok = QInputDialog.getText(
            parent,
            f"{name} トークン登録",
            f"{name} の API トークンを入力してください：",
            QLineEdit.Password
        )

        if ok and token:
            try:
                set_token(name, token)
                QMessageBox.information(parent, "トークン登録", f"{name} のトークンを登録しました。")
            except Exception as e:
                QMessageBox.critical(parent, "エラー", f"{name} のトークン登録に失敗しました:\n{e}")
