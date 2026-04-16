from enum import Enum


class ScoreRegion(str, Enum):
    HOME = "home"
    AWAY = "away"
    BOTH = "both"