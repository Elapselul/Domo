from PyQt6.QtCore import QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QSizePolicy, QWidget


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

        self.warning_value = (
            warning if warning is not None else maximum * 0.75
        )
        self.danger_value = (
            danger if danger is not None else maximum * 0.9
        )

        self.setMinimumSize(190, 190)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # Roughly 60 FPS

    def set_value(self, value):
        self.target_value = max(
            self.minimum,
            min(value, self.maximum),
        )

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

        size = max(1, min(self.width(), self.height()) - 7)
        rect = QRectF(
            (self.width() - size) / 2,
            (self.height() - size) / 2,
            size,
            size,
        )

        scale = size / 325.0
        arc_width = max(3, round(5 * scale))
        glow_width = max(8, round(14 * scale))
        label_font_size = max(8, round(11 * scale))
        value_font_size = max(30, round(54 * scale))
        title_offset = round(90 * scale)
        unit_offset = round(95 * scale)

        start_angle = 225
        total_angle = 270

        bg_pen = QPen(QColor("#343C46"))
        bg_pen.setWidth(arc_width)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(
            rect,
            start_angle * 16,
            -total_angle * 16,
        )

        value_range = self.maximum - self.minimum
        percent = 0 if value_range == 0 else (
            (self.value - self.minimum) / value_range
        )
        value_angle = -int(total_angle * percent * 16)

        glow_pen = QPen(QColor("#AEB8C5"))
        glow_pen.setWidth(glow_width)
        glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setOpacity(0.12)
        painter.setPen(glow_pen)
        painter.drawArc(rect, start_angle * 16, value_angle)
        painter.setOpacity(1.0)

        value_pen = QPen(self.get_colour())
        value_pen.setWidth(arc_width)
        value_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(value_pen)
        painter.drawArc(rect, start_angle * 16, value_angle)

        painter.setPen(QColor("#8A98A8"))
        painter.setFont(
            QFont("Inter", label_font_size, QFont.Weight.Bold)
        )
        painter.drawText(
            rect.adjusted(0, -title_offset, 0, 0),
            Qt.AlignmentFlag.AlignCenter,
            self.title,
        )

        painter.setPen(QColor("#F2F5F7"))
        painter.setFont(
            QFont("Inter", value_font_size, QFont.Weight.Bold)
        )
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignCenter,
            f"{self.value:.1f}",
        )

        painter.setPen(QColor("#8A98A8"))
        painter.setFont(
            QFont("Inter", label_font_size, QFont.Weight.Bold)
        )
        painter.drawText(
            rect.adjusted(0, unit_offset, 0, 0),
            Qt.AlignmentFlag.AlignCenter,
            self.unit,
        )
