import logging
import subprocess
from pathlib import Path

from config import RECORDING_FPS, VIDEO_SIZE

logger = logging.getLogger(__name__)


class ScreenRecorder:

    def __init__(self, output_folder="data/recordings"):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.recording_process = None
        self.output_path = None

    def _build_command(self, duration):
        """Build command for macOS using ffmpeg"""

        cmd = [
            'ffmpeg',
            '-f', 'avfoundation',
            '-framerate', str(RECORDING_FPS),
            '-video_size', VIDEO_SIZE,
            '-t', str(duration),
            '-i', '1',

            # Encoder settings
            '-c:v', 'libx264',
            '-preset', 'veryfast',   # "slow" wastes CPU with no gain for screen content
            '-crf', '18',            # visually lossless
            '-pix_fmt', 'yuv420p',
            '-profile:v', 'high',
            '-level', '4.2',

            # smoother seeking
            '-movflags', '+faststart',

            str(self.output_path)
        ]

        return cmd

    def record_for_duration(self, team_name: str, game_date: str, duration: int) -> bool:
        safe_date = game_date.replace("-", "")
        self.output_path = self.output_folder / f"{team_name}_{safe_date}.mp4"
        cmd = self._build_command(duration)

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=duration + 30  # Safety timeout
            )

            if result.returncode == 0:
                logger.info("Recording completed successfully")
                logger.info(f"File saved to: {self.output_path}")
                return True
            else:
                stderr = result.stderr.decode(errors="ignore")
                logger.error(f"Recording failed with error: {stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Recording timed out")
            return False
        except Exception as e:
            logger.error(f"An error occurred while recording: {e}")
            return False