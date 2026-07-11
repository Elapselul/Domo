from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from PyQt6.QtCore import Qt

from app.widgets.circular_gauge import CircularGauge
from app.widgets.value_card import ValueCard


class HomePage(QWidget):
    def __init__(self, vehicle_service):
        super().__init__()

        self.vehicle_service = vehicle_service

        self.setStyleSheet(
            "background-color: #05070A; color: white;"
        )


        self.boost_gauge = CircularGauge(
            "BOOST",
            "PSI",
            0,
            24,
            warning=18,
            danger=22,
        )

        self.rpm = ValueCard("RPM", "--", "rpm")
        self.coolant = ValueCard("COOLANT", "--", "°C")
        self.battery = ValueCard(
            "BATTERY",
            "--",
            "V",
            decimals=1,
        )
        self.egt = ValueCard("EGT", "--", "°C")
        self.trans_temp = ValueCard("TRANS TEMP", "--", "°C")
        self.oil_pressure = ValueCard(
            "OIL PRESSURE",
            "--",
            "psi",
        )

        grid = QGridLayout()
        grid.addWidget(self.rpm, 0, 0)
        grid.addWidget(self.coolant, 0, 1)
        grid.addWidget(self.battery, 0, 2)
        grid.addWidget(self.egt, 1, 0)
        grid.addWidget(self.trans_temp, 1, 1)
        grid.addWidget(self.oil_pressure, 1, 2)
        grid.setSpacing(10)

        layout = QVBoxLayout()
        layout.addWidget(
            self.boost_gauge,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        layout.addLayout(grid)

        layout.setContentsMargins(14, 10, 14, 12)
        layout.setSpacing(10)

        self.setLayout(layout)

    def update_data(self, data):

        self.boost_gauge.set_value(data.boost)
        self.rpm.set_value(data.rpm)
        self.coolant.set_value(data.coolant)
        self.battery.set_value(data.battery)
        self.egt.set_value(data.egt)
        self.trans_temp.set_value(data.trans_temp)
        self.oil_pressure.set_value(data.oil_pressure)