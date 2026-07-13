from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QSlider,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.theme import colours
from app.theme import sizes


class SettingRow(QFrame):
    def __init__(
        self,
        title,
        subtitle="",
        control=None,
    ):
        super().__init__()

        self.setStyleSheet(f"""
            SettingRow {{
                background-color: {colours.PANEL};
                border: 1px solid {colours.BORDER};
                border-radius: {sizes.BUTTON_RADIUS}px;
            }}

            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

        self.title_label = QLabel(title)
        self.subtitle_label = QLabel(subtitle)

        self.title_label.setFont(
            QFont(
                "Inter",
                10,
                QFont.Weight.DemiBold,
            )
        )

        self.subtitle_label.setFont(
            QFont("Inter", 8)
        )

        self.title_label.setStyleSheet(
            f"color: {colours.TEXT};"
        )

        self.subtitle_label.setStyleSheet(
            f"color: {colours.TEXT_SECONDARY};"
        )

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.subtitle_label)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 7, 10, 7)
        layout.setSpacing(10)

        layout.addLayout(text_layout)
        layout.addStretch()

        if control is not None:
            layout.addWidget(control)

        self.setLayout(layout)


class SettingsPage(QWidget):
    def __init__(self, settings_service):
        super().__init__()

        self.settings_service = settings_service

        self.section_label_style = f"""
            color: {colours.TEXT_SECONDARY};
            background: transparent;
            border: none;
        """

        self.button_style = f"""
            QPushButton {{
                background-color: {colours.PANEL_ACTIVE};
                color: {colours.TEXT};
                border: 1px solid {colours.BORDER};
                border-radius: {sizes.BUTTON_RADIUS}px;
                padding: 5px 12px;
                font-family: Inter;
                font-size: 9px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                border-color: {colours.BORDER_ACTIVE};
            }}

            QPushButton:pressed {{
                background-color: {colours.BORDER};
            }}

            QPushButton:checked {{
                color: {colours.TEXT};
                border-color: {colours.BORDER_ACTIVE};
            }}
        """

        # -------------------------------------------------
        # Display section
        # -------------------------------------------------

        display_label = self.make_section_label(
            "DISPLAY"
        )

        self.brightness_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.brightness_slider.setRange(10, 100)
        self.brightness_slider.setFixedWidth(170)

        saved_brightness = self.settings_service.get(
            "brightness",
            80,
        )

        self.brightness_slider.setValue(
            int(saved_brightness)
        )

        self.brightness_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 5px;
                background: {colours.BORDER};
                border-radius: 2px;
            }}

            QSlider::sub-page:horizontal {{
                background: {colours.TEXT_SECONDARY};
                border-radius: 2px;
            }}

            QSlider::add-page:horizontal {{
                background: {colours.BORDER};
                border-radius: 2px;
            }}

            QSlider::handle:horizontal {{
                width: 14px;
                margin: -5px 0;
                background: {colours.TEXT};
                border-radius: 7px;
            }}
        """)

        self.brightness_slider.valueChanged.connect(
            self.save_brightness
        )

        brightness_row = SettingRow(
            "Brightness",
            "Dashboard display brightness",
            self.brightness_slider,
        )

        saved_theme = self.settings_service.get(
            "theme",
            "STEALTH",
        )

        self.theme_button = QPushButton(
            saved_theme
        )
        self.theme_button.setStyleSheet(
            self.button_style
        )

        theme_row = SettingRow(
            "Theme",
            "Current colour theme",
            self.theme_button,
        )

        # -------------------------------------------------
        # Vehicle section
        # -------------------------------------------------

        vehicle_label = self.make_section_label(
            "VEHICLE"
        )

        saved_data_source = self.settings_service.get(
            "data_source",
            "SIMULATOR",
        )

        self.data_source_button = QPushButton(
            saved_data_source
        )
        self.data_source_button.setStyleSheet(
            self.button_style
        )

        data_source_row = SettingRow(
            "Data Source",
            "Vehicle connection mode",
            self.data_source_button,
        )

        saved_units = self.settings_service.get(
            "units",
            "PSI_C",
        )

        self.units_button = QPushButton(
            self.get_units_button_text(saved_units)
        )
        self.units_button.setStyleSheet(
            self.button_style
        )

        self.units_button.clicked.connect(
            self.toggle_units
        )

        units_row = SettingRow(
            "Units",
            "Pressure and temperature units",
            self.units_button,
        )

        # -------------------------------------------------
        # About section
        # -------------------------------------------------

        about_label = self.make_section_label(
            "ABOUT"
        )

        version_value = QLabel("v0.3")
        version_value.setFont(
            QFont(
                "Inter",
                9,
                QFont.Weight.DemiBold,
            )
        )
        version_value.setStyleSheet(
            f"""
                color: {colours.TEXT_SECONDARY};
                background: transparent;
                border: none;
            """
        )

        version_row = SettingRow(
            "DOMO",
            "2018 Isuzu D-MAX dashboard",
            version_value,
        )

        # -------------------------------------------------
        # Main layout
        # -------------------------------------------------

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        layout.addWidget(display_label)
        layout.addWidget(brightness_row)
        layout.addWidget(theme_row)

        layout.addSpacing(3)

        layout.addWidget(vehicle_label)
        layout.addWidget(data_source_row)
        layout.addWidget(units_row)

        layout.addSpacing(3)

        layout.addWidget(about_label)
        layout.addWidget(version_row)

        layout.addStretch()

        self.setLayout(layout)

    def make_section_label(self, text):
        label = QLabel(text)

        label.setFont(
            QFont(
                "Inter",
                9,
                QFont.Weight.DemiBold,
            )
        )

        label.setStyleSheet(
            self.section_label_style
        )

        return label

    def save_brightness(self, value):
        self.settings_service.set(
            "brightness",
            int(value),
        )

    def toggle_units(self):
        current_units = self.settings_service.get(
            "units",
            "PSI_C",
        )

        if current_units == "PSI_C":
            new_units = "KPA_C"
        else:
            new_units = "PSI_C"

        self.settings_service.set(
            "units",
            new_units,
        )

        self.units_button.setText(
            self.get_units_button_text(new_units)
        )

    def get_units_button_text(self, units):
        if units == "KPA_C":
            return "kPa / °C"

        return "PSI / °C"