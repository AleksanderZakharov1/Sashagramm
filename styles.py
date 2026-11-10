MAIN_STYLE = """
    QMainWindow { background-color: #121212; }
    QWidget {
        background-color: #121212; color: #E0E0E0;
        font-family: 'Segoe UI', Arial;
    }
    QListWidget {
        background-color: #1E1E1E; border: none;
        border-radius: 8px; padding: 5px; outline: none;
    }
    QListWidget::item { padding: 10px; border-radius: 5px; }
    QListWidget::item:selected {
        background-color: #333333; color: white;
    }
    QTextBrowser {
        background-color: #1E1E1E; border: none; border-radius: 8px;
        padding: 10px; selection-background-color: #444444;
        selection-color: white; outline: none;
    }
    QLineEdit {
        background-color: #1E1E1E; border: 1px solid #333333;
        padding: 10px; border-radius: 8px; color: #FFFFFF;
        outline: none;
    }
    QLineEdit:focus { border: 1px solid #555555; }
    QPushButton {
        background-color: #0088cc; border: none; padding: 10px;
        border-radius: 8px; font-weight: bold; color: #FFFFFF;
        outline: none;
    }
    QPushButton:hover { background-color: #0077b3; }
    QPushButton:focus { outline: none; border: none; }
    QTabWidget::pane {
        border: 1px solid #333; background-color: #121212;
    }
    QTabBar::tab {
        background-color: #1E1E1E; color: #FFFFFF;
        padding: 10px; outline: none;
    }
    QTabBar::tab:selected { background-color: #333333; }
    QTableWidget {
        background-color: #1E1E1E; color: #FFFFFF;
        border: none; outline: none;
    }
    QHeaderView::section {
        background-color: #333333; color: #FFFFFF;
        padding: 5px; border: none;
    }
"""

DIALOG_STYLE = """
    QDialog { background-color: #121212; }
    QLabel { color: #FFFFFF; font-size: 14px; font-weight: bold; }
    QLineEdit {
        background-color: #1E1E1E; border: 1px solid #333;
        padding: 8px; border-radius: 5px; color: #FFFFFF;
        outline: none;
    }
    QLineEdit:focus { border: 1px solid #555555; }
    QListWidget {
        background-color: #1E1E1E; border: 1px solid #333;
        border-radius: 5px; color: #FFFFFF; outline: none;
    }
    QListWidget::item { padding: 5px; }
    QListWidget::item:selected {
        background-color: #333333; color: white;
    }
    QPushButton {
        background-color: #0088cc; border: none; padding: 10px;
        border-radius: 5px; font-weight: bold; color: #FFFFFF;
        outline: none;
    }
    QPushButton:hover { background-color: #0077b3; }
    QPushButton:focus { outline: none; border: none; }
"""