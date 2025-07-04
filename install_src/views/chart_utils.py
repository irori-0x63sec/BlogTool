import os
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from collections import Counter
from PySide6.QtWidgets import QWidget, QVBoxLayout
import matplotlib.dates as mdates
from datetime import datetime
import math

# ▼ フォント設定共通関数
def apply_japanese_font():
    import platform
    from matplotlib import font_manager

    if platform.system() == "Windows":
        # Windows標準の日本語フォント
        for name in ["Yu Gothic", "Meiryo", "MS Gothic"]:
            try:
                matplotlib.rcParams['font.family'] = name
                print(f"[INFO] Windowsフォント {name} を使用します")
                return
            except Exception:
                continue
    else:
        font_path = "/usr/share/fonts/truetype/ipaexg/ipaexg.ttf"
        if os.path.exists(font_path):
            font_manager.fontManager.addfont(font_path)
            matplotlib.rcParams['font.family'] = font_manager.FontProperties(fname=font_path).get_name()
            print("[INFO] IPAexGothic フォントを適用しました")
            return

    print("[WARN] 日本語フォントが見つからず、DejaVu Sans にフォールバックします")
    matplotlib.rcParams['font.family'] = 'DejaVu Sans'


class PlatformPieChart(QWidget):
    def __init__(self, data, i18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        apply_japanese_font()

        # ▼ プラットフォームごとの followers 数（最大値を代表値とする）
        platform_followers = {}
        for item in data:
            platform = item["platform"]
            raw = item.get("followers", 0)

            try:
                val = int(float(raw))  # NaNやstrに対応
                if math.isnan(val):  # 念のため
                    val = 0
            except:
                val = 0

            if platform not in platform_followers:
                platform_followers[platform] = val
            else:
                platform_followers[platform] = max(platform_followers[platform], val)

        # ▼ 表示用ラベルとサイズ
        labels = [
            f"{platform} ({followers} followers)" if followers > 0 else f"{platform} (0 followers)"
            for platform, followers in platform_followers.items()
        ]
        sizes = list(platform_followers.values())

        # ▼ 描画
        figure = Figure(figsize=(5, 5))
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)

        if any(sizes):  # 1つでも非0があれば通常描画
            ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
            ax.set_title(self.i18n.t("platform_ratio"))
            ax.axis("equal")
        else:
            ax.text(0.5, 0.5, self.i18n.t("no_folloewr"), ha='center', va='center', fontsize=14)
            ax.set_title(self.i18n.t("platform_ratio"))
            ax.axis("off")

        layout = QVBoxLayout()
        layout.addWidget(canvas)
        self.setLayout(layout)


class ArticleViewLineChart(QWidget):
    def __init__(self, data, i18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        apply_japanese_font()

        figure = Figure(figsize=(6, 4))
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)

        date_view_map = {}
        for item in data:
            date_str = item.get("date")
            views = item.get("views", 0)
            if date_str:
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    date_view_map[date] = date_view_map.get(date, 0) + views
                except Exception as e:
                    print(f"[WARN] 日付パース失敗: {date_str} / {e}")

        sorted_dates = sorted(date_view_map.keys())
        sorted_views = [date_view_map[d] for d in sorted_dates]

        ax.plot(sorted_dates, sorted_views, marker="o", linestyle="-")
        ax.set_title(self.i18n.t("views_over_time"))
        ax.set_xlabel(self.i18n.t("date"))
        ax.set_ylabel(self.i18n.t("total_views"))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.grid(True)
        figure.autofmt_xdate()

        layout = QVBoxLayout()
        layout.addWidget(canvas)
        self.setLayout(layout)

class ArticlePlatformViewBarChart(QWidget):
    def __init__(self, data, i18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        apply_japanese_font()

        # 最新記事タイトルの抽出
        latest_title = ""
        latest_date = ""
        for item in data:
            if item.get("date", "") > latest_date:
                latest_date = item["date"]
                latest_title = item["title"]

        # 同じタイトルの記事をプラットフォームごとに集計
        filtered = [item for item in data if item["title"] == latest_title]
        platforms = [item["platform"] for item in filtered]
        views = [item["views"] for item in filtered]

        figure = Figure(figsize=(6, 4))
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)

        ax.bar(platforms, views, width=0.4)  # バーを細く
        ax.set_title(f"{self.i18n.t('view_by_platform')}: {latest_title}")
        ax.set_xlabel(self.i18n.t("platform"))
        ax.set_ylabel(self.i18n.t("views"))
        ax.grid(True)
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))  # 整数だけのY軸

        layout = QVBoxLayout()
        layout.addWidget(canvas)
        self.setLayout(layout)
