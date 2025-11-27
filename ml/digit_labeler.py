import os
import cv2
import time

from video import VideoLoader
from video.scoreboard_finder import ScoreboardFinder
from config import FIELD_CONFIGS


VIDEO_PATH = "./data/recordings/SampleScoreChange.mp4"
FIELD = "East Field"

REGION = FIELD_CONFIGS[FIELD]["home_score_region"]
ROTATION = FIELD_CONFIGS[FIELD]['rotation_angle']

# Output dir
OUTPUT_DIR = "./dataset_unsorted"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    video = VideoLoader(VIDEO_PATH)
    finder = ScoreboardFinder()

    print("\nExtracting digit frames...")
    print(f"Saving to: {OUTPUT_DIR}\n")

    frame_index = 0

    # sample_rate controls how often frames are grabbed
    for timestamp, frame in video.frames_generator(sample_rate=1):
        frame_index += 1

        digit_img = finder.preprocess_scoreboard_region(frame, REGION, ROTATION)

        if digit_img is None or digit_img.size == 0:
            print(f"Skipping empty ROI on frame {frame_index}")
            continue

        # filename: frame_12345_1732493029.png
        filename = f"frame_{frame_index}_{int(time.time())}.png"
        save_path = os.path.join(OUTPUT_DIR, filename)

        cv2.imwrite(save_path, digit_img)
        print(f"Saved: {save_path}")

    print("\nDone!")


if __name__ == "__main__":
    main()
