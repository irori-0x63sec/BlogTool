# utils/shortcut_manager.py
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import QSettings

class ShortcutManager:
    def __init__(self, parent_widget):
        self.settings = QSettings("~/.BlogTool/Config/preferences.ini", QSettings.IniFormat)
        self.parent = parent_widget
        self.shortcuts = {}  # name → QShortcut

    def bind(self, name: str, default: str, callback):
        keyseq = self.settings.value(f"shortcut_{name}", default)
        shortcut = QShortcut(QKeySequence(keyseq), self.parent)
        shortcut.activated.connect(callback)
        self.shortcuts[name] = shortcut

    def get(self, name: str, default: str) -> str:
        return self.settings.value(f"shortcut_{name}", default)

    def set(self, name: str, keyseq: str):
        self.settings.setValue(f"shortcut_{name}", keyseq)
        if name in self.shortcuts:
            self.shortcuts[name].setKey(QKeySequence(keyseq))

    def all_shortcuts(self):
        return self.shortcuts
