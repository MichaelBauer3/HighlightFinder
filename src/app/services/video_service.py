import logging
from pathlib import Path

from numpy import ndarray

from src.app.data_model.game_context import GameContext
from src.app.data_model.score_region import ScoreRegion
from src.app.video import ScoreboardFinder, ScoreboardReader, VideoLoader, ScreenRecorder, ScoreValidator

logger = logging.getLogger(__name__)

class VideoService:

    def __init__(self, scoreboard_finder: ScoreboardFinder,
                 scoreboard_reader: ScoreboardReader,
                 screen_recorder: ScreenRecorder,
                 video_loader: VideoLoader,
                 score_validator: ScoreValidator):
        self.scoreboard_finder = scoreboard_finder
        self.scoreboard_reader = scoreboard_reader
        self.screen_recorder = screen_recorder
        self.video_loader = video_loader
        self.score_validator = score_validator

    def screen_record_for_duration(self, recording_path: Path, duration_seconds: int) -> bool:
        return self.screen_recorder.record_for_duration(recording_path, duration_seconds, 30)

    def stream_frames(self, file_name: str, sample_rate: int = 3):
        return self.video_loader.frames_generator(file_name, sample_rate)

    def get_digit_region(self, frame: ndarray, region_config: dict, region: ScoreRegion) -> ndarray:
        return self.scoreboard_finder.get_scores(frame, region_config, region)

    def get_score(self, img: ndarray) -> int:
        return self.scoreboard_reader.get_score(img)

    def validate_score(self, score: int) -> tuple[bool, int]:
        return self.score_validator.validate_score(score)

    def clip_goal(self, game_context: GameContext, real_score: int, start: int, duration: int) -> bool:
        return self.video_loader.clip_video(game_context, real_score, start, duration)

    def delete_video(self, file_name: str) -> bool:
        return self.video_loader.delete_video(file_name)

    def set_template(self, template_path: Path, anchor_template: Path):
        self.scoreboard_finder.set_template(template_path, anchor_template)