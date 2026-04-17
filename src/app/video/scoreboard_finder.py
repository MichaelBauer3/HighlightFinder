from pathlib import Path

import cv2
import logging

import numpy as np

from app.data_model.score_region import ScoreRegion

logger = logging.getLogger(__name__)


class ScoreboardFinder:

    def __init__(self):
        self.scoreboard_template = None
        self.score_anchor_template = None
        self._fixed_region = None

    def set_template(self, template_path: Path):

        if template_path.exists():

            template_img = cv2.imread(str(template_path))

            if template_img is None:
                raise ValueError(f"Failed to load image: {template_path}")

            self.scoreboard_template = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)

    def get_scoreboard(
            self,
            frame: np.ndarray,
            config: dict):
        """
        1st template match (cached) → crop + rotate → slice out 22x49 scoreboard.

        :param frame: Raw 1080x1920 BGR frame
        :param config: Field config dict
        :return: 22x49 BGR scoreboard crop, or None on failure
        """
        region_config = config["scoreboard_region"]
        rotation_angle = config["rotation_angle"]

        gray_raw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self._fixed_region is None:
            self._fixed_region = self.locate_scoreboard_by_template(
                gray_raw, region_config, self.scoreboard_template
            )

        if self._fixed_region is None:
            logger.warning("1st template match failed")
            return None

        ax, ay = self._fixed_region["x"], self._fixed_region["y"]
        pad = 100

        y1, y2 = max(0, ay - pad), min(frame.shape[0], ay + pad)
        x1, x2 = max(0, ax - pad), min(frame.shape[1], ax + pad)

        raw_crop = frame[y1:y2, x1:x2].copy()
        anchor_in_crop = (ax - x1, ay - y1)

        ch, cw = raw_crop.shape[:2]
        matrix = cv2.getRotationMatrix2D(anchor_in_crop, rotation_angle, 1.0)
        rotated = cv2.warpAffine(raw_crop, matrix, (cw, ch), flags=cv2.INTER_CUBIC)

        offset = region_config["local_offset"]
        sx = anchor_in_crop[0] + offset["dx"]
        sy = anchor_in_crop[1] + offset["dy"]

        scoreboard = rotated[sy: sy + offset["h"], sx: sx + offset["w"]]

        if scoreboard.size == 0:
            logger.warning("Scoreboard crop is empty — check local_offset values")
            return None

        return scoreboard

    def get_scores(
            self,
            frame: np.ndarray,
            config: dict,
            target: ScoreRegion = ScoreRegion.BOTH
    ):
        """
        Full pipeline convenience method. Returns preprocessed digit image(s).

        :param frame: Raw BGR frame
        :param config: Field config dict
        :param target: ScoreTarget.HOME, .AWAY, or .BOTH
        :return: Dict with 'home' and/or 'away' as 28x28 float32 arrays, or None on failure
        """
        scoreboard = self.get_scoreboard(frame, config)
        if scoreboard is None or scoreboard.size == 0:
            logger.warning("get_scoreboard returned empty — skipping frame")
            return {k: None for k in ("home", "away")}

        region_config = config["scoreboard_region"]
        result = {}

        if target in (ScoreRegion.HOME, ScoreRegion.BOTH):
            result["home"] = self._crop_digit_for_ml(
                scoreboard, region_config["home_score_region"]
            )

        if target in (ScoreRegion.AWAY, ScoreRegion.BOTH):
            result["away"] = self._crop_digit_for_ml(
                scoreboard, region_config["away_score_region"]
            )

        return result

    @staticmethod
    def _crop_digit_for_ml(scoreboard, region_config) -> np.ndarray | None:
        if scoreboard is None:
            return None

        x = max(0, region_config["x"])
        y = max(0, region_config["y"])
        w = region_config["width"]
        h = region_config["height"]

        x = min(x, scoreboard.shape[1] - 1)
        y = min(y, scoreboard.shape[0] - 1)
        w = min(w, scoreboard.shape[1] - x)
        h = min(h, scoreboard.shape[0] - y)

        region = scoreboard[y: y + h, x: x + w].copy()

        if region.size == 0:
            logger.warning(f"Empty region crop x={x} y={y} w={w} h={h}")
            return None

        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        gray: np.ndarray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

        upscaled = cv2.resize(gray, (0, 0), fx=4, fy=4, interpolation=cv2.INTER_NEAREST)
        _, cleaned = cv2.threshold(upscaled, 150, 255, cv2.THRESH_TOZERO)

        pad = 10
        padded = cv2.copyMakeBorder(
            cleaned, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=[0]
        )
        final_28x28 = cv2.resize(padded, (28, 28), interpolation=cv2.INTER_AREA)

        return final_28x28.astype("float32") / 255.0


    @staticmethod
    def locate_scoreboard_by_template(
            frame_gray: np.ndarray,
            expected_region: dict,
            template_gray: np.ndarray,
            search_expansion: int = 100
    ):
        """
        1st template match — find the scoreboard anchor in the full frame.

        :param frame_gray: Full grayscale frame
        :param expected_region: Expected scoreboard region dict (x, y, width, height)
        :param template_gray: Grayscale template image
        :param search_expansion: Pixels to expand the search area around expected region
        :return: Dict with x, y, width, height, confidence — or None if below threshold
        """
        x, y, w, h = (
            expected_region["x"],
            expected_region["y"],
            expected_region["width"],
            expected_region["height"],
        )

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

        if max_val < 0.7:
            logger.debug(f"1st template match confidence {max_val:.3f} below threshold 0.7")
            return None

        return {
            "x": search_x1 + max_loc[0],
            "y": search_y1 + max_loc[1],
            "width": w,
            "height": h,
            "confidence": max_val,
        }


    @staticmethod
    def _match_local_template(
            search_img: np.ndarray,
            template: np.ndarray,
            threshold: float = 0.6):
        """
        2nd template match — find the stable anchor blob within the 22x49 scoreboard crop.

        :param search_img: Grayscale scoreboard crop
        :param template: Grayscale anchor blob template
        :param threshold: Minimum confidence to accept match
        :return: Dict with x, y, confidence — or None if below threshold
        """
        blur_k = (3, 3)
        search_blur = cv2.GaussianBlur(search_img, blur_k, 0)
        template_blur = cv2.GaussianBlur(template, blur_k, 0)

        result = cv2.matchTemplate(search_blur, template_blur, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val < threshold and max_val != 0: # At 30 minutes, screen goes black while switching VOD
            logger.info(f"2nd template match confidence {max_val:.3f} below threshold {threshold}")

            # Don't make the job fail
            return {
                "x": 0,
                "y": 0,
                "confidence": 0
            }

        return {
            "x": max_loc[0],
            "y": max_loc[1],
            "confidence": max_val,
        }