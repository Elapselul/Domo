from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor


class ValueCard(QFrame):
    def __init__(self, title, value="--", unit=""):
        super().__init__()

        self.title_label = QLabel(title)
        self.value_label = QLabel(str(value))
        self.unit_label = QLabel(unit)

        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        self.value_label.setFont(QFont("Inter", 32, QFont.Weight.Bold))
        self.unit_label.setFont(QFont("Inter", 11))

        self.setMinimumHeight(110)

        self.setStyleSheet("""
            QFrame {
                background-color: #101418;
                border: 1px solid #2F3742;
                border-radius: 18px;
            }

            QLabel {
                border: none;
                background: transparent;
            }
        """)

        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(18)
        glow.setOffset(0, 0)
        glow.setColor(QColor("#2F3742"))
        self.setGraphicsEffect(glow)

        self.title_label.setStyleSheet("color: #8A98A8;")
        self.value_label.setStyleSheet("color: #F2F5F7;")
        self.unit_label.setStyleSheet("color: #8A98A8;")

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(2)

        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.value_label)
        layout.addWidget(self.unit_label)
        layout.addStretch()

        self.setLayout(layout)

    def set_value(self, value):
        self.value_label.setText(str(value))