from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QCheckBox, QComboBox,
    QDialogButtonBox, QHBoxLayout, QGroupBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate


class CustomGraphDialog(QDialog):
    def __init__(self, indicators, platforms, parent=None):
        super().__init__(parent)
        self.setWindowTitle("カスタムグラフ作成")
        self.resize(400, 300)

        self.indicators = indicators
        self.platforms = platforms
        self.selected = {}

        layout = QVBoxLayout(self)

        # ▼ 指標選択（チェックボックス）
        indicator_box = QGroupBox("表示する指標")
        ind_layout = QVBoxLayout()
        self.indicator_checks = {}
        for ind in indicators:
            cb = QCheckBox(ind)
            cb.setChecked(True)
            self.indicator_checks[ind] = cb
            ind_layout.addWidget(cb)
        indicator_box.setLayout(ind_layout)
        layout.addWidget(indicator_box)

        # ▼ グラフ種類選択
        layout.addWidget(QLabel("グラフ形式："))
        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems(["折れ線グラフ", "棒グラフ", "円グラフ"])
        layout.addWidget(self.graph_type_combo)

        # ▼ プラットフォーム選択
        layout.addWidget(QLabel("プラットフォーム："))
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(platforms)
        layout.addWidget(self.platform_combo)

        # ▼ 日付範囲（オプション）
        date_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())

        date_layout.addWidget(QLabel("期間："))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("～"))
        date_layout.addWidget(self.end_date)
        layout.addLayout(date_layout)

        # ▼ ボタン
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_selection(self):
        selected_indicators = [
            k for k, cb in self.indicator_checks.items() if cb.isChecked()
        ]
        graph_type = self.graph_type_combo.currentText()
        platform = self.platform_combo.currentText()
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        return {
            "indicators": selected_indicators,
            "graph_type": graph_type,
            "platform": platform,
            "start_date": start,
            "end_date": end
        }
