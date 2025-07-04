# post_confirm_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout, QComboBox, QMessageBox
)
from utils.deepl_translator import translate_text, translate_text_preserve_code

class PostConfirmDialog(QDialog):
    def __init__(self, platforms, payload, plugin_map, parent=None):
        super().__init__(parent)
        self.platforms = platforms  # ['qiita', 'devto', 'hashnode'] 等
        self.payload = payload
        self.plugin_map = plugin_map
        self.editors = {}
        self.language_combos = {}

        self.setWindowTitle("投稿前編集")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        for platform in platforms:
            layout.addWidget(QLabel(f"\u25c6 {platform}"))

            # 翻訳言語選択
            lang_row = QHBoxLayout()
            lang_label = QLabel("翻訳先:")
            lang_combo = QComboBox()
            lang_combo.addItem("日本語", "JA")
            lang_combo.addItem("English", "EN")
            lang_combo.addItem("翻訳しない", "NONE")
            lang_combo.setCurrentIndex(2)

            self.language_combos[platform] = lang_combo
            lang_combo.currentIndexChanged.connect(lambda _, p=platform: self.translate_body(p))

            lang_row.addWidget(lang_label)
            lang_row.addWidget(lang_combo)
            layout.addLayout(lang_row)

            # 本文編集欄
            editor = QTextEdit()
            content = payload.get_platform_markdown(platform)
            editor.setPlainText(content.get("body_md", ""))
            self.editors[platform] = editor
            layout.addWidget(editor)

        # OK / Cancel
        button_row = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("キャンセル")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        button_row.addStretch()
        button_row.addWidget(cancel_btn)
        button_row.addWidget(ok_btn)
        layout.addLayout(button_row)

    def translate_body(self, platform):
        combo = self.language_combos[platform]
        target_lang = combo.currentData()
        if target_lang == "NONE":
            return
        try:
            original = self.editors[platform].toPlainText()
            translated = translate_text_preserve_code(original, "JA", target_lang)
            self.editors[platform].setPlainText(translated)
        except Exception as e:
            QMessageBox.critical(self, "翻訳エラー", str(e))

    def get_edit_targets(self):
        return self.platforms

    def accept(self):
        for platform in self.platforms:
            body_md = self.editors[platform].toPlainText()
            combo = self.language_combos[platform]
            target_lang = combo.currentData()
            title = self.payload.default_title
            tags = self.payload.default_tags
            if target_lang != "NONE":
                try:
                    title = translate_text(title, "JA", target_lang)
                    tags = translate_text(tags, "JA", target_lang)
                except Exception as e:
                    QMessageBox.critical(self, "翻訳エラー", str(e))
                    continue
            self.payload.set_platform_markdown(platform, title, tags, body_md)
            plugin = self.plugin_map.get(platform)
            if plugin:
                convert = getattr(plugin, "convert", lambda md: md)
                html = convert(body_md)
                self.payload.set_platform_html(platform, title, tags, html)
        super().accept()
