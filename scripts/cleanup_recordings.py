import logging
import shutil
import sys
from datetime import datetime, timedelta

from app.clip_exporter.drive_runner import DriveRunner
from app.config.config import RECORDINGS_DIR, CLIPS_DIR


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Only delete recordings older than 7 days
    cutoff_time = datetime.now() - timedelta(days=7)

    cleaned_count = 0

    for file_path in RECORDINGS_DIR.glob("*.mp4"):
        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)

        if file_time < cutoff_time and not ("east" in file_path.name or "west" in file_path.name):
            logging.warning(f"Found stale recording (>7 days old): {file_path.name}")
            file_path.unlink()
            cleaned_count += 1

    if cleaned_count == 0:
        logging.info("No stale recordings found")
    else:
        logging.warning(f"Cleaned up {cleaned_count} stale recordings")

    cleaned_count = 0
    for folder_path in CLIPS_DIR.glob('*/'):
        folder_time = datetime.fromtimestamp(folder_path.stat().st_mtime)

        if folder_time < cutoff_time:
            logging.warning(f"Found folder: {folder_path.name}")
            shutil.rmtree(folder_path)
            cleaned_count += 1

    if cleaned_count == 0:
        logging.info("No folders found")
    else:
        logging.warning(f"Cleaned up {cleaned_count} folders")

    drive_runner = DriveRunner()
    drive_runner.cleanup_old_folders(30)


if __name__ == "__main__":
    main()