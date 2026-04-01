import json
import os
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    def __init__(self, path="local_settings.json"):
        combined_path = os.path.join(SCRIPT_DIR, path)
        self.config_path = Path(combined_path)
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

SENDER_EMAIL_ADDRESS = config.get_user_settings("SENDER_EMAIL_ADDRESS")
SENDER_EMAIL_PASSWORD = config.get_user_settings("SENDER_EMAIL_PASSWORD")
SEND_TO_EMAIL_ADDRESS = config.get_user_settings("SEND_TO_EMAIL_ADDRESS")

GOOGLE_FOLDER_ID = config.get_user_settings("GOOGLE_FOLDER_ID")
GOOGLE_CREDENTIALS_PATH = config.get_user_settings("GOOGLE_CREDENTIALS_PATH")
GOOGLE_TOKEN_PATH = config.get_user_settings("GOOGLE_TOKEN_PATH")

GITHUB_USERNAME = config.get_user_settings("GITHUB_USERNAME")
GITHUB_REPO = config.get_user_settings("GITHUB_REPO")
GITHUB_BRANCH = config.get_user_settings("GITHUB_BRANCH")

# Teams to track
TEAMS = ["ewoks fc", "ewoks united"]

FIELD_CONFIGS = {
    "West Field": {
        "name": "West Field (Top Left)",
        "scoreboard_region": {
            'x': 1605,
            'y': 322,
            'width': 60,
            'height': 60,

            "local_offset": {
                "dx": 28,
                "dy": 8,
                "w": 49,
                "h": 22
            },
            "home_score_region": {
                "x": -17,
                "y": -4,
                "width": 4,
                "height": 7
            },
            "away_score_region": {
                "x": 18,
                "y": -4,
                "width": 4,
                "height": 7
            },
            "nested_offset" : {
                "dx": 25,
                "dy": -4,
            }
        },
        "rotation_angle": 36,
        "template_path": "templates/west/west_field_template.png",
        "score_anchor_template_path": "templates/west/west_scoreboard.png",
    },
    "East Field": {
        "name": "East Field (Top Right)",
        "scoreboard_region": {
            'x': 273,
            'y': 210,
            'width': 60,
            'height': 60,

            "local_offset": {
                "dx": -52,
                "dy": 24,
                "w": 49,
                "h": 22
            },
            "home_score_region": {
                "x": -18,
                "y": -2,
                "width": 4,
                "height": 7
            },
            "away_score_region": {
                "x": 17,
                "y": -2,
                "width": 4,
                "height": 7
            },
            "nested_offset" : {
                "dx": 25,
                "dy": -6
            }
        },
        "rotation_angle": -30,
        "template_path": "templates/east/east_field_template.png",
        "score_anchor_template_path": "templates/east/east_scoreboard.png",
    }
}

# Recording settings
RECORDING_DURATION = 60
RECORDING_QUALITY = "720p"
RECORDING_FPS = 30
VIDEO_SIZE = '1920x1080'
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Paths
ROOT_DIR = Path(SCRIPT_DIR)
DATA_DIR = ROOT_DIR / "data"
RECORDINGS_DIR = DATA_DIR / "recordings"
CLIPS_DIR = DATA_DIR / "clips"
METADATA_DIR = DATA_DIR / "metadata"
LOGS_DIR = ROOT_DIR / "logs"
ML_DIR = ROOT_DIR / "ml"

for directory in [RECORDINGS_DIR, CLIPS_DIR, METADATA_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
