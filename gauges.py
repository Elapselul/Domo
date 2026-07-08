from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF


class BoostGauge(QWidget):
    def __init__(self):
        super().__init__()

        self.value = 0
        self.maximum = 24

        self.setMinimumSize(320, 320)

    def setValue(self, value):
        self.value = max(0, min(value, self.maximum))
        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = min(self.width(), self.height()) - 30

        rect = QRectF(
            (self.width() - size) / 2,
            (self.height() - size) / 2,
            size,
            size,
        )

        # Background circle
        pen = QPen(QColor(45, 45, 55))
        pen.setWidth(18)
        painter.setPen(pen)
        painter.drawArc(rect, 225 * 16, -270 * 16)

        # Boost arc
        pen = QPen(QColor(45, 156, 219))
        pen.setWidth(18)
        painter.setPen(pen)

        span = int((-270 * (self.value / self.maximum)) * 16)

        painter.drawArc(rect, 225 * 16, span)

        # Boost number
        painter.setPen(Qt.GlobalColor.white)

        font = QFont("Arial", 36, QFont.Weight.Bold)
        painter.setFont(font)

        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter,
            f"{self.value:.1f}"
        )

        # Label

        font = QFont("Arial", 14)
        painter.setFont(font)

        painter.drawText(
            rect.adjusted(0, 70, 0, 0),
            Qt.AlignmentFlag.AlignCenter,
            "BOOST PSI"
        )