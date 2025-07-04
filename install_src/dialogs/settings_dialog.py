from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QCheckBox, QLabel, QComboBox,
    QPushButton, QDialogButtonBox, QLineEdit, QFormLayout, QMessageBox, QInputDialog
)
from PySide6.QtGui import QKeySequence
from utils.i18n_manager import I18nManager
from utils.shortcut_manager import ShortcutManager
import utils.token_register as token_register
from utils.token_manager import set_token, token_exists

def is_valid_keyseq(seq_str):
    try:
        return QKeySequence(seq_str).count() > 0
    except Exception:
        return False

class SettingsDialog(QDialog):
    def __init__(self, settings, shortcut_manager, parent=None, i18n=None):
        super().__init__(parent)
        self.settings = settings
        self.shortcut_manager = shortcut_manager
        self.i18n = i18n or I18nManager("japanese")
        self.resize(400, 300)
        self.shortcut_edits = {}

        layout = QVBoxLayout(self)

        self.dark_mode_checkbox = QCheckBox(self.i18n.t("enable_dark_mode"))
        self.dark_mode_checkbox.setChecked(
            self.settings.value("dark_mode", "false").lower() == "true"
        )
        layout.addWidget(self.dark_mode_checkbox)

        self.autocomplete_checkbox = QCheckBox(self.i18n.t("enable_autocomplete"))
        self.autocomplete_checkbox.setChecked(
            self.settings.value("autocomplete", "false").lower() == "true"
        )
        layout.addWidget(self.autocomplete_checkbox)

        layout.addWidget(QLabel(self.i18n.t("language")))
        self.language_combo = QComboBox()
        self.language_combo.addItem("日本語", "japanese")
        self.language_combo.addItem("English", "english")

        current_lang = self.settings.value("language", "japanese").lower()
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        layout.addWidget(self.language_combo)

        layout.addWidget(QLabel(self.i18n.t("keyboard_shortcuts")))
        form = QFormLayout()
        shortcuts = {
            "bold": "Ctrl+B",
            "italic": "Ctrl+I",
            "link": "Ctrl+K",
            "code": "Ctrl+Shift+C",
            "img": "Ctrl+Shift+I",
            "hr": "Ctrl+Shift+H",
        }

        for key, default in shortcuts.items():
            edit = QLineEdit(self.settings.value(f"shortcut_{key}", default))
            form.addRow(f"{self.i18n.t('shortcut_' + key)}:", edit)
            self.shortcut_edits[key] = edit

        layout.addLayout(form)

        token_button = QPushButton(self.i18n.t("register_token"))
        token_button.clicked.connect(self.handle_token_registration)
        layout.addWidget(token_button)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def apply(self):
        self.settings.setValue("dark_mode", "true" if self.dark_mode_checkbox.isChecked() else "false")
        self.settings.setValue("autocomplete", "true" if self.autocomplete_checkbox.isChecked() else "false")
        self.settings.setValue("language", self.language_combo.currentData())

        for key, edit in self.shortcut_edits.items():
            seq = edit.text().strip()
            if not is_valid_keyseq(seq):
                QMessageBox.warning(self, self.i18n.t("invalid_shortcut"), f"'{seq}' {self.i18n.t('shortcut_invalid_message')}")
                edit.setFocus()
                return
            self.settings.setValue(f"shortcut_{key}", seq)
            self.shortcut_manager.set(key, seq)

    def handle_token_registration(self):
        try:
            import utils.token_register as token_register
            token_register.register_tokens()

            # ▼ DeepL APIキー未登録なら、登録を促す
            if not token_exists("deepl"):
                key, ok = QInputDialog.getText(
                    self,
                    self.i18n.t("register_deepl_token"),
                    self.i18n.t("input_deepl_token")
                )
                if ok and key.strip():
                    set_token("deepl", key.strip())
                    QMessageBox.information(self, self.i18n.t("done"), self.i18n.t("token_saved"))

            QMessageBox.information(self, self.i18n.t("done"), self.i18n.t("token_register_success"))

        except Exception as e:
            QMessageBox.critical(self, self.i18n.t("error"), f"{self.i18n.t('token_register_error')}:\n{e}")