import logging
from pathlib import Path

import cv2
import keras
import numpy as np

logger = logging.getLogger(__name__)

class ScoreboardReader:

    def __init__(self):
        model_path = Path("ml/digit_model.keras")
        self.model = keras.models.load_model(model_path)

    @staticmethod
    def _prepare_digit(img):
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        resized = cv2.resize(img, (28, 28), interpolation=cv2.INTER_AREA)
        arr = resized.astype("float32") / 255.0
        arr = np.expand_dims(arr, axis=-1)
        arr = np.expand_dims(arr, axis=0)

        return arr

    def get_scores(self, home_img, away_img):
        home_arr, away_arr = self._prepare_digit(home_img), self._prepare_digit(away_img)

        return (np.argmax(self.model.predict(home_arr, verbose=0)),
                np.argmax(self.model.predict(away_arr, verbose=0)))

    def get_score(self, img):
        img_arr = self._prepare_digit(img)
        return np.argmax(self.model.predict(img_arr, verbose=0))