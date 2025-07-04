from PySide6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox, QLabel
from PySide6.QtCore import Qt

class PostTargetDialog(QDialog):
    def __init__(self, plugins, parent=None, i18n=None):  # ← i18nを引数に追加
        super().__init__(parent)
        self.i18n = i18n  # ← ここで代入

        self.setWindowTitle(self.i18n.t("select_post_target") if self.i18n else "Select Target")
        self.setMinimumWidth(300)

        self.checkboxes = []

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(self.i18n.t("select_post_target_msg") if self.i18n else "Select the platforms you want to post to:"))

        for plugin in plugins:
            plugin_name = getattr(plugin, "__name__", str(plugin))
            print(f"[DEBUG] プラグイン候補: {plugin_name}")  
            checkbox = QCheckBox(plugin_name)
            checkbox.setChecked(True)
            layout.addWidget(checkbox)
            self.checkboxes.append((plugin, checkbox))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_selected_plugins(self):
        return [plugin for plugin, checkbox in self.checkboxes if checkbox.isChecked()]
