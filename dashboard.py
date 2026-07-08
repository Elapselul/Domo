from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QProgressBar
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

from data import FakeCarData
import theme

from gauges import BoostGauge


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("D-MAX Digital Gauge")
        self.resize(900, 500)
        self.setStyleSheet(f"background-color: {theme.BG}; color: {theme.TEXT};")

        self.title = QLabel("D-MAX")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.title.setStyleSheet(f"color: {theme.ACCENT};")

        self.speed_value = QLabel("0")
        self.speed_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_value.setFont(QFont("Arial", 86, QFont.Weight.Bold))

        self.speed_unit = QLabel("km/h")
        self.speed_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_unit.setFont(QFont("Arial", 22))
        self.speed_unit.setStyleSheet(f"color: {theme.MUTED};")

        self.boost_gauge = BoostGauge()
        self.rpm_card, self.rpm_value = self.make_card("RPM", "0")
        self.coolant_card, self.coolant_value = self.make_card("COOLANT", "0°C")
        self.battery_card, self.battery_value = self.make_card("BATTERY", "0.0V")

        self.boost_bar = QProgressBar()
        self.boost_bar.setRange(0, 24)
        self.boost_bar.setTextVisible(False)
        self.boost_bar.setFixedHeight(28)
        self.boost_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {theme.PANEL};
                border: 1px solid {theme.ACCENT};
                border-radius: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {theme.ACCENT};
                border-radius: 10px;
            }}
        """)

        top_layout = QVBoxLayout()
        top_layout.addWidget(self.title)
        top_layout.addWidget(self.speed_value)
        top_layout.addWidget(self.speed_unit)

        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.boost_gauge)
        middle_layout.addWidget(self.rpm_card)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.coolant_card)
        bottom_layout.addWidget(self.battery_card)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(bottom_layout)
        main_layout.addWidget(self.boost_bar)
        main_layout.setSpacing(18)
        main_layout.setContentsMargins(30, 20, 30, 25)

        self.setLayout(main_layout)

        self.car_data = FakeCarData()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(300)

    def make_card(self, title, value):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.PANEL};
                border-radius: 16px;
                border: 1px solid #1B2A36;
            }}
        """)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {theme.MUTED};")

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Arial", 34, QFont.Weight.Bold))

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)

        return card, value_label

    def update_dashboard(self):
        data = self.car_data.get_data()

        self.speed_value.setText(str(data["speed"]))
        self.boost_gauge.setValue(data["boost"])
        self.rpm_value.setText(str(data["rpm"]))
        self.coolant_value.setText(f'{data["coolant"]}°C')
        self.battery_value.setText(f'{data["battery"]:.1f}V')

        self.boost_bar.setValue(int(data["boost"]))

        if data["coolant"] >= 95:
            self.coolant_value.setStyleSheet(f"color: {theme.DANGER};")
        else:
            self.coolant_value.setStyleSheet(f"color: {theme.TEXT};")