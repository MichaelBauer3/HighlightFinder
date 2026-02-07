import logging
import os
import signal
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class ScreenRecorder:
    def __init__(self, output_dir="data/recordings"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.proc = None

    def record_for_duration(self, name, duration, fps=60):
        output = self.output_dir / f"{name}.mp4"

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

            str(output)
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

        return output.exists()
