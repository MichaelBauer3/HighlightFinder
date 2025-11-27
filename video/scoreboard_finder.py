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

        region_rgb = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
        pli_img = Image.fromarray(region_rgb)

        scale_factor = 4
        new_size = (w * scale_factor, h * scale_factor)
        pli_img = pli_img.resize(new_size, Image.Resampling.LANCZOS)

        pli_img_array = np.array(pli_img)

        gray = cv2.cvtColor(pli_img_array, cv2.COLOR_RGB2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(denoised)
        kernel_sharpen = np.array([[-1, -1, -1],
                                   [-1, 9, -1],
                                   [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel_sharpen)


        _, binary = cv2.threshold(sharpened, 0, 255,
                                  cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        if np.mean(binary) < 127:
            binary = cv2.bitwise_not(binary)

        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        kernel_close = np.ones((3, 3), np.uint8)
        closed = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_close, iterations=2)

        kernel_dilate = np.ones((2, 2), np.uint8)
        dilated = cv2.dilate(closed, kernel_dilate, iterations=1)

        return dilated