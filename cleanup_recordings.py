import logging
from pathlib import Path
from datetime import datetime, timedelta

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    recordings_dir = Path("jobs/data/recordings")

    # Only delete recordings older than 7 days
    cutoff_time = datetime.now() - timedelta(days=7)

    cleaned_count = 0

    for file_path in recordings_dir.glob("*.mp4"):
        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)

        if file_time < cutoff_time:
            logging.warning(f"Found stale recording (>7 days old): {file_path.name}")
            file_path.unlink()
            cleaned_count += 1

    if cleaned_count == 0:
        logging.info("No stale recordings found - system is healthy!")
    else:
        logging.warning(f"Cleaned up {cleaned_count} stale recordings - investigate why they weren't processed")


if __name__ == "__main__":
    main()