from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget

from app.widgets.header_bar import HeaderBar

from app.pages.home import HomePage
from app.pages.performance import PerformancePage
from app.pages.diagnostics import DiagnosticsPage
from app.pages.settings import SettingsPage


class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DOMO")
        self.resize(800, 480)

        self.setStyleSheet("""
            QWidget {
                background-color: #05070A;
            }
        """)

        self.header = HeaderBar()
        self.header.page_selected.connect(self.change_page)

        self.pages = QStackedWidget()
        self.pages.addWidget(HomePage())
        self.pages.addWidget(PerformancePage())
        self.pages.addWidget(DiagnosticsPage())
        self.pages.addWidget(SettingsPage())

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 6, 10, 10)
        layout.setSpacing(6)

        layout.addWidget(self.header)
        layout.addWidget(self.pages, stretch=1)

        self.setLayout(layout)

    def change_page(self, page_index, page_name):
        self.pages.setCurrentIndex(page_index)