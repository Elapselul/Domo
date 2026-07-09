from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from app.widgets.circular_gauge import CircularGauge
from app.widgets.value_card import ValueCard
from app.services.vehicle_service import VehicleService


class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        self.vehicle_service = VehicleService()

        self.setStyleSheet("background-color: #05070A; color: white;")

        title = QLabel("DOMO")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))

        status = QLabel("● Connected")
        status.setAlignment(Qt.AlignmentFlag.AlignRight)
        status.setFont(QFont("Arial", 12))

        header = QHBoxLayout()
        header.addWidget(title)
        header.addWidget(status)

        self.boost_gauge = CircularGauge("MAP", "PSI", 0, 24, warning=18, danger=22)

        self.rpm = ValueCard("RPM", "--", "rpm")
        self.coolant = ValueCard("COOLANT", "--", "°C")
        self.battery = ValueCard("BATTERY", "--", "V")
        self.iat = ValueCard("IAT", "--", "°C")
        self.map = ValueCard("MAP", "--", "kPa")
        self.maf = ValueCard("MAF", "--", "g/s")

        grid = QGridLayout()
        grid.addWidget(self.rpm, 0, 0)
        grid.addWidget(self.coolant, 0, 1)
        grid.addWidget(self.battery, 0, 2)
        grid.addWidget(self.iat, 1, 0)
        grid.addWidget(self.map, 1, 1)
        grid.addWidget(self.maf, 1, 2)
        grid.setSpacing(14)

        layout = QVBoxLayout()
        layout.addLayout(header)
        layout.addWidget(self.boost_gauge, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(grid)
        layout.setContentsMargins(24, 18, 24, 24)
        layout.setSpacing(18)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(16)

    def update_data(self):
        data = self.vehicle_service.get_current_data()

        self.boost_gauge.set_value(data["boost"])
        self.rpm.set_value(data["rpm"])
        self.coolant.set_value(data["coolant"])
        self.battery.set_value(data["battery"])
        self.iat.set_value(data["iat"])
        self.map.set_value(data["map"])
        self.maf.set_value(data["maf"])