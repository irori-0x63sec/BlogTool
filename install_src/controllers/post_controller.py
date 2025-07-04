# controllers/post_controller.py

from PySide6.QtWidgets import QMessageBox

def post_to_plugins(payload, plugins, i18n=None):
    for plugin in plugins:
        try:
            plugin.post(payload)
            print(f"[INFO] 投稿成功: {plugin.__name__}")
        except Exception as e:
            print(f"[ERROR] 投稿失敗: {plugin.__name__} - {e}")
            if i18n:
                QMessageBox.critical(
                    None,
                    i18n.t("post_failed_title"),
                    i18n.t("post_failed_message").format(plugin=plugin.__name__, error=e)
                )
