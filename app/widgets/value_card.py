from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    pyqtProperty,
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
)

from app.theme import animations, colours, effects, sizes


class ValueCard(QFrame):
    def __init__(
        self,
        title,
        value="--",
        unit="",
        decimals=0,
    ):
        super().__init__()

        self.decimals = decimals
        self._display_value = 0.0
        self.unit_text = unit

        self.setMinimumHeight(78)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.title_label = QLabel(title)
        self.value_label = QLabel(str(value))
        self.unit_label = QLabel(unit)

        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label.setFont(
            QFont("Inter", 11, QFont.Weight.Bold)
        )
        self.value_label.setFont(
            QFont("Inter", 32, QFont.Weight.Bold)
        )
        self.unit_label.setFont(QFont("Inter", 11))

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colours.PANEL};
                border: 1px solid {colours.BORDER};
                border-radius: {sizes.CARD_RADIUS}px;
            }}

            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

        self.title_label.setStyleSheet(
            f"color: {colours.TEXT_SECONDARY};"
        )
        self.value_label.setStyleSheet(
            f"color: {colours.TEXT};"
        )
        self.unit_label.setStyleSheet(
            f"color: {colours.TEXT_SECONDARY};"
        )

        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(effects.GLOW_BLUR)
        glow.setOffset(0, 0)
        glow.setColor(QColor(*effects.GLOW_COLOUR))
        self.setGraphicsEffect(glow)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(1)
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.value_label)
        layout.addWidget(self.unit_label)
        layout.addStretch()

        self.setLayout(layout)

        self.animation = QPropertyAnimation(
            self,
            b"display_value",
        )
        self.animation.setDuration(animations.VALUE_DURATION)
        self.animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

    def get_display_value(self):
        return self._display_value

    def set_display_value(self, value):
        self._display_value = value

        if self.decimals == 0:
            displayed_value = str(round(value))
        else:
            displayed_value = f"{value:.{self.decimals}f}"

        self.value_label.setText(displayed_value)

    display_value = pyqtProperty(
        float,
        fget=get_display_value,
        fset=set_display_value,
    )

    def set_value(self, value):
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            self.animation.stop()
            self.value_label.setText(str(value))
            return

        self.animation.stop()
        self.animation.setStartValue(self._display_value)
        self.animation.setEndValue(numeric_value)
        self.animation.start()
