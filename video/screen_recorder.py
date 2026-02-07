import logging
import os
import signal
import subprocess

logger = logging.getLogger(__name__)

class ScreenRecorder:
    def __init__(self):
        self.proc = None

    def record_for_duration(self, recording_path, duration, fps=60):
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "x11grab",
            "-i", ":0",
            "-r", str(fps),
            "-t", str(duration),

            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",

            str(recording_path)
        ]

        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        try:
            self.proc.wait(timeout=duration + 5)
        except subprocess.TimeoutExpired:
            os.killpg(self.proc.pid, signal.SIGTERM)

        return recording_path.exists()
