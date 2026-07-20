from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
)

from app.widgets.navigation_bar import NavigationBar
from app.widgets.status_chip import StatusChip


class HeaderBar(QWidget):
    page_selected = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()

        self.setFixedHeight(52)

        logo_path = (
            Path(__file__).resolve().parent.parent
            / "assets"
            / "logo.svg"
        )

        self.logo_label = QSvgWidget(str(logo_path))
        self.logo_label.setFixedSize(165, 36)

        self.navigation = NavigationBar()
        self.navigation.page_selected.connect(
            self.page_selected.emit
        )

        self.status_chip = StatusChip(
            "Simulator",
            "warning",
        )

        header_content = QWidget()

        content_layout = QHBoxLayout(header_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        content_layout.addWidget(
            self.logo_label,
            alignment=Qt.AlignmentFlag.AlignVCenter,
        )

        content_layout.addStretch(1)

        content_layout.addWidget(
            self.navigation,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        content_layout.addStretch(1)

        content_layout.addWidget(
            self.status_chip,
            alignment=(
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter
            ),
        )

        self.divider = QFrame()
        self.divider.setFixedHeight(1)
        self.divider.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 28);
                border: none;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        main_layout.addWidget(header_content)
        main_layout.addWidget(self.divider)

    def set_status(self, text, status):
        self.status_chip.set_status(text, status)