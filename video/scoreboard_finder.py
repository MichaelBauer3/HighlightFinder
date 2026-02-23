from pathlib import Path
import cv2
import logging

logger = logging.getLogger(__name__)

class ScoreboardFinder:

    def __init__(self):
        self.template_path = None
        self.template_gray = None
        self.fixed_region = None

    def set_template(self, template_path: Path):
        self.template_path = template_path

        if self.template_path.exists():
            self.template_gray = cv2.cvtColor(cv2.imread(str(template_path)), cv2.COLOR_BGR2GRAY)

    @staticmethod
    def _crop_digit_for_ml(frame, region_config):
        """
        Preprocess the scoreboard digit region

        :param frame: Cropped frame of the scoreboard
        :param region_config: Region of interest
        :return: nd_array
        """

        x, y, w, h = region_config['x'], region_config['y'], region_config['width'], region_config['height']
        region = frame[y:y + h, x:x + w].copy()

        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

        gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

        upscaled = cv2.resize(gray, (0, 0), fx=4, fy=4, interpolation=cv2.INTER_NEAREST)

        _, cleaned = cv2.threshold(upscaled, 120, 255, cv2.THRESH_TOZERO)

        pad = 10
        padded = cv2.copyMakeBorder(cleaned, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0])
        final_28x28 = cv2.resize(padded, (28, 28), interpolation=cv2.INTER_AREA)

        return final_28x28.astype('float32') / 255.0

    def preprocess_scoreboard_region(self, frame, region_config, rotation_angle: int, digit_region):
        """
        Preprocess the entire frame and crop to only scoreboard

        :param frame: Raw frame
        :param region_config: Region of interest
        :param rotation_angle: Angle to rotate the scoreboard for it to be straight
        :param digit_region: Specific region to extract digits
        :return: nd_array
        """

        gray_raw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.fixed_region is None:
            self.fixed_region = self.locate_scoreboard_by_template(
                gray_raw, region_config, self.template_gray
            )

        if not self.fixed_region:
            return None

        # ax, ay is the EXACT pixel of anchor
        ax, ay = self.fixed_region['x'], self.fixed_region['y']

        pad = 100

        y1, y2 = max(0, ay - pad), min(frame.shape[0], ay + pad)
        x1, x2 = max(0, ax - pad), min(frame.shape[1], ax + pad)
        raw_crop = frame[y1:y2, x1:x2].copy()

        anchor_in_crop = (ax - x1, ay - y1)

        (ch, cw) = raw_crop.shape[:2]
        matrix = cv2.getRotationMatrix2D(anchor_in_crop, rotation_angle, 1.0)
        straightened = cv2.warpAffine(raw_crop, matrix, (cw, ch), flags=cv2.INTER_CUBIC)

        loc = region_config['local_offset']

        final_x = anchor_in_crop[0] + loc['dx']
        final_y = anchor_in_crop[1] + loc['dy']

        scoreboard_final = straightened[
            final_y: final_y + loc['h'],
            final_x: final_x + loc['w']
        ]

        return ScoreboardFinder._crop_digit_for_ml(scoreboard_final, digit_region)

    @staticmethod
    def locate_scoreboard_by_template(frame_gray, expected_region, template_gray, search_expansion: int = 100):
        """
        Find scoreboard using template matching on the static border

        :param frame_gray: Rotated gray frame to search
        :param expected_region: Expected full scoreboard region
        :param template_gray: template image
        :param search_expansion: Search area expansion
        :return: Located scoreboard position or None
        """

        x, y, w, h = expected_region['x'], expected_region['y'], expected_region['width'], expected_region['height']

        img_h, img_w = frame_gray.shape[:2]

        search_x1 = max(0, x - search_expansion)
        search_y1 = max(0, y - search_expansion)
        search_x2 = min(img_w, x + w + search_expansion)
        search_y2 = min(img_h, y + h + search_expansion)

        search_region = frame_gray[search_y1:search_y2, search_x1:search_x2]

        blur_k = (3, 3)
        search_blurred = cv2.GaussianBlur(search_region, blur_k, 0)
        template_blurred = cv2.GaussianBlur(template_gray, blur_k, 0)

        result = cv2.matchTemplate(search_blurred, template_blurred, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < 0.5:
            return None

        actual_x = search_x1 + max_loc[0]
        actual_y = search_y1 + max_loc[1]

        return {
            'x': actual_x,
            'y': actual_y,
            'width': w,
            'height': h,
            'confidence': max_val
        }