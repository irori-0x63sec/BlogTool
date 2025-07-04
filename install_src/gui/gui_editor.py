from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QComboBox
from PySide6.QtGui import QTextCursor
from functools import partial
from utils.shortcut_manager import ShortcutManager

class MarkdownEditorToolbar(QWidget):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.shortcut_manager = ShortcutManager(self.editor)
        self.init_ui()


    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        # ▼ スタイル選択ドロップダウン
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Normal text", "Heading 1", "Heading 2", "Heading 3", "Heading 4"])
        self.style_combo.setFixedWidth(120)
        self.style_combo.currentTextChanged.connect(self.apply_style_format)
        layout.addWidget(self.style_combo)

        # ▼ ボタン：Bold（**text**）
        key = self.shortcut_manager.get("bold", "Ctrl+B")
        btn_bold = QPushButton("B")
        btn_bold.setToolTip(f"Bold ({key})")
        btn_bold.clicked.connect(partial(self.insert_snippet, "**text**"))
        layout.addWidget(btn_bold)

        # ▼ ボタン：Italic（*text*）
        key = self.shortcut_manager.get("italic", "Ctrl+I")
        btn_italic = QPushButton("I")
        btn_italic.setToolTip(f"Italic ({key})")
        btn_italic.clicked.connect(partial(self.insert_snippet, "*text*"))
        layout.addWidget(btn_italic)

        # ▼ ボタン：Link
        key = self.shortcut_manager.get("link", "Ctrl+K")
        btn_link = QPushButton("Link")
        btn_link.setToolTip("Insert link")
        btn_link.setToolTip(f"Insert link ({key})")
        btn_link.clicked.connect(partial(self.insert_snippet, "[text](https://example.com)"))
        layout.addWidget(btn_link)

        # ▼ ボタン：Code
        key = self.shortcut_manager.get("code", "Ctrl+Shift+C")
        btn_code = QPushButton("Code")
        btn_code.setToolTip(f"Insert code ({key})")
        btn_code.clicked.connect(partial(self.insert_snippet, "```python\ncode\n```"))
        layout.addWidget(btn_code)

        # ▼ ボタン：Image
        key = self.shortcut_manager.get("img", "Ctrl+Shift+I")
        btn_img = QPushButton("Img")
        btn_img.setToolTip(f"Insert image ({key})")
        btn_img.clicked.connect(partial(self.insert_snippet, "![alt text](path/to/image.png)"))
        layout.addWidget(btn_img)

        # ▼ ボタン：Horizontal Rule
        key = self.shortcut_manager.get("hr", "Ctrl+Shift+H")
        btn_hr = QPushButton("---")
        btn_hr.setToolTip(f"Insert horizontal rule ({key})")
        btn_hr.clicked.connect(partial(self.insert_snippet, "---"))
        layout.addWidget(btn_hr)


        layout.addStretch()

        self.shortcut_manager.bind("bold", "Ctrl+B", lambda: self.insert_snippet("**text**"))
        self.shortcut_manager.bind("italic", "Ctrl+I", lambda: self.insert_snippet("*text*"))
        self.shortcut_manager.bind("link", "Ctrl+K", lambda: self.insert_snippet("[text](https://example.com)"))
        self.shortcut_manager.bind("code", "Ctrl+Shift+C", lambda: self.insert_snippet("```python\ncode\n```"))
        self.shortcut_manager.bind("img", "Ctrl+Shift+I", lambda: self.insert_snippet("![alt text](path/to/image.png)"))
        self.shortcut_manager.bind("hr", "Ctrl+Shift+H", lambda: self.insert_snippet("---"))

    def insert_snippet(self, text):
        cursor = self.editor.textCursor()
        cursor.insertText(text)
        self.editor.setTextCursor(cursor)

    def apply_style_format(self, style_text):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.StartOfBlock)  # 行頭へ（Block = 行扱い）
        cursor.select(QTextCursor.LineUnderCursor)
        selected_text = cursor.selectedText().lstrip('# ').strip()

        heading_map = {
            "Normal text": "",
            "Heading 1": "# ",
            "Heading 2": "## ",
            "Heading 3": "### ",
            "Heading 4": "#### ",
        }

        prefix = heading_map.get(style_text, "")
        cursor.removeSelectedText()
        cursor.insertText(f"{prefix}{selected_text}")
        self.editor.setTextCursor(cursor)