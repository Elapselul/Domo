from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ValueCard(QFrame):
    def __init__(self, title, value="--", unit=""):
        super().__init__()

        self.title = QLabel(title)
        self.value = QLabel(str(value))
        self.unit = QLabel(unit)

        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.value.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.unit.setFont(QFont("Arial", 11))

        self.setStyleSheet("""
    QFrame {
    background-color: #101418;
    border: 1px solid #222831;
    border-radius: 18px;
}

    QFrame:hover {
    border: 1px solid #3A434D;
}

    QLabel {
    color: white;
    border: none;
}
""")

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        layout.addWidget(self.unit)

        self.setLayout(layout)

    def set_value(self, value):
        self.value.setText(str(value))