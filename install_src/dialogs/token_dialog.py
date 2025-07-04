from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from utils.i18n_manager import i18n
from utils.token_manager import save_token_encrypted

class TokenDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.t("register_qiita_token"))

        self.label = QLabel(i18n.t("input_qiita_token"))
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)

        self.save_button = QPushButton(i18n.t("save"))
        self.save_button.clicked.connect(self.save_token)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.token_input)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def save_token(self):
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, i18n.t("warning"), i18n.t("token_empty"))
            return

        save_token_encrypted(token)
        QMessageBox.information(self, i18n.t("done"), i18n.t("token_saved"))
        self.accept()
