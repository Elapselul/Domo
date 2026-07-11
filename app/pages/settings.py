from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        label = QLabel("SETTINGS")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Inter", 24, QFont.Weight.Bold))
        label.setStyleSheet("color: #F2F5F7;")

        layout = QVBoxLayout()
        layout.addWidget(label)

        self.setLayout(layout)