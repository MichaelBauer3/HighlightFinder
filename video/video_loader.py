import os
import subprocess
from pathlib import Path

import cv2
import logging
import glob

from config import RECORDINGS_DIR, CLIPS_DIR

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

    def frames_generator(self, file_name, sample_rate: int = 3):
        """
        Yield a frame approximately every `sample_rate` seconds.
        """
        logger.info(f"Processing video with sample rate: {sample_rate} seconds")

        video_path = self._make_path(RECORDINGS_DIR, file_name)

        self._load_video_info(video_path)

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        frame_interval = int(self.fps * sample_rate)
        frame_num = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            timestamp = frame_num / self.fps

            if frame_num % frame_interval == 0:
                yield timestamp, frame

            frame_num += 1

            if frame_num % (frame_interval * 100) == 0:
                progress = (frame_num / self.frame_count) * 100
                logger.info(f"  Progress: {progress:.1f}% ({timestamp / 60:.1f} min)")

        cap.release()
        logger.info(f"Processed {frame_num} frames")

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


    def clip_video(self, file_name: str, clip_file_name: str, start_time: int, duration: int) -> bool:

        file_path = self._make_path(RECORDINGS_DIR, file_name)
        clip_file_path = self._make_path(CLIPS_DIR, clip_file_name)
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start_time),
            "-i", file_path,
            "-t", str(duration),
            "-c", "copy",
            clip_file_path,
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