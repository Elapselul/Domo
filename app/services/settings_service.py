import json
from pathlib import Path


class SettingsService:
    DEFAULT_SETTINGS = {
        "brightness": 80,
        "units": "PSI_C",
        "data_source": "SIMULATOR",
        "theme": "STEALTH",
    }

    def __init__(self):
        self.settings_path = (
            Path.home()
            / ".domo"
            / "settings.json"
        )

        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        try:
            if not self.settings_path.exists():
                self.save()
                return

            with self.settings_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                loaded_settings = json.load(file)

            if isinstance(loaded_settings, dict):
                self.settings.update(loaded_settings)

        except (
            OSError,
            json.JSONDecodeError,
        ):
            self.settings = self.DEFAULT_SETTINGS.copy()

    def save(self):
        self.settings_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.settings_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.settings,
                file,
                indent=4,
            )

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()