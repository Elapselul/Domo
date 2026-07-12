from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.theme import colours
from app.theme import sizes


class HealthRow(QFrame):
    STATUS_COLOURS = {
        "good": colours.SUCCESS,
        "warning": colours.WARNING,
        "danger": colours.DANGER,
        "neutral": colours.TEXT_SECONDARY,
    }

    def __init__(self, name, message="Normal", status="good"):
        super().__init__()

        self.name_label = QLabel(name)
        self.message_label = QLabel(message)
        self.dot_label = QLabel("●")

        self.name_label.setFont(
            QFont("Inter", 10, QFont.Weight.DemiBold)
        )
        self.message_label.setFont(QFont("Inter", 9))
        self.dot_label.setFont(
            QFont("Inter", 10, QFont.Weight.Bold)
        )

        self.name_label.setStyleSheet(
            f"color: {colours.TEXT};"
        )
        self.message_label.setStyleSheet(
            f"color: {colours.TEXT_SECONDARY};"
        )

        self.setStyleSheet(f"""
            HealthRow {{
                background-color: {colours.PANEL};
                border: 1px solid {colours.BORDER};
                border-radius: {sizes.BUTTON_RADIUS}px;
            }}

            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 7, 10, 7)
        layout.setSpacing(8)

        layout.addWidget(self.dot_label)
        layout.addWidget(self.name_label)
        layout.addStretch()
        layout.addWidget(self.message_label)

        self.setLayout(layout)
        self.set_status(message, status)

    def set_status(self, message, status):
        status_colour = self.STATUS_COLOURS.get(
            status,
            colours.TEXT_SECONDARY,
        )

        self.message_label.setText(message)
        self.dot_label.setStyleSheet(
            f"color: {status_colour};"
        )


class DiagnosticsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.connection_status = QLabel(
            "● SIMULATOR CONNECTED"
        )
        self.connection_status.setFont(
            QFont("Inter", 10, QFont.Weight.DemiBold)
        )
        self.connection_status.setStyleSheet(
            f"color: {colours.WARNING};"
        )

        self.battery_health = HealthRow(
            "Battery",
            "Normal",
            "good",
        )
        self.coolant_health = HealthRow(
            "Coolant",
            "Normal",
            "good",
        )
        self.oil_health = HealthRow(
            "Oil Pressure",
            "Normal",
            "good",
        )
        self.map_health = HealthRow(
            "MAP Sensor",
            "Normal",
            "good",
        )
        self.maf_health = HealthRow(
            "MAF Sensor",
            "Normal",
            "good",
        )
        self.boost_health = HealthRow(
            "Boost Control",
            "Normal",
            "good",
        )

        health_grid = QGridLayout()
        health_grid.setSpacing(8)

        health_grid.addWidget(
            self.battery_health,
            0,
            0,
        )
        health_grid.addWidget(
            self.coolant_health,
            0,
            1,
        )
        health_grid.addWidget(
            self.oil_health,
            0,
            2,
        )
        health_grid.addWidget(
            self.map_health,
            1,
            0,
        )
        health_grid.addWidget(
            self.maf_health,
            1,
            1,
        )
        health_grid.addWidget(
            self.boost_health,
            1,
            2,
        )

        self.code_panel = QFrame()
        self.code_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {colours.PANEL};
                border: 1px solid {colours.BORDER};
                border-radius: {sizes.CARD_RADIUS}px;
            }}
        """)

        self.code_label = QLabel(
            "No active diagnostic trouble codes"
        )
        self.code_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.code_label.setFont(
            QFont("Inter", 10, QFont.Weight.DemiBold)
        )
        self.code_label.setStyleSheet(
            f"color: {colours.TEXT_SECONDARY};"
        )

        code_layout = QVBoxLayout()
        code_layout.setContentsMargins(12, 10, 12, 10)
        code_layout.addWidget(self.code_label)

        self.code_panel.setLayout(code_layout)

        self.read_button = QPushButton("READ CODES")
        self.clear_button = QPushButton("CLEAR CODES")

        self.read_button.setFixedHeight(36)
        self.clear_button.setFixedHeight(36)

        button_style = f"""
            QPushButton {{
                background-color: {colours.PANEL};
                color: {colours.TEXT};
                border: 1px solid {colours.BORDER};
                border-radius: {sizes.BUTTON_RADIUS}px;
                font-family: Inter;
                font-size: 10px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background-color: {colours.PANEL_ACTIVE};
                border-color: {colours.BORDER_ACTIVE};
            }}

            QPushButton:pressed {{
                background-color: {colours.BORDER};
            }}
        """

        self.read_button.setStyleSheet(button_style)
        self.clear_button.setStyleSheet(button_style)

        self.read_button.clicked.connect(self.read_codes)
        self.clear_button.clicked.connect(self.clear_codes)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addWidget(self.read_button)
        button_layout.addWidget(self.clear_button)

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        layout.addWidget(self.connection_status)
        layout.addLayout(health_grid)
        layout.addWidget(self.code_panel, stretch=1)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def update_data(self, data):
        self.update_battery_health(data.battery)
        self.update_coolant_health(data.coolant)
        self.update_oil_health(data.oil_pressure)
        self.update_map_health(data.map)
        self.update_maf_health(data.maf)
        self.update_boost_health(
            data.boost,
            data.commanded_boost,
        )

    def update_battery_health(self, voltage):
        if voltage < 12.0:
            self.battery_health.set_status(
                f"{voltage:.1f} V - Battery low",
                "danger",
            )

        elif voltage < 13.2:
            self.battery_health.set_status(
                f"{voltage:.1f} V - Charging low",
                "warning",
            )

        elif voltage <= 14.8:
            self.battery_health.set_status(
                f"{voltage:.1f} V - Charging",
                "good",
            )

        else:
            self.battery_health.set_status(
                f"{voltage:.1f} V - High voltage",
                "warning",
            )

    def update_coolant_health(self, coolant):
        if coolant >= 110:
            self.coolant_health.set_status(
                f"{coolant}°C - Overheating",
                "danger",
            )

        elif coolant >= 100:
            self.coolant_health.set_status(
                f"{coolant}°C - Hot",
                "warning",
            )

        elif coolant >= 75:
            self.coolant_health.set_status(
                f"{coolant}°C - Normal",
                "good",
            )

        else:
            self.coolant_health.set_status(
                f"{coolant}°C - Warming up",
                "neutral",
            )

    def update_oil_health(self, pressure):
        if pressure < 10:
            self.oil_health.set_status(
                f"{pressure} psi - Critical",
                "danger",
            )

        elif pressure < 20:
            self.oil_health.set_status(
                f"{pressure} psi - Low",
                "warning",
            )

        else:
            self.oil_health.set_status(
                f"{pressure} psi - Healthy",
                "good",
            )

    def update_map_health(self, value):
        if value < 80 or value > 300:
            self.map_health.set_status(
                f"{value} kPa - Check",
                "warning",
            )
        else:
            self.map_health.set_status(
                f"{value} kPa",
                "good",
            )

    def update_maf_health(self, value):
        if value < 0:
            self.maf_health.set_status(
                "Invalid reading",
                "danger",
            )
        else:
            self.maf_health.set_status(
                f"{value} g/s",
                "good",
            )

    def update_boost_health(
        self,
        actual,
        commanded,
    ):
        difference = actual - commanded

        if abs(difference) < 1:
            self.boost_health.set_status(
                f"{difference:+.1f} PSI",
                "good",
            )

        elif abs(difference) < 3:
            self.boost_health.set_status(
                f"{difference:+.1f} PSI",
                "warning",
            )

        else:
            self.boost_health.set_status(
                f"{difference:+.1f} PSI",
                "danger",
            )

    def read_codes(self):
        self.code_label.setText(
            "No active diagnostic trouble codes"
        )
        self.code_label.setStyleSheet(
            f"color: {colours.TEXT_SECONDARY};"
        )

    def clear_codes(self):
        self.code_label.setText("Codes cleared")
        self.code_label.setStyleSheet(
            f"color: {colours.SUCCESS};"
        )