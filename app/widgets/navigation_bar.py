from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
)


class NavigationBar(QWidget):
    page_selected = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()

        self.buttons = []

        self.pages = [
            "Home",
            "Performance",
            "Diagnostics",
            "Settings",
        ]

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(48)

        for index, page_name in enumerate(self.pages):
            button = QPushButton(page_name)

            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            button.setCheckable(True)

            button.clicked.connect(
                lambda checked, i=index, name=page_name:
                self.select_page(i, name)
            )

            self.buttons.append(button)
            layout.addWidget(button)

        self.select_page(0, self.pages[0])

    def select_page(self, index, page_name):
        for button_index, button in enumerate(self.buttons):
            selected = button_index == index

            button.setChecked(selected)

            if selected:
                button.setStyleSheet("""
                    QPushButton {
                        color: #F2F5F7;
                        background: transparent;
                        border: none;
                        border-bottom: 2px solid #F2F5F7;
                        padding: 8px 3px 7px 3px;
                        font-family: Inter;
                        font-size: 11px;
                        font-weight: 600;
                    }
                """)

                glow = QGraphicsDropShadowEffect(button)
                glow.setBlurRadius(14)
                glow.setOffset(0, 2)
                glow.setColor(
                    QColor(255, 255, 255, 95)
                )

                button.setGraphicsEffect(glow)

            else:
                button.setStyleSheet("""
                    QPushButton {
                        color: rgba(242, 245, 247, 135);
                        background: transparent;
                        border: none;
                        border-bottom: 2px solid transparent;
                        padding: 8px 3px 7px 3px;
                        font-family: Inter;
                        font-size: 11px;
                        font-weight: 500;
                    }

                    QPushButton:hover {
                        color: rgba(242, 245, 247, 210);
                    }
                """)

                button.setGraphicsEffect(None)

        self.page_selected.emit(index, page_name)