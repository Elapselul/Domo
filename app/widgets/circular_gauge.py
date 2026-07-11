from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF, QTimer


class CircularGauge(QWidget):
    def __init__(
        self,
        title="GAUGE",
        unit="",
        minimum=0,
        maximum=100,
        warning=None,
        danger=None,
    ):
        super().__init__()

        self.title = title
        self.unit = unit
        self.minimum = minimum
        self.maximum = maximum

        self.value = minimum
        self.target_value = minimum

        self.warning_value = warning if warning is not None else maximum * 0.75
        self.danger_value = danger if danger is not None else maximum * 0.9

        self.setMinimumSize(325, 325)

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # roughly 60 FPS

    def set_value(self, value):
        self.target_value = max(self.minimum, min(value, self.maximum))

    def animate(self):
        difference = self.target_value - self.value

        if abs(difference) < 0.01:
            self.value = self.target_value
        else:
            self.value += difference * 0.04

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

        size = min(self.width(), self.height()) - 7
        rect = QRectF(
            (self.width() - size) / 2,
            (self.height() - size) / 2,
            size,
            size,
        )

        start_angle = 225   
        total_angle = 270

        bg_pen = QPen(QColor("#343C46"))
        bg_pen.setWidth(5)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(rect, start_angle * 16, -total_angle * 16)


        percent = (self.value - self.minimum) / (self.maximum - self.minimum)
        value_angle = -int(total_angle * percent * 16)
        
        glow_pen = QPen(self.get_colour())
        glow_pen.setWidth(14)
        glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setOpacity(0.18)
        painter.setPen(glow_pen)
        painter.drawArc(rect, start_angle * 16, value_angle)
        painter.setOpacity(1.0)


        value_pen = QPen(self.get_colour())
        value_pen.setWidth(5)
        value_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(value_pen)
        painter.drawArc(rect, start_angle * 16, value_angle)

        painter.setPen(QColor("#8A98A8"))
        painter.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        painter.drawText(
            rect.adjusted(0, -90, 0, 0),
            Qt.AlignmentFlag.AlignCenter,
            self.title,
        )

        painter.setPen(QColor("#F2F5F7"))
        painter.setFont(QFont("Inter", 54, QFont.Weight.Bold))
        
        value_rect = rect.adjusted(0, 0, 0, 0)


        painter.drawText(
            value_rect,
            Qt.AlignmentFlag.AlignCenter,
            f"{self.value:.1f}",
        )

        painter.setPen(QColor("#8A98A8"))
        painter.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        painter.drawText(
            rect.adjusted(0, 95, 0, 0),
            Qt.AlignmentFlag.AlignCenter,
            self.unit,
        )