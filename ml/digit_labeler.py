import os
from pathlib import Path

import cv2
import time

from video import VideoLoader
from video.scoreboard_finder import ScoreboardFinder
from config import FIELD_CONFIGS

ROOT_DIR = Path(__file__).parent.parent
VIDEO_PATH = ROOT_DIR / "data/recordings/West_Field_Demo.mp4"
FIELD = "West Field"

# Get both regions
HOME_REGION = FIELD_CONFIGS[FIELD]["home_score_region"]
AWAY_REGION = FIELD_CONFIGS[FIELD]["away_score_region"]
ROTATION = FIELD_CONFIGS[FIELD]['rotation_angle']

# Output dir
OUTPUT_DIR = ROOT_DIR / "dataset_unsorted"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    video = VideoLoader()
    finder = ScoreboardFinder()

    print("\nExtracting digit frames...")
    print(f"Saving to: {OUTPUT_DIR}\n")

    frame_index = 0

    # sample_rate controls how often frames are grabbed
    for timestamp, frame in video.frames_generator(VIDEO_PATH, sample_rate=1):
        frame_index += 1

        regions = {
            'home': HOME_REGION,
            'away': AWAY_REGION
        }

        for team, region in regions.items():
            digit_img = finder.preprocess_scoreboard_region(frame, region, ROTATION)

            if digit_img is None or digit_img.size == 0:
                print(f"Skipping empty {team} ROI on frame {frame_index}")
                continue

            # Convert from normalized float [0,1] to uint8 [0,255] for saving
            digit_img_uint8 = (digit_img * 255).astype('uint8')

            filename = f"frame_{team}_{frame_index}_{int(time.time())}.png"
            save_path = os.path.join(OUTPUT_DIR, filename)

            cv2.imwrite(save_path, digit_img_uint8)
            print(f"Saved: {save_path}")

    print("\nDone!")


if __name__ == "__main__":
    main()