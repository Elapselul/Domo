from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import pyqtSignal


class NavigationBar(QWidget):
    page_selected = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()

        self.setFixedHeight(42)
        self.buttons = []

        pages = [
            ("HOME", 0),
            ("PERFORMANCE", 1),
            ("DIAGNOSTICS", 2),
            ("SETTINGS", 3),
        ]

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        for page_name, page_index in pages:
            button = QPushButton(page_name)
            button.setCheckable(True)
            button.setMinimumHeight(36)

            button.clicked.connect(
                lambda checked,
                index=page_index,
                name=page_name:
                self.select_page(index, name)
            )

            self.buttons.append(button)
            layout.addWidget(button)

        self.setLayout(layout)
        self.buttons[0].setChecked(True)

        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8A98A8;
                border: none;
                border-radius: 9px;
                padding: 6px 10px;
                font-family: Inter;
                font-size: 9px;
                font-weight: 600;
            }

            QPushButton:checked {
                color: #F2F5F7;
                background-color: #151A1F;
                border: 1px solid #343C46;
            }

            QPushButton:hover {
                color: #F2F5F7;
                background-color: #101418;
            }

            QPushButton:pressed {
                background-color: #20262D;
            }
        """)

    def select_page(self, index, name):
        for button_index, button in enumerate(self.buttons):
            button.setChecked(button_index == index)

        self.page_selected.emit(index, name)