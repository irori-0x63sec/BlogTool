from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QSplitter, QPushButton, QHBoxLayout, QDialog
)
from PySide6.QtCore import Qt
from utils.fetch_plugin_loader import discover_fetchers
from views.chart_utils import PlatformPieChart, ArticleViewLineChart, ArticlePlatformViewBarChart
from utils.cache_manager import load_cached_data, save_cached_data
from utils.token_manager import get_token
from utils.platform_date import normalize_date

# ▼ 追加
from dialogs.custom_graph_dialog import CustomGraphDialog
from views.chart_custom import draw_custom_chart



class AnalyzeTab(QWidget):
    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n

        self.all_items = []

        # ▼ グラフタブ（初期化は1回だけ！）
        self.chart_tabs = QTabWidget()
        self.chart_tabs.setTabsClosable(True)
        self.chart_tabs.setMovable(True)
        self.chart_tabs.tabCloseRequested.connect(self.remove_chart_tab)

        # ▼ ボタン
        self.refresh_button = QPushButton(self.i18n.t("reload"))
        self.refresh_button.clicked.connect(self.load_data)

        self.custom_graph_button = QPushButton(self.i18n.t("custom_graph"))
        self.custom_graph_button.clicked.connect(self.open_custom_graph)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.custom_graph_button)
        button_layout.addStretch()

        # ▼ プラットフォームデータ表示用タブ
        self.platform_tabs = QTabWidget()

        # ▼ 上下分割
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.platform_tabs)
        splitter.addWidget(self.chart_tabs)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self.load_data(initial=True)

    def load_data(self, initial=False):
        try:
            self.platform_tabs.clear()
            self.chart_tabs.clear()
            
            if initial:
                cached = load_cached_data()
                if cached is not None:
                    print("[INFO] キャッシュからデータを読み込みました")
                    self.all_items = cached
                    self.display_data(cached)
                    return

            fetchers = discover_fetchers()
            all_items = []

            for name, fetcher in fetchers.items():
                try:
                    token = get_token(name)
                    items = fetcher.fetch(token)
                    all_items.extend(items)

                    table = QTableWidget()
                    table.setColumnCount(4)
                    table.setHorizontalHeaderLabels([
                        self.i18n.t("title"), self.i18n.t("date"), self.i18n.t("likes"), self.i18n.t("views")
                    ])
                    for item in items:
                        item["date"] = normalize_date(item.get("date", ""))   

                    if not items:
                        table.setRowCount(1)
                        item = QTableWidgetItem(self.i18n.t("no_data_available"))
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                        table.setItem(0, 0, item)
                        table.setSpan(0, 0, 1, 4)
                    else:
                        table.setRowCount(len(items))
                        for row, item in enumerate(items):
                            table.setItem(row, 0, QTableWidgetItem(item["title"]))
                            table.setItem(row, 1, QTableWidgetItem(item["date"]))
                            table.setItem(row, 2, QTableWidgetItem(str(item["like"])))
                            table.setItem(row, 3, QTableWidgetItem(str(item["views"])))

                    self.platform_tabs.addTab(table, name.capitalize())

                except Exception as e:
                    print(f"[WARN] {name} の fetch 処理中にエラー発生: {e}")
                    continue

            if all_items:
                save_cached_data(all_items)
                self.all_items = all_items
                self.chart_tabs.clear()
                self.chart_tabs.addTab(PlatformPieChart(all_items, self.i18n), self.i18n.t("platform_ratio"))
                self.chart_tabs.addTab(ArticleViewLineChart(all_items, self.i18n), self.i18n.t("views_over_time"))
            else:
                print("[WARN] グラフ描画対象データが存在しないためスキップします")

        except Exception as e:
            error_table = QTableWidget()
            error_table.setRowCount(1)
            error_table.setColumnCount(1)
            error_table.setItem(0, 0, QTableWidgetItem(f"{self.i18n.t('error')}: {e}"))
            self.platform_tabs.addTab(error_table, self.i18n.t("error"))


    def display_data(self, items):
        self.platform_tabs.clear()
        self.chart_tabs.clear()

        platforms = {}
        for item in items:
            platform = item["platform"]
            platforms.setdefault(platform, []).append(item)

        for name, p_items in platforms.items():
            table = QTableWidget()
            table.setRowCount(len(p_items))
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels([
                self.i18n.t("title"), self.i18n.t("date"), self.i18n.t("likes"), self.i18n.t("views")
            ])

            for row, item in enumerate(p_items):
                table.setItem(row, 0, QTableWidgetItem(item["title"]))
                table.setItem(row, 1, QTableWidgetItem(item["date"]))
                table.setItem(row, 2, QTableWidgetItem(str(item["like"])))
                table.setItem(row, 3, QTableWidgetItem(str(item["views"])))

            self.platform_tabs.addTab(table, name.capitalize())

        all_items_flat = [i for sublist in platforms.values() for i in sublist]
        self.chart_tabs.addTab(PlatformPieChart(all_items_flat, self.i18n), self.i18n.t("platform_ratio"))
        self.chart_tabs.addTab(ArticleViewLineChart(all_items_flat, self.i18n), self.i18n.t("views_over_time"))
        self.chart_tabs.addTab(ArticlePlatformViewBarChart(all_items_flat, self.i18n), "最新記事の閲覧数比較")
    def open_custom_graph(self):
        dialog = CustomGraphDialog(
            indicators=["views", "likes"],
            platforms=list({i["platform"] for i in self.all_items}),
            parent=self
        )
        if dialog.exec_() == QDialog.Accepted:
            selection = dialog.get_selection()
            chart = draw_custom_chart(selection, self.all_items)
            self.chart_tabs.addTab(chart, f"📊 {selection['graph_type']}")
            self.chart_tabs.setCurrentWidget(chart)

    def remove_chart_tab(self, index):
        widget = self.chart_tabs.widget(index)
        if widget:
            widget.deleteLater()
        self.chart_tabs.removeTab(index)