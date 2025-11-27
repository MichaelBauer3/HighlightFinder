import logging
import subprocess
from datetime import datetime
from pathlib import Path
from config import RECORDING_FPS, VIDEO_SIZE

logger = logging.getLogger(__name__)

class ScreenRecorder:

    def __init__(self, output_folder="data/recordings"):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.recording_process = None
        self.output_path = None

    def start_recording(self, team_name: str, duration: int = 3600):
        """
        Start screen recording

        Args:
            team_name (str): Team Name
            duration (int): Recording duration in seconds (default 60 min)

        Returns:
            str: Path to output file
        """
        self.output_path = self.output_folder / f"{team_name}_{datetime.now().strftime("%Y%m%d")}.mp4"

        logger.info(f"Starting screen recording to: {self.output_path}")

        self._start_recording(duration)

        logger.info("Recording started")
        return str(self.output_path)

    def stop_recording(self):
        """Stop the recording"""
        if self.recording_process is None:
            logger.warning("No recording in progress")
            return None

        logger.info("Stopping recording...")

        try:
            self.recording_process.terminate()

            try:
                self.recording_process.wait(timeout=10)
                logger.info("Recording stopped")
            except subprocess.TimeoutExpired:
                logger.info("Recording timed out")
                self.recording_process.kill()
                self.recording_process.wait()

        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            try:
                self.recording_process.kill()
                self.recording_process.wait()
            except Exception as e:
                logger.error(f"Error stopping process: {e}")
                pass

        logger.info(f"Recording stopped: {self.output_path}")

        if self.output_path.exists():
            size_mb = self.output_path.stat().st_size / (1024 * 1024)
            logger.info(f"File size: {size_mb:.2f} MB")
        else:
            logger.error("Recording file not found!")
            return None

        return str(self.output_path)

    def _start_recording(self, duration):
        """Start recording on macOS using ffmpeg"""
        try:
            cmd = [
                'ffmpeg',
                '-f', 'avfoundation',
                '-framerate', str(RECORDING_FPS),
                '-video_size', VIDEO_SIZE,  # 720p resolution
                '-i', '1',  # Screen capture device (1 = main display)
                '-t', str(duration),  # Duration
                '-c:v', 'libx264',  # H.264 codec
                '-preset', 'ultrafast',  # Fast encoding
                '-pix_fmt', 'yuv420p',  # Compatibility
                '-y',  # Overwrite output file
                str(self.output_path)
            ]

            logger.info(f"Running: {' '.join(cmd)}")

            self.recording_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

        except FileNotFoundError:
            logger.error("ffmpeg not found")
            raise

    def record_for_duration(self, team_name: str, duration: int):
        """
        Record for a specific duration and stop automatically

        Args:
            team_name (str): Output filename for mp4 file
            duration (int): Recording duration in seconds

        Returns:
            str: Path to recorded file
        """
        logger.info(f"Recording for {duration} seconds ({duration / 60:.1f} minutes)")

        self.start_recording(team_name=team_name, duration=duration)

        self.recording_process.wait()

        return self.stop_recording()