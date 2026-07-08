from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF


class CircularGauge(QWidget):
    def __init__(self, title="GAUGE", unit="", minimum=0, maximum=100):
        super().__init__()

        self.title = title
        self.unit = unit
        self.minimum = minimum
        self.maximum = maximum
        self.value = minimum

        self.warning_value = maximum * 0.75
        self.danger_value = maximum * 0.9

        self.setMinimumSize(320, 320)

    def set_value(self, value):
        self.value = max(self.minimum, min(value, self.maximum))
        self.update()

    def get_colour(self):
        if self.value >= self.danger_value:
            return QColor("#EB5757")
        if self.value >= self.warning_value:
            return QColor("#F2994A")
        return QColor("#F2F5F7")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = min(self.width(), self.height()) - 40
        rect = QRectF(
            (self.width() - size) / 2,
            (self.height() - size) / 2,
            size,
            size,
        )

        start_angle = 225
        total_angle = 270

        # Background arc
        bg_pen = QPen(QColor("#262C33"))
        bg_pen.setWidth(10)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(rect, start_angle * 16, -total_angle * 16)

        # Value arc
        percent = (self.value - self.minimum) / (self.maximum - self.minimum)
        value_angle = -int(total_angle * percent * 16)

        value_pen = QPen(self.get_colour())
        value_pen.setWidth(10)
        value_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(value_pen)
        painter.drawArc(rect, start_angle * 16, value_angle)

        # Title
        painter.setPen(QColor("#8A98A8"))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(
            rect.adjusted(0, -70, 0, 0),
            Qt.AlignmentFlag.AlignCenter,
            self.title,
        )

        # Value
        painter.setPen(QColor("#F2F5F7"))
        painter.setFont(QFont("Arial", 44, QFont.Weight.Bold))
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter,
            f"{self.value:.1f}",
        )

        # Unit
        painter.setPen(QColor("#8A98A8"))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(
            rect.adjusted(0, 75, 0, 0),
            Qt.AlignmentFlag.AlignCenter,
            self.unit,
        )