from PySide6.QtWidgets import QApplication, QPlainTextEdit, QCompleter
from PySide6.QtCore import QStringListModel, Qt
from PySide6.QtGui import QTextCursor
import sys

class TestEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()

        keywords = ["# ", "## ", "### ", "- ", "* ", "> ", "`code`", "---"]
        self.completer = QCompleter(keywords, self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setWidget(self)
        self.completer.activated.connect(self.insert_completion)

    def insert_completion(self, completion):
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor) 
        cursor.removeSelectedText()
        cursor.insertText(completion)
        self.setTextCursor(cursor)

    def keyPressEvent(self, event):
        if self.completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape):
                event.ignore()
                return
        super().keyPressEvent(event)

        prefix = self.text_under_cursor()
        if prefix and len(prefix) >= 1:
            self.completer.setCompletionPrefix(prefix)
            self.completer.complete()  # self.cursorRect() は無しでまず動作確認

    def text_under_cursor(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 10)  # ← 修正ポイント
        return cursor.selectedText()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = TestEditor()
    editor.resize(600, 400)
    editor.show()
    sys.exit(app.exec())
