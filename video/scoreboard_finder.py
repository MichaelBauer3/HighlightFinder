import cv2
import numpy as np
import logging

from PIL import Image

logger = logging.getLogger(__name__)

class ScoreboardFinder:

    @staticmethod
    def preprocess_scoreboard_region(frame, region_config, rotation_angle: int):
        """
        Extract and preprocess the scoreboard region

        :param frame: Original Video Frame
        :param region_config: Region of interest
        :param rotation_angle:  Degrees to rotate (neg = clockwise)
        :return: Tuple(binary, rotated)
        """

        frame_img = Image.fromarray(frame)
        frame_rotated = frame_img.rotate(rotation_angle, expand=True,
                                 resample=Image.Resampling.BICUBIC,
                                 fillcolor=(255, 255, 255))
        frame_rotated_array = np.array(frame_rotated)

        x, y, w, h = region_config['x'], region_config['y'], region_config['width'], region_config['height']
        region = frame_rotated_array[y:y+h, x:x+w].copy()

        """region_rgb = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
        pli_img = Image.fromarray(region_rgb)

        scale_factor = 4
        new_size = (w * scale_factor, h * scale_factor)
        pli_img = pli_img.resize(new_size, Image.Resampling.LANCZOS)

        pli_img_array = np.array(pli_img)"""
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

        """        # 2. Invert if the text is darker than the background
        # Scoreboards are often light-on-dark, but your crop looks dark-on-light.
        # We want white numbers on a black background.
        if np.mean(gray) > 127:
            gray = cv2.bitwise_not(gray)"""

        # 3. High-Contrast Stretch
        # This forces the '7' to become bright white
        gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

        # 4. Sharp Scale up
        upscaled = cv2.resize(gray, (0, 0), fx=4, fy=4, interpolation=cv2.INTER_NEAREST)

        # 5. Clean the edges (Crucial for image_97b3e4.png)
        # We'll apply a slight threshold to kill the 'gray' noise in the background
        _, cleaned = cv2.threshold(upscaled, 155, 255, cv2.THRESH_TOZERO)

        # 6. Add Padding & Final Resize
        pad = 10
        padded = cv2.copyMakeBorder(cleaned, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0])
        final_28x28 = cv2.resize(padded, (28, 28), interpolation=cv2.INTER_AREA)

        return final_28x28.astype('float32') / 255.0


