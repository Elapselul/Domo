from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from app.widgets.navigation_bar import NavigationBar
from app.widgets.status_chip import StatusChip


class HeaderBar(QWidget):
    page_selected = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()

        self.setFixedHeight(52)

        self.logo_label = QLabel("DOMO")
        self.logo_label.setFont(
            QFont("Inter", 18, QFont.Weight.Bold)
        )
        self.logo_label.setStyleSheet("""
            color: #F2F5F7;
            background: transparent;
            border: none;
        """)

        self.navigation = NavigationBar()
        self.navigation.page_selected.connect(
            self.page_selected.emit
        )

        self.status_chip = StatusChip(
            "Simulator",
            "warning",
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(self.logo_label)
        layout.addSpacing(12)
        layout.addWidget(self.navigation, stretch=1)
        layout.addWidget(self.status_chip)

        self.setLayout(layout)

    def set_status(self, text, status):
        self.status_chip.set_status(text, status)