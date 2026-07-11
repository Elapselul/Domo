from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PyQt6.QtCore import QTimer

from app.widgets.header_bar import HeaderBar

from app.pages.home import HomePage
from app.pages.performance import PerformancePage
from app.pages.diagnostics import DiagnosticsPage
from app.pages.settings import SettingsPage
from app.services.vehicle_service import VehicleService
from app.services.data_logger import DataLogger


class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.vehicle_service = VehicleService()
        self.data_logger = DataLogger(max_samples=500)
        self.setWindowTitle("DOMO")
        self.resize(800, 480)

        self.setStyleSheet("""
            QWidget {
                background-color: #05070A;
            }
        """)

        self.header = HeaderBar()
        self.header.page_selected.connect(self.change_page)

        self.pages = QStackedWidget()
        self.home_page = HomePage(self.vehicle_service)
        self.performance_page = PerformancePage(self.vehicle_service)

        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.performance_page)
        self.pages.addWidget(DiagnosticsPage())
        self.pages.addWidget(SettingsPage())
        self.pages.addWidget(DiagnosticsPage())
        self.pages.addWidget(SettingsPage())

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 6, 10, 10)
        layout.setSpacing(6)

        layout.addWidget(self.header)
        layout.addWidget(self.pages, stretch=1)

        self.setLayout(layout)

        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_vehicle_data)
        self.data_timer.start(180)

    def change_page(self, page_index, page_name):
        self.pages.setCurrentIndex(page_index)

    def update_vehicle_data(self):
        data = self.vehicle_service.get_current_data()

        self.home_page.update_data(data)
        self.performance_page.update_data(data)    
    
    def update_vehicle_data(self):
        data = self.vehicle_service.get_current_data()

        self.data_logger.add_sample(data)

        self.home_page.update_data(data)
        self.performance_page.update_data(data)

       