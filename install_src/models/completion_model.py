# models/completion_model.py
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex

class CompletionModel(QAbstractListModel):
    def __init__(self, entries: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self.entries = entries

    def rowCount(self, parent=QModelIndex()):
        return len(self.entries)

    def data(self, index, role):
        if not index.isValid():
            return None
        snippet, description = self.entries[index.row()]
        if role == Qt.DisplayRole:
            return f"{snippet:<6} | {description}"
        elif role == Qt.UserRole:
            return snippet
        return None
