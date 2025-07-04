def apply_preferences(window, settings):
    dark = settings.value("dark_mode", "false").lower() == "true"
    if dark:
        window.setStyleSheet("""
            QWidget { background-color: #2b2b2b; color: white; font-size: 12px; }
            QMenuBar::item:selected { background: rgba(100, 100, 100, 180); }
            QTabBar::tab {
                background: #2b2b2b; color: white;
                padding: 6px 12px;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:selected { background: #3a3a3a; }
            QTabBar::tab:hover { background: #444; }
            QPlainTextEdit {
                border: 1px solid #2e2e2e;
                background-color: #1e1e1e;
            }
            QLabel#preview {
                border: 1px solid #2e2e2e;
                background-color: #1e1e1e;
            }
            QLineEdit, QPushButton {
                font-size: 12px;
                padding: 4px;
                border: 1px solid #666;
            }
            QDockWidget {
                border: none;
            }
        """)
    else:
        window.setStyleSheet("")
