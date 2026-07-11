from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
)

from app.widgets.value_card import ValueCard
from app.widgets.graph_widget import GraphWidget

from app.theme import colours
from app.theme import sizes


class PerformancePage(QWidget):
    GRAPH_SIGNALS = {
        "BOOST": {
            "field": "boost",
            "title": "BOOST HISTORY",
            "unit": "PSI",
            "minimum": 0,
            "maximum": 24,
        },
        "EGT": {
            "field": "egt",
            "title": "EGT HISTORY",
            "unit": "°C",
            "minimum": 200,
            "maximum": 800,
        },
        "RPM": {
            "field": "rpm",
            "title": "RPM HISTORY",
            "unit": "RPM",
            "minimum": 0,
            "maximum": 4500,
        },
        "COOLANT": {
            "field": "coolant",
            "title": "COOLANT HISTORY",
            "unit": "°C",
            "minimum": 60,
            "maximum": 120,
        },
        "TRANS": {
            "field": "trans_temp",
            "title": "TRANS TEMP HISTORY",
            "unit": "°C",
            "minimum": 40,
            "maximum": 130,
        },
        "OIL": {
            "field": "oil_pressure",
            "title": "OIL PRESSURE HISTORY",
            "unit": "PSI",
            "minimum": 0,
            "maximum": 100,
        },
    }

    def __init__(self, vehicle_service, data_logger):
        self.vehicle_service = vehicle_service
        self.data_logger = data_logger

        super().__init__()

        self.vehicle_service = vehicle_service
        self.selected_signal = "BOOST"
        self.graph_buttons = []

        self.peaks = {
            "boost": 0.0,
            "rpm": 0,
            "egt": 0,
            "coolant": 0,
            "trans_temp": 0,
            "oil_pressure": 999,
        }

        self.peak_boost = ValueCard(
            "PEAK BOOST",
            "--",
            "PSI",
            decimals=1,
        )
        self.peak_rpm = ValueCard(
            "PEAK RPM",
            "--",
            "rpm",
        )
        self.peak_egt = ValueCard(
            "PEAK EGT",
            "--",
            "°C",
        )
        self.max_coolant = ValueCard(
            "MAX COOLANT",
            "--",
            "°C",
        )
        self.max_trans_temp = ValueCard(
            "MAX TRANS TEMP",
            "--",
            "°C",
        )
        self.min_oil_pressure = ValueCard(
            "MIN OIL PRESSURE",
            "--",
            "psi",
        )

        peak_grid = QGridLayout()
        peak_grid.setSpacing(10)

        peak_grid.addWidget(self.peak_boost, 0, 0)
        peak_grid.addWidget(self.peak_rpm, 0, 1)
        peak_grid.addWidget(self.peak_egt, 0, 2)

        peak_grid.addWidget(self.max_coolant, 1, 0)
        peak_grid.addWidget(self.max_trans_temp, 1, 1)
        peak_grid.addWidget(self.min_oil_pressure, 1, 2)

        selector_layout = QHBoxLayout()
        selector_layout.setContentsMargins(0, 0, 0, 0)
        selector_layout.setSpacing(4)

        for signal_name in self.GRAPH_SIGNALS:
            button = QPushButton(signal_name)
            button.setCheckable(True)
            button.setFixedHeight(30)

            button.clicked.connect(
                lambda checked, name=signal_name:
                self.select_graph_signal(name)
            )

            self.graph_buttons.append(button)
            selector_layout.addWidget(button)

        self.graph_buttons[0].setChecked(True)

        self.set_selector_style()

        self.graph = GraphWidget(
            title="BOOST HISTORY",
            unit="PSI",
            minimum=0,
            maximum=24,
            max_points=150,
        )

        self.reset_button = QPushButton("RESET PEAKS")
        self.reset_button.setFixedHeight(36)
        self.reset_button.clicked.connect(self.reset_peaks)

        self.reset_button.setStyleSheet(f"""
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
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        layout.addLayout(peak_grid)
        layout.addLayout(selector_layout)
        layout.addWidget(self.graph, stretch=1)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)

    def set_selector_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colours.TEXT_SECONDARY};
                border: none;
                border-radius: {sizes.BUTTON_RADIUS}px;
                padding: 4px 8px;
                font-family: Inter;
                font-size: 8px;
                font-weight: 600;
            }}

            QPushButton:checked {{
                color: {colours.TEXT};
                background-color: {colours.PANEL_ACTIVE};
                border: 1px solid {colours.BORDER_ACTIVE};
            }}

            QPushButton:hover {{
                color: {colours.TEXT};
                background-color: {colours.PANEL};
            }}
        """)

    def select_graph_signal(self, signal_name):
        self.selected_signal = signal_name

        for button in self.graph_buttons:
            button.setChecked(
                button.text() == signal_name
            )

        config = self.GRAPH_SIGNALS[signal_name]

        self.graph.configure(
            title=config["title"],
            unit=config["unit"],
            minimum=config["minimum"],
            maximum=config["maximum"],
        )
        
        self.reload_graph()

    def reload_graph(self):
        config = self.GRAPH_SIGNALS[self.selected_signal]

        samples = self.data_logger.get_latest(
            self.graph.max_points
        )

        values = [
            getattr(sample, config["field"])
            for sample in samples
        ]

        self.graph.set_values(values)

    def update_data(self, data):
        self.peaks["boost"] = max(
            self.peaks["boost"],
            data.boost,
        )
        self.peaks["rpm"] = max(
            self.peaks["rpm"],
            data.rpm,
        )
        self.peaks["egt"] = max(
            self.peaks["egt"],
            data.egt,
        )
        self.peaks["coolant"] = max(
            self.peaks["coolant"],
            data.coolant,
        )
        self.peaks["trans_temp"] = max(
            self.peaks["trans_temp"],
            data.trans_temp,
        )
        self.peaks["oil_pressure"] = min(
            self.peaks["oil_pressure"],
            data.oil_pressure,
        )

        graph_config = self.GRAPH_SIGNALS[
            self.selected_signal
        ]

        graph_value = getattr(
            data,
            graph_config["field"],
        )

        self.graph.add_value(graph_value)

        self.update_cards()

    def update_cards(self):
        self.peak_boost.set_value(
            self.peaks["boost"]
        )
        self.peak_rpm.set_value(
            self.peaks["rpm"]
        )
        self.peak_egt.set_value(
            self.peaks["egt"]
        )
        self.max_coolant.set_value(
            self.peaks["coolant"]
        )
        self.max_trans_temp.set_value(
            self.peaks["trans_temp"]
        )
        self.min_oil_pressure.set_value(
            self.peaks["oil_pressure"]
        )

    def reset_peaks(self):
        self.peaks = {
            "boost": 0.0,
            "rpm": 0,
            "egt": 0,
            "coolant": 0,
            "trans_temp": 0,
            "oil_pressure": 999,
        }

        self.graph.clear()
        self.update_cards()