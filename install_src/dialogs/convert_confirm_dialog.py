from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QDialogButtonBox, QRadioButton, QGroupBox, QButtonGroup
)

class ConvertConfirmDialog(QDialog):
    def __init__(self, plugins, parent=None):
        super().__init__(parent)
        self.setWindowTitle("投稿前編集の確認")
        self.resize(400, 300)

        self.result = {}  # platform_name: True（編集する） or False（編集しない）

        layout = QVBoxLayout(self)

        self.button_groups = {}

        for plugin in plugins:
            name = getattr(plugin, "__name__", str(plugin))

            group_box = QGroupBox(name)
            hbox = QHBoxLayout()

            edit_radio = QRadioButton("編集する")
            skip_radio = QRadioButton("編集しない")
            edit_radio.setChecked(True)

            hbox.addWidget(edit_radio)
            hbox.addWidget(skip_radio)

            button_group = QButtonGroup(self)
            button_group.addButton(edit_radio, 1)
            button_group.addButton(skip_radio, 0)
            self.button_groups[name] = button_group

            group_box.setLayout(hbox)
            layout.addWidget(group_box)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_edit_targets(self):
        """戻り値：編集対象（True）にしたプラットフォーム名のリスト"""
        edit_targets = []
        for name, group in self.button_groups.items():
            if group.checkedId() == 1:
                edit_targets.append(name)
        return edit_targets
