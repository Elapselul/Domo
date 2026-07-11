import sys

from PyQt6.QtWidgets import QApplication

from app.dashboard_window import DashboardWindow


app = QApplication(sys.argv)

window = DashboardWindow()
window.show()

sys.exit(app.exec())