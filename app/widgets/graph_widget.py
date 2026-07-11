from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QPainterPath,
    QFont,
)
from PyQt6.QtCore import Qt, QRectF, QTimer

from app.theme import colours
from app.theme import sizes


class GraphWidget(QFrame):
    def __init__(
        self,
        title="BOOST HISTORY",
        unit="PSI",
        minimum=0,
        maximum=24,
        max_points=150,
    ):
        super().__init__()

        self.title = title
        self.unit = unit
        self.minimum = minimum
        self.maximum = maximum
        self.max_points = max_points

        # Final data values received from the vehicle.
        self.values = []

        # Starting positions used while animating toward new values.
        self.start_values = []

        self.animation_progress = 1.0
        self.animation_duration = 180
        self.frame_interval = 16

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate)

        self.setMinimumHeight(150)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colours.PANEL};
                border: 1px solid {colours.BORDER};
                border-radius: {sizes.CARD_RADIUS}px;
            }}
        """)

    def set_values(self, values):
        """
        Immediately replaces the graph history.

        This is used when switching between Boost, EGT, RPM,
        Coolant, Transmission Temperature and Oil Pressure.
        """
        self.values = [
            max(
                self.minimum,
                min(float(value), self.maximum),
            )
            for value in values[-self.max_points:]
        ]

        self.start_values = self.values.copy()
        self.animation_progress = 1.0
        self.animation_timer.stop()

        self.update()

    def add_value(self, value):
        """
        Adds a new sample and smoothly animates the graph
        toward its new position.
        """
        value = max(
            self.minimum,
            min(float(value), self.maximum),
        )

        old_display_values = self.get_display_values()

        new_values = self.values.copy()
        new_values.append(value)

        if len(new_values) > self.max_points:
            new_values.pop(0)

        if not old_display_values:
            self.start_values = new_values.copy()

        elif len(old_display_values) < len(new_values):
            # While the graph is filling, the newest point starts
            # at the height of the previous newest point.
            self.start_values = (
                old_display_values
                + [old_display_values[-1]]
            )

        else:
            # Once the graph is full, the oldest value moves off
            # the left side and everything shifts left.
            self.start_values = (
                old_display_values[1:]
                + [old_display_values[-1]]
            )

        self.values = new_values
        self.animation_progress = 0.0

        if not self.animation_timer.isActive():
            self.animation_timer.start(
                self.frame_interval
            )

        self.update()

    def animate(self):
        """
        Advances the graph animation at approximately 60 FPS.
        """
        progress_step = (
            self.frame_interval
            / self.animation_duration
        )

        self.animation_progress = min(
            1.0,
            self.animation_progress + progress_step,
        )

        self.update()

        if self.animation_progress >= 1.0:
            self.animation_timer.stop()
            self.start_values = self.values.copy()

    def get_display_values(self):
        """
        Returns interpolated values used while the graph is moving.
        """
        if not self.values:
            return []

        if (
            self.animation_progress >= 1.0
            or len(self.start_values)
            != len(self.values)
        ):
            return self.values.copy()

        # Cubic ease-out movement.
        progress = 1.0 - (
            1.0 - self.animation_progress
        ) ** 3

        return [
            start + (target - start) * progress
            for start, target in zip(
                self.start_values,
                self.values,
            )
        ]

    def clear(self):
        self.animation_timer.stop()
        self.values.clear()
        self.start_values.clear()
        self.animation_progress = 1.0
        self.update()

    def configure(
        self,
        title,
        unit,
        minimum,
        maximum,
        max_points=None,
    ):
        self.title = title
        self.unit = unit
        self.minimum = minimum
        self.maximum = maximum

        if max_points is not None:
            self.max_points = max_points

        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        title_height = 42
        left_margin = 42
        right_margin = 18
        bottom_margin = 18

        graph_rect = QRectF(
            left_margin,
            title_height,
            self.width()
            - left_margin
            - right_margin,
            self.height()
            - title_height
            - bottom_margin,
        )

        # Header title
        painter.setPen(
            QColor(colours.TEXT_SECONDARY)
        )
        painter.setFont(
            QFont(
                "Inter",
                10,
                QFont.Weight.DemiBold,
            )
        )

        painter.drawText(
            QRectF(
                14,
                12,
                self.width() - 28,
                22,
            ),
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter,
            self.title,
        )

        # Header unit
        painter.setFont(
            QFont("Inter", 9)
        )

        painter.drawText(
            QRectF(
                14,
                12,
                self.width() - 28,
                22,
            ),
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter,
            self.unit,
        )

        # Grid lines and scale labels
        grid_pen = QPen(
            QColor(47, 55, 66, 120)
        )
        grid_pen.setWidth(1)

        painter.setFont(
            QFont("Inter", 8)
        )

        grid_lines = 4

        for index in range(grid_lines + 1):
            ratio = index / grid_lines

            y = (
                graph_rect.bottom()
                - ratio * graph_rect.height()
            )

            painter.setPen(grid_pen)

            painter.drawLine(
                int(graph_rect.left()),
                int(y),
                int(graph_rect.right()),
                int(y),
            )

            label_value = (
                self.minimum
                + ratio
                * (
                    self.maximum
                    - self.minimum
                )
            )

            painter.setPen(
                QColor(
                    colours.TEXT_SECONDARY
                )
            )

            painter.drawText(
                QRectF(
                    4,
                    y - 8,
                    left_margin - 10,
                    16,
                ),
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter,
                f"{label_value:.0f}",
            )

        display_values = (
            self.get_display_values()
        )

        if len(display_values) < 2:
            painter.setPen(
                QColor(
                    colours.TEXT_SECONDARY
                )
            )
            painter.setFont(
                QFont("Inter", 10)
            )

            painter.drawText(
                graph_rect,
                Qt.AlignmentFlag.AlignCenter,
                "Waiting for data...",
            )
            return

        value_range = (
            self.maximum
            - self.minimum
        )

        if value_range <= 0:
            return

        path = QPainterPath()

        first_x = None
        last_x = None
        last_y = None

        missing_points = (
            self.max_points
            - len(display_values)
        )

        slot_width = (
            graph_rect.width()
            / max(
                1,
                self.max_points - 1,
            )
        )

        easing_progress = 1.0 - (
            1.0 - self.animation_progress
        ) ** 3

        scroll_offset = (
            slot_width
            * (
                1.0
                - easing_progress
            )
        )

        painter.save()
        painter.setClipRect(graph_rect)

        for index, value in enumerate(
            display_values
        ):
            display_index = (
                missing_points + index
            )

            x_ratio = (
                display_index
                / max(
                    1,
                    self.max_points - 1,
                )
            )

            y_ratio = (
                value - self.minimum
            ) / value_range

            x = (
                graph_rect.left()
                + x_ratio
                * graph_rect.width()
                + scroll_offset
            )

            y = (
                graph_rect.bottom()
                - y_ratio
                * graph_rect.height()
            )

            if index == 0:
                first_x = x
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)

            last_x = x
            last_y = y

        # Fill beneath the graph line
        fill_path = QPainterPath(path)

        fill_path.lineTo(
            last_x,
            graph_rect.bottom(),
        )

        fill_path.lineTo(
            first_x,
            graph_rect.bottom(),
        )

        fill_path.closeSubpath()

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            QColor(
                255,
                255,
                255,
                18,
            )
        )

        painter.drawPath(fill_path)

        # Soft graph glow
        glow_pen = QPen(
            QColor(
                174,
                184,
                197,
                55,
            )
        )

        glow_pen.setWidth(7)
        glow_pen.setCapStyle(
            Qt.PenCapStyle.RoundCap
        )
        glow_pen.setJoinStyle(
            Qt.PenJoinStyle.RoundJoin
        )

        painter.setPen(glow_pen)
        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )
        painter.drawPath(path)

        # Main graph line
        line_pen = QPen(
            QColor(colours.TEXT)
        )

        line_pen.setWidth(2)
        line_pen.setCapStyle(
            Qt.PenCapStyle.RoundCap
        )
        line_pen.setJoinStyle(
            Qt.PenJoinStyle.RoundJoin
        )

        painter.setPen(line_pen)
        painter.drawPath(path)

        # Current value marker
        marker_x = last_x - 2
        marker_y = last_y

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        # Marker glow
        painter.setBrush(
            QColor(
                255,
                255,
                255,
                60,
            )
        )

        painter.drawEllipse(
            QRectF(
                marker_x - 6,
                marker_y - 6,
                12,
                12,
            )
        )

        # Marker centre
        painter.setBrush(
            QColor(colours.TEXT)
        )

        painter.drawEllipse(
            QRectF(
                marker_x - 3,
                marker_y - 3,
                6,
                6,
            )
        )

        painter.restore()