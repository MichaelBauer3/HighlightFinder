import logging

from numpy import ndarray

from video import ScoreboardFinder, ScoreboardReader, VideoLoader, ScreenRecorder, ScoreValidator

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

    def screen_record_for_duration(self, duration_seconds: int) -> None:
        self.screen_record_for_duration(duration_seconds)

    def stream_frames(self, file_name: str, sample_rate: int = 3):
        return self.video_loader.frames_generator(file_name, sample_rate)

    def process_to_digit(self, frame: ndarray, region_config: dict, rotation_angle: int) -> ndarray:
        return self.scoreboard_finder.preprocess_scoreboard_region(frame, region_config, rotation_angle)

    def get_score(self, img: ndarray) -> int:
        return self.scoreboard_reader.get_score(img)

    def get_scores(self, home_img: ndarray, away_img: ndarray) -> tuple[int, int]:
        return self.scoreboard_reader.get_scores(home_img, away_img)

    def validate_score(self, score: int) -> bool:
        return self.score_validator.validate_score(score)

    def clip_goal(self, source_video: str, clip_name: str, start: int, duration: int) -> bool:
        return self.video_loader.clip_video(source_video, clip_name, start, duration)