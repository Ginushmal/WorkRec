import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "target_apps": [], # List of paths to executables
    "base_dir": "captures",
    "fps": 2.0,
    "quality": 30,
    "resize_percent": 100
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            # Merge with default to ensure keys exist
            for k, v in DEFAULT_SETTINGS.items():
                if k not in data:
                    data[k] = v
            return data
    except:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)
