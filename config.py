import json
from pathlib import Path


class Config:
    def __init__(self, path="local_settings.json"):
        self.config_path = Path(path)
        if self.config_path.exists():
            with open(self.config_path) as json_file:
                self._config = json.load(json_file)
        else:
            self._config = {}

    def get_user_settings(self, key, default=None):
        return self._config.get(key, default)


config = Config()

# Credentials
DAY_SMART_EMAIL = config.get_user_settings("DAY_SMART_EMAIL_ADDRESS")
DAY_SMART_PASSWORD = config.get_user_settings("DAY_SMART_PASSWORD")
LIVE_BARN_EMAIL = config.get_user_settings("LIVE_BARN_EMAIL_ADDRESS")
LIVE_BARN_PASSWORD = config.get_user_settings("LIVE_BARN_PASSWORD")
GITHUB_USERNAME = config.get_user_settings("GITHUB_USERNAME")
GITHUB_REPO = config.get_user_settings("GITHUB_REPO")
GITHUB_BRANCH = config.get_user_settings("GITHUB_BRANCH")

# Teams to track
TEAMS = ["ewoks fc", "ewoks united"]

# Field configurations (you'll fill these in after calibration)
FIELD_CONFIGS = {
    "field_1": {
        "name": "Field 1 (Top Right)",
        "scoreboard_region": {
            "x": 0,  # To be calibrated
            "y": 0,
            "width": 400,
            "height": 150
        },
        "zoom_factor": 3.0,
    },
    "field_2": {
        "name": "Field 2 (Top Left)",
        "scoreboard_region": {
            "x": 0,  # To be calibrated
            "y": 0,
            "width": 400,
            "height": 150
        },
        "zoom_factor": 3.0,
    }
}

# Recording settings
RECORDING_DURATION = 60
RECORDING_QUALITY = "720p"
RECORDING_FPS = 15

# Processing settings
FRAME_SAMPLE_RATE = 3  # Check score every N seconds
OCR_ENGINE = "tesseract"  # or "easyocr"
CLIP_BUFFER_BEFORE = 10  # seconds before goal
CLIP_BUFFER_AFTER = 10  # seconds after goal

# Cleanup
DELETE_RECORDING_AFTER_PROCESSING = True

# Paths
DATA_DIR = Path("data")
RECORDINGS_DIR = DATA_DIR / "recordings"
CLIPS_DIR = DATA_DIR / "clips"
METADATA_DIR = DATA_DIR / "metadata"
LOGS_DIR = Path("logs")

for directory in [RECORDINGS_DIR, CLIPS_DIR, METADATA_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)