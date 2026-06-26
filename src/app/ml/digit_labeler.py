import os
import cv2
import time

from app.video import VideoLoader
from app.video.scoreboard_finder import ScoreboardFinder
from app.config.config import FIELD_CONFIGS, METADATA_DIR, RECORDINGS_DIR, DIGITS_DIR

VIDEO_PATH = RECORDINGS_DIR / "ewoks_fc_vs_monroe_united_20260625.mp4"
FIELD = "West Field"

# Get both regions
HOME_REGION = FIELD_CONFIGS[FIELD]["scoreboard_region"]["home_score_region"]
AWAY_REGION = FIELD_CONFIGS[FIELD]["scoreboard_region"]["away_score_region"]
ROTATION = FIELD_CONFIGS[FIELD]['rotation_angle']

# Output dir
OUTPUT_DIR = DIGITS_DIR / "raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    video = VideoLoader()
    finder = ScoreboardFinder()

    scoreboard_template = METADATA_DIR / FIELD_CONFIGS[FIELD]['template_path']
    finder.set_template(scoreboard_template)

    field_config = FIELD_CONFIGS[FIELD]

    print("\nExtracting digit frames...")
    print(f"Saving to: {OUTPUT_DIR}\n")

    frame_index = 0

    # sample_rate controls how often frames are grabbed
    for timestamp, frame in video.frames_generator(VIDEO_PATH, sample_rate=1):
        frame_index += 1

        scores = finder.get_scores(frame, field_config)
        home_digit = scores["home"]
        away_digit = scores["away"]

        if home_digit is None or home_digit.size == 0:
            print(f"Skipping empty home ROI on frame {frame_index}")
            continue

        if away_digit is None or away_digit.size == 0:
            print(f"Skipping empty away ROI on frame {frame_index}")
            continue

        # Convert from normalized float [0,1] to uint8 [0,255] for saving
        home_digit_img_uint8 = (home_digit * 255).astype('uint8')
        away_digit_img_uint8 = (away_digit * 255).astype('uint8')

        home_filename = f"frame_home_{frame_index}_{int(time.time())}.png"
        away_filename = f"frame_away_{frame_index}_{int(time.time())}.png"

        home_save_path = os.path.join(OUTPUT_DIR, home_filename)
        away_save_path = os.path.join(OUTPUT_DIR, away_filename)

        cv2.imwrite(away_save_path, away_digit_img_uint8)
        cv2.imwrite(home_save_path, home_digit_img_uint8)

    print("\nDone!")


if __name__ == "__main__":
    main()