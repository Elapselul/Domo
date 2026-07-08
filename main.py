import sys
from PyQt6.QtWidgets import QApplication
from app.pages.home import HomePage


app = QApplication(sys.argv)

window = HomePage()
window.setWindowTitle("DOMO")
window.resize(900, 500)
window.show()

sys.exit(app.exec())