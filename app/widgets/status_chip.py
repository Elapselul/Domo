from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class StatusChip(QFrame):
    COLOURS = {
        "success": "#4CAF50",
        "warning": "#F2A43A",
        "danger": "#EB5757",
        "neutral": "#8A98A8",
    }

    def __init__(self, text="Simulator", status="warning"):
        super().__init__()

        self.dot = QLabel("●")
        self.text_label = QLabel(text)

        self.dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dot.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        self.text_label.setFont(QFont("Inter", 11, QFont.Weight.DemiBold))

        self.setStyleSheet("""
            QFrame {
                background-color: #101418;
                border: 1px solid #2F3742;
                border-radius: 14px;
            }

            QLabel {
                border: none;
                background: transparent;
                color: #F2F5F7;
            }
        """)

        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(14)
        glow.setOffset(0, 0)
        glow.setColor(QColor(90, 100, 112, 110))
        self.setGraphicsEffect(glow)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 12, 5)
        layout.setSpacing(6)
        layout.addWidget(self.dot)
        layout.addWidget(self.text_label)

        self.setLayout(layout)

        self.set_status(text, status)

    def set_status(self, text, status="neutral"):
        colour = self.COLOURS.get(status, self.COLOURS["neutral"])

        self.text_label.setText(text)

        self.dot.setStyleSheet(f"""
            color: {colour};
            border: none;
            background: transparent;
        """)

        self.text_label.setStyleSheet("""
            color: #F2F5F7;
            border: none;
            background: transparent;
        """)

        glow = self.graphicsEffect()
        if glow:
            glow.setColor(QColor(colour))