import os
import subprocess
import cv2
import logging
import glob
import numpy as np

from pathlib import Path
from app.config.config import RECORDINGS_DIR, CLIPS_DIR
from app.data_model.game_context import GameContext

logger = logging.getLogger(__name__)

class VideoLoader:

    def __init__(self):
        self.video = None
        self.fps = None
        self.frame_count = None
        self.duration = None
        self.width = None
        self.height = None


    def _load_video_info(self, video_path: Path):
        """Load video metadata"""
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.duration = self.frame_count / self.fps if self.fps > 0 else 0

        cap.release()

        logger.info(f"Video loaded: {video_path.name}")
        logger.info(f"\tResolution: {self.width}x{self.height}")
        logger.info(f"\tFPS: {self.fps:.2f}")
        logger.info(f"\tDuration: {self.duration / 60:.1f} minutes ({self.frame_count} frames)")

    def frames_generator(self, file_name, sample_rate: int = 1):

        video_path = self._make_path(RECORDINGS_DIR, file_name)

        self._load_video_info(video_path)

        fps = 1 / sample_rate

        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vf", f"fps={fps}",
            "-f", "image2pipe",
            "-pix_fmt", "bgr24",
            "-vcodec", "rawvideo",
            "-"
        ]

        pipe = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )

        frame_size = self.width * self.height * 3

        frame_index = 0

        stdout = pipe.stdout
        if stdout is None:
            raise RuntimeError("Failed to open ffmpeg pipe")

        while True:
            raw_frame = pipe.stdout.read(frame_size)
            if len(raw_frame) != frame_size:
                break

            frame = np.frombuffer(raw_frame, dtype=np.uint8)
            frame = frame.reshape((self.height, self.width, 3))

            timestamp = frame_index * sample_rate
            yield timestamp, frame

            frame_index += 1

        pipe.stdout.close()
        pipe.wait()

    def delete_video(self, file_name: str, all_files: bool = False):
        """Clean up the recordings folder"""
        video_path = self._make_path(RECORDINGS_DIR, file_name)

        if all_files and video_path.parent.exists():
            files_to_delete = glob.glob(f"{video_path.parent}/*.mp4")
            for file in files_to_delete:
                os.remove(file)

        elif video_path.exists():
            os.remove(video_path)

    @staticmethod
    def _make_path(directory: str, file_name: str) -> Path:
        return Path(directory) / file_name

    def clip_video(self,
                   game_context: GameContext,
                   real_score: int,
                   start_time: int,
                   duration: int,
                   file_override: str = None
    ) -> bool:

        file_path = self._make_path(RECORDINGS_DIR, file_override or game_context.file_name)

        clip_file_path = self._make_path(CLIPS_DIR, game_context.clip_folder_name())

        clip_file_path.mkdir(parents=True, exist_ok=True)
        clip_file_name = game_context.goal_file_name(real_score)
        clip_goal_path = clip_file_path / clip_file_name

        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start_time),
            "-i", str(file_path),
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-b:v", "6M",
            "-maxrate", "8M",
            "-bufsize", "12M",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            str(clip_goal_path),
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            logger.error(f"FFmpeg clip failed:\n{result.stderr.decode()}")
            return False

        logger.info(f"Clip created: {clip_file_name}")
        return True

    @staticmethod
    def count_clips():
        return len([name for name in os.listdir(CLIPS_DIR) if os.path.isfile(os.path.join(CLIPS_DIR, name))])