from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
)
from PyQt6.QtCore import QTimer

from app.widgets.header_bar import HeaderBar

from app.pages.home import HomePage
from app.pages.performance import PerformancePage
from app.pages.diagnostics import DiagnosticsPage
from app.pages.settings import SettingsPage

from app.services.vehicle_service import VehicleService
from app.services.data_logger import DataLogger
from app.services.settings_service import SettingsService


class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DOMO")
        self.resize(800, 480)

        self.setStyleSheet("""
            QWidget {
                background-color: #05070A;
            }
        """)

        # Shared services
        self.vehicle_service = VehicleService()
        self.data_logger = DataLogger(max_samples=500)

        self.settings_service = SettingsService()

        # Header and navigation
        self.header = HeaderBar()
        self.header.page_selected.connect(self.change_page)

        # Pages
        self.home_page = HomePage(
            self.vehicle_service
        )

        self.performance_page = PerformancePage(
            self.vehicle_service,
            self.data_logger,
        )

        self.diagnostics_page = DiagnosticsPage()

        self.settings_page = SettingsPage(
            self.settings_service
        )

        # Page stack
        self.pages = QStackedWidget()
        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.performance_page)
        self.pages.addWidget(self.diagnostics_page)
        self.pages.addWidget(self.settings_page)

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 6, 10, 10)
        layout.setSpacing(6)

        layout.addWidget(self.header)
        layout.addWidget(self.pages, stretch=1)

        self.setLayout(layout)

        # One shared vehicle-data update loop
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(
            self.update_vehicle_data
        )
        self.data_timer.start(180)

    def update_vehicle_data(self):
        data = self.vehicle_service.get_current_data()

        status_text, status_colour = self.vehicle_service.get_status()
        self.header.set_status(status_text, status_colour)

        self.data_logger.add_sample(data)

        self.home_page.update_data(data)
        self.performance_page.update_data(data)
        self.diagnostics_page.update_data(data)

    def change_page(self, page_index, page_name):
        self.pages.setCurrentIndex(page_index)       