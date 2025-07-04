from PySide6.QtWidgets import QPlainTextEdit, QCompleter
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QKeySequence
from models.completion_model import CompletionModel

MARKDOWN_KEYWORDS = [
    ("# ", "見出しレベル1"),
    ("## ", "見出しレベル2"),
    ("### ", "見出しレベル3"),
    ("#### ", "見出しレベル4"),
    ("- ", "箇条書き（ダッシュ）"),
    ("* ", "箇条書き（アスタリスク）"),
    ("> ", "引用"),
    ("`code`", "インラインコード"),
    ("```python\n\n```", "コードブロック（Python）"),
    ("---", "水平線"),
    ("[リンクテキスト](https://example.com)", "リンク"),
    ("![画像説明](path/to/image.png)", "画像埋め込み"),
    ("**強調**", "太字"),
    ("*強調*", "斜体"),
    ("1. ", "番号付きリスト"),
    ("- [ ] ", "チェックリスト（未完了）"),
    ("- [x] ", "チェックリスト（完了）"),
]

class MarkdownEditor(QPlainTextEdit):
    def __init__(self, parent=None, enable_autocomplete=True, shortcut_autocomplete="Ctrl+Space"):
        super().__init__(parent)
        self.enable_autocomplete = enable_autocomplete
        self.shortcut_seq = QKeySequence(shortcut_autocomplete)

        self.setFocusPolicy(Qt.StrongFocus)
        self.completer = QCompleter()
        self.completer.setModel(CompletionModel(MARKDOWN_KEYWORDS))
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.insert_completion)

    def insert_completion(self, completion):
        cursor = self.textCursor()
        prefix = self.text_under_cursor()

        if prefix:  # prefix が存在する場合のみ削除
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, len(prefix))
            cursor.removeSelectedText()

        model_index = self.completer.popup().currentIndex()
        snippet = self.completer.completionModel().data(model_index, Qt.UserRole)
        cursor.insertText(snippet)
        self.setTextCursor(cursor)
        self.completer.popup().hide()

def keyPressEvent(self, event):
    if self.enable_autocomplete and self.completer.popup().isVisible():
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.insert_completion(self.completer.currentCompletion())
            self.completer.popup().hide()
            return  # Enter押下で新行に行かないように

    # Ctrl+Space で補完発動
    if self.enable_autocomplete and event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Space:
        print("[DEBUG] Ctrl+Spaceで補完発動")
        self.manual_completion()
        return

    super().keyPressEvent(event)

    if not self.enable_autocomplete:
        return

    # 自動補完（キー押下後に毎回判定）
    prefix = self.text_under_cursor()
    if prefix:
        self.completer.setCompletionPrefix(prefix)
        self.completer.complete()
        self._move_popup()
    else:
        self.completer.popup().hide()

    def manual_completion(self):
        pass

    def text_under_cursor(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        return cursor.selectedText().strip()

    def _move_popup(self):
        popup = self.completer.popup()
        popup_pos = self.mapToGlobal(self.cursorRect().bottomRight())
        popup.move(popup_pos)
        popup.raise_()
        popup.setFocus()
        popup.show()

    def focusOutEvent(self, event):
        if self.completer and self.completer.popup().isVisible():
            self.completer.popup().hide()
        super().focusOutEvent(event)