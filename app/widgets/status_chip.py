from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QFont


class StatusChip(QLabel):
    COLOURS = {
        "success": "#27AE60",
        "warning": "#F2C94C",
        "danger": "#EB5757",
    }

    def __init__(self, text="Disconnected", status="danger"):
        super().__init__()

        self.setFont(QFont("Inter", 9, QFont.Weight.Bold))
        self.set_status(text, status)

    def set_status(self, text, status):
        colour = self.COLOURS.get(status, "#EB5757")

        self.setText(f"●  {text}")

        self.setStyleSheet(f"""
            QLabel {{
                color: white;
                background: transparent;
                border: none;
                padding: 0px;
            }}
        """)

        # Colour only the bullet
        self.setText(
            f'<span style="color:{colour};">●</span> {text}'
        )