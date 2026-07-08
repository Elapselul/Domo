from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        title = QLabel("DOMO")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 42, QFont.Weight.Bold))

        slogan = QLabel("What a weapon.")
        slogan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slogan.setFont(QFont("Arial", 18))

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(slogan)

        self.setLayout(layout)