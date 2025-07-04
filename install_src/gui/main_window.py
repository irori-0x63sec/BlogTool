
# === main_window.py ===

# ─────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────
import sys
import os
import markdown2
from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTabWidget, QLabel, QDockWidget, QMessageBox, QTextBrowser, QDialog
)
from PySide6.QtGui import QAction, QTextOption
from PySide6.QtCore import Qt, QTimer, QSettings

from utils.plugin_loader import discover_plugins
from utils.i18n_manager import I18nManager
from utils.file_io import save_markdown_file, open_markdown_file
from utils.token_manager import get_token_expiry
from views.analyze_tab import AnalyzeTab
from views.markdown_editor import MarkdownEditor
from gui.gui_editor import MarkdownEditorToolbar
from style.theme_manager import apply_preferences
from controllers.post_controller import post_to_plugins
from dialogs.post_target_dialog import PostTargetDialog
from dialogs.post_confirm_dialog import PostConfirmDialog
from dialogs.convert_confirm_dialog import ConvertConfirmDialog

# ─────────────────────────────────────
# MAIN WINDOW CLASS
# ─────────────────────────────────────
class BlogToolMainWindow(QMainWindow):
    # ────────────────
    # INIT & SETUP
    # ────────────────
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlogTool v1.2.17")
        self.resize(1000, 700)
        self.setup()

    def setup(self):
        self.config_path = os.path.expanduser("~/.BlogTool/Config/preferences.ini")
        self.settings = QSettings(self.config_path, QSettings.IniFormat)
        apply_preferences(self, self.settings)

        self.plugins = discover_plugins()
        self.i18n = I18nManager(self.settings.value("language", "japanese").lower())
        self.i18n.load()

        self.init_menu()
        self.init_ui()
        self.restore_layout()
        self.refresh_ui_texts()
        self.init_events()
        self.check_token_expiry()  

    # ────────────────
    # UI INITIALIZATION
    # ────────────────
    def init_ui(self):
        central = QWidget()
        central_layout = QVBoxLayout(central)
        self.setCentralWidget(central)

        # Editor
        self.editor = MarkdownEditor(
            enable_autocomplete=self.settings.value("autocomplete", "false").lower() == "true",
            shortcut_autocomplete=self.settings.value("shortcut_autocomplete", "Ctrl+Space")
        )

        self.preview = QTextBrowser()
        self.preview.setOpenExternalLinks(True)
        self.preview.setObjectName("preview")
        self.preview.setWordWrapMode(QTextOption.WordWrap)

        self.toolbar_dock = QDockWidget("Editor Tools", self)
        self.toolbar_dock.setObjectName("EditorTools")
        self.editor_toolbar = MarkdownEditorToolbar(self.editor)
        self.toolbar_dock.setWidget(self.editor_toolbar)
        self.toolbar_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.TopDockWidgetArea, self.toolbar_dock)

        dock1 = QDockWidget("Prot", self)
        dock1.setObjectName("Prot")
        dock1.setWidget(self.editor)
        dock1.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

        dock2 = QDockWidget("Preview", self)
        dock2.setObjectName("Preview")
        dock2.setWidget(self.preview)
        dock2.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

        self.editor_tab = QMainWindow()
        self.editor_tab.setDockNestingEnabled(True)
        self.editor_tab.addDockWidget(Qt.LeftDockWidgetArea, dock1)
        self.editor_tab.addDockWidget(Qt.RightDockWidgetArea, dock2)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.editor_tab, "Editor")

        self.analyze_tab = AnalyzeTab(self.i18n)
        self.tabs.addTab(self.analyze_tab, "Analyze")

        input_row = QHBoxLayout()
        self.title_label = QLabel(self.i18n.t("title") + ":")
        self.tags_label = QLabel(self.i18n.t("tags") + ":")
        self.title_input = QLineEdit()
        self.tags_input = QLineEdit()
        input_row.addWidget(self.title_label)
        input_row.addWidget(self.title_input)
        input_row.addWidget(self.tags_label)
        input_row.addWidget(self.tags_input)

        tool_row = QHBoxLayout()
        self.post_button = QPushButton(self.i18n.t("post"))
        self.save_button = QPushButton(self.i18n.t("save"))
        self.open_button = QPushButton(self.i18n.t("open"))
        tool_row.addStretch()
        tool_row.addWidget(self.open_button)
        tool_row.addWidget(self.save_button)
        tool_row.addWidget(self.post_button)
        
        central_layout.addLayout(input_row)
        central_layout.addWidget(self.tabs)
        central_layout.addLayout(tool_row)

    # ────────────────
    # MENU / EVENTS / PREVIEW
    # ────────────────
    def init_menu(self):
        menubar = self.menuBar()
        setting_menu = menubar.addMenu(self.i18n.t("menu_setting"))
        pref_action = QAction(self.i18n.t("preferences"), self)
        pref_action.triggered.connect(self.show_preferences_dialog)
        setting_menu.addAction(pref_action)

    def init_events(self):
        self.post_button.clicked.connect(self.handle_post)
        self.save_button.clicked.connect(self.handle_save)
        self.open_button.clicked.connect(self.handle_open)
        self.typing_timer = QTimer()
        self.typing_timer.setSingleShot(True)
        self.typing_timer.timeout.connect(self.update_preview)
        self.editor.textChanged.connect(self.schedule_preview)

    def schedule_preview(self):
        self.typing_timer.start(500)

    def update_preview(self):
        html = markdown2.markdown(self.editor.toPlainText(), extras=["break-on-newline"])
        self.preview.setHtml(html)
    
    @staticmethod
    def extract_plugin_name(plugin):
        name = getattr(plugin, "__name__", str(plugin))
        return name.split('.')[-2] if '.' in name else name

    # ────────────────
    # POST / SAVE / OPEN
    # ────────────────
    def handle_post(self):
        from models.post_payload import PostPayload
        target_dialog = PostTargetDialog(self.plugins, self, self.i18n)
        if target_dialog.exec_() != QDialog.Accepted:
            return

        selected_plugins = target_dialog.get_selected_plugins()
        if not selected_plugins:
            QMessageBox.warning(self, self.i18n.t("warning"), self.i18n.t("no_target_selected"))
            return

        confirm_dialog = ConvertConfirmDialog(selected_plugins, self)
        if confirm_dialog.exec_() != QDialog.Accepted:
            return

        edit_targets = confirm_dialog.get_edit_targets()
        payload = PostPayload(
            default_title=self.title_input.text(),
            default_tags=self.tags_input.text(),
            default_body_md=self.editor.toPlainText()
        )

        plugin_map = {self.extract_plugin_name(p): p for p in selected_plugins}


        # 非編集対象のMarkdownをセット
#        for name in plugin_map.keys():
#            if name not in edit_targets:
#                payload.set_platform_markdown(
#                    name,
#                    title=payload.default_title,
#                    tags=payload.default_tags,
#                    body_md=payload.default_body_md
#                )
#               print(f"[DEBUG] {name} - Markdown set: title='{payload.default_title}', tags='{payload.default_tags}'")

        # 編集対象があればダイアログで編集
        if edit_targets:
            confirm_dialog = PostConfirmDialog(edit_targets, payload, plugin_map, parent=self)
            if confirm_dialog.exec_() != QDialog.Accepted:
                return

        # 全対象に対してconvert実行 → HTML保存
        for name, plugin in plugin_map.items():
            convert = getattr(plugin, "convert", lambda md: md)
            content = payload.get_platform_markdown(name)
            html_body = convert(content["body_md"])
            payload.set_platform_html(
                name,
                title=content["title"],
                tags=content["tags"],
                body_html=html_body
            )

        # 最終送信前の内容確認
        for name in plugin_map:
            print(f"[DEBUG] FINAL PAYLOAD for {name} → {payload.get_platform_html(name)}")

        post_to_plugins(payload, selected_plugins)


    def handle_save(self):
        save_markdown_file(
            title=self.title_input.text(),
            tags=self.tags_input.text(),
            body=self.editor.toPlainText()
        )

    def handle_open(self):
        title, tags, body = open_markdown_file()
        print(f"[DEBUG] handle_open(): title={title}, tags={tags}, body starts with={body[:50]}")

        if title is not None:
            self.title_input.setText(title)
            self.tags_input.setText(tags)
            self.editor.setPlainText(body)

    def translate_with_deepl(self):
        from utils.token_manager import token_exists, set_token
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        from utils.deepl_translator import translate_text
        import re

        # ▼ Deepl APIキー未登録なら入力ダイアログ表示
        if not token_exists("deepl"):
            key, ok = QInputDialog.getText(self, self.i18n.t("deepl_register_title"), self.i18n.t("deepl_input_prompt"))
            if ok and key.strip():
                set_token("deepl", key.strip())
                QMessageBox.information(self, self.i18n.t("done"), self.i18n.t("deepl_saved"))
            else:
                return

        # ▼ 言語設定に基づいて翻訳方向を決定
        source_lang = "JA" if self.i18n.language.lower() == "japanese" else "EN"
        target_lang = "EN" if source_lang == "JA" else "JA"

        # ▼ タイトル・タグを翻訳
        try:
            translated_title = translate_text(self.title_input.text(), source_lang, target_lang)
            translated_tags = translate_text(self.tags_input.text(), source_lang, target_lang)
            self.title_input.setText(translated_title)
            self.tags_input.setText(translated_tags)
        except Exception as e:
            QMessageBox.critical(self, self.i18n.t("error"), f"{self.i18n.t('deepl_error')}:\n{e}")
            return

        # ▼ 本文：コードブロック除外して翻訳
        original_text = self.editor.toPlainText()
        parts = re.split(r"(```.*?```)", original_text, flags=re.DOTALL)
        translated_parts = []

        for part in parts:
            if part.startswith("```") and part.endswith("```"):
                translated_parts.append(part)
            else:
                try:
                    translated = translate_text(part, source_lang=source_lang, target_lang=target_lang)
                    translated_parts.append(translated)
                except Exception as e:
                    QMessageBox.critical(self, self.i18n.t("error"), f"{self.i18n.t('deepl_error')}:\n{e}")
                    return

        self.editor.setPlainText("".join(translated_parts))


    # ────────────────
    # I18N / SETTINGS
    # ────────────────
    def refresh_ui_texts(self):
        self.setWindowTitle(self.i18n.t("app_title"))
        self.title_label.setText(self.i18n.t("title") + ":")
        self.tags_label.setText(self.i18n.t("tags") + ":")
        self.post_button.setText(self.i18n.t("post"))
        self.save_button.setText(self.i18n.t("save"))
        self.open_button.setText(self.i18n.t("open"))
        self.tabs.setTabText(0, self.i18n.t("editor_tab"))
        self.tabs.setTabText(1, self.i18n.t("analyze_tab"))
        self.toolbar_dock.setWindowTitle(self.i18n.t("editor_tools"))
        self.editor_tab.findChild(QDockWidget, "Prot").setWindowTitle(self.i18n.t("editor_area"))
        self.editor_tab.findChild(QDockWidget, "Preview").setWindowTitle(self.i18n.t("preview_area"))

    def apply_preferences(self):
        dark = self.settings.value("dark_mode", "false").lower() == "true"
        if dark:
            self.setStyleSheet("QWidget { background-color: #2b2b2b; color: white; }")
        else:
            self.setStyleSheet("")

    def show_preferences_dialog(self):
        from dialogs.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.settings, self.editor_toolbar.shortcut_manager, self, self.i18n)
        if dialog.exec_():
            dialog.apply()
            self.i18n.language = self.settings.value("language", "Japanese")
            self.i18n.load()
            self.refresh_ui_texts()
            apply_preferences(self, self.settings)
            QMessageBox.information(self, self.i18n.t("restart_title"), self.i18n.t("settings_applied"))

    def show_completion(self):
        if self.editor:
            self.editor.manual_completion()


    # ────────────────
    # TOKEN
    # ────────────────
    def check_token_expiry(self):
        now = datetime.now()
        for plugin in self.plugins:
            platform = getattr(plugin, "__name__", None)
            if not platform:
                continue

            expires = get_token_expiry(platform)
            if expires and now + timedelta(days=3) >= expires:
                remaining = (expires - now).days
                msg = f"{platform} のトークン有効期限があと {remaining} 日です。\n更新しますか？"

                result = QMessageBox.question(
                    self,
                    "トークンの有効期限が近づいています",
                    msg,
                    QMessageBox.Yes | QMessageBox.No
                )

                if result == QMessageBox.Yes:
                    from dialogs.token_dialog import TokenDialog
                    dlg = TokenDialog(self)
                    dlg.exec_()

    # ────────────────
    # WINDOW STATE SAVE / RESTORE
    # ────────────────
    def closeEvent(self, event):
        self.save_layout()
        super().closeEvent(event)

    def save_layout(self):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("lastTabIndex", self.tabs.currentIndex())

    def restore_layout(self):
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        window_state = self.settings.value("windowState")
        if window_state:
            self.restoreState(window_state)

        last_index = self.settings.value("lastTabIndex", 0, type=int)
        self.tabs.setCurrentIndex(last_index)

# ─────────────────────────────────────
# APP LAUNCHER
# ─────────────────────────────────────
def launch_main():
    app = QApplication(sys.argv)
    win = BlogToolMainWindow()
    win.show()
    sys.exit(app.exec())  