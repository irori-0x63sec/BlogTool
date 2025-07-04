import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


def draw_custom_chart(selection: dict, items: list[dict]) -> QWidget:
    # フォント設定
    font_path = "/usr/share/fonts/truetype/ipaexg/ipaexg.ttf"
    if os.path.exists(font_path):
        from matplotlib import font_manager
        font_prop = font_manager.FontProperties(fname=font_path)
        matplotlib.rcParams["font.family"] = font_prop.get_name()
    else:
        print("[WARN] IPAexGothic not found. Falling back to DejaVu Sans.")
        matplotlib.rcParams["font.family"] = "DejaVu Sans"

    indicators = selection["indicators"]
    graph_type = selection["graph_type"]
    platform = selection["platform"]
    start_date = datetime.strptime(selection["start_date"], "%Y-%m-%d").date()
    end_date = datetime.strptime(selection["end_date"], "%Y-%m-%d").date()

    filtered = [
        item for item in items
        if item["platform"] == platform and
           start_date <= datetime.strptime(item["date"], "%Y-%m-%d").date() <= end_date
    ]

    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)

    if not filtered:
        label = QLabel("No data available")
        label.setAlignment(Qt.AlignCenter)
        chart_widget = QWidget()
        layout = QVBoxLayout(chart_widget)
        layout.addWidget(label)
        return chart_widget

    if graph_type == "Bar":
        labels = [item["title"] for item in filtered]
        x = range(len(labels))
        width = 0.8 / len(indicators)

        for i, key in enumerate(indicators):
            values = [item.get(key, 0) for item in filtered]
            ax.bar([xi + i * width for xi in x], values, width=width, label=key)

        ax.set_xticks([xi + width * (len(indicators) - 1) / 2 for xi in x])
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_title(f"{platform} - Metrics (Bar Chart)")
        ax.legend()

    elif graph_type == "Line":
        date_keys = sorted(set(item["date"] for item in filtered))
        date_objs = [datetime.strptime(d, "%Y-%m-%d").date() for d in date_keys]

        for key in indicators:
            y_values = []
            for d in date_keys:
                total = sum(item.get(key, 0) for item in filtered if item["date"] == d)
                y_values.append(total)
            ax.plot(date_objs, y_values, marker="o", label=key)

        ax.set_title(f"{platform} - Metrics Over Time (Line Chart)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        ax.legend()
        ax.grid(True)

    elif graph_type == "Pie":
        if len(indicators) != 1:
            ax.text(0.5, 0.5, "Only one metric allowed in Pie Chart", ha="center", va="center")
        else:
            key = indicators[0]
            values = [item.get(key, 0) for item in filtered]
            labels = [item["title"] for item in filtered]
            ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=140)
            ax.set_title(f"{platform} - {key} Distribution")
            ax.axis("equal")
            ax.set_xticks([])
            ax.set_yticks([])

    canvas = FigureCanvas(fig)
    chart_widget = QWidget()
    layout = QVBoxLayout(chart_widget)
    layout.addWidget(canvas)
    return chart_widget
