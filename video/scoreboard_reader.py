import logging
from pathlib import Path

import keras
import numpy as np

logger = logging.getLogger(__name__)

class ScoreboardReader:

    def __init__(self):
        model_path = Path("ml/digit_model.keras")
        self.model = keras.models.load_model(model_path)

    @staticmethod
    def _prepare_digit(img):
        """
        Prepare preprocessed digit for model prediction

        :param img: Already preprocessed 28x28 normalized image from preprocess_scoreboard_region
        :return: Batch-ready array with shape (1, 28, 28, 1)
        """
        if len(img.shape) == 2:
            img = np.expand_dims(img, axis=-1)

        img = np.expand_dims(img, axis=0)

        return img

    def get_scores(self, home_img, away_img):
        home_arr, away_arr = self._prepare_digit(home_img), self._prepare_digit(away_img)

        return (np.argmax(self.model.predict(home_arr, verbose=0)),
                np.argmax(self.model.predict(away_arr, verbose=0)))

    def get_score(self, img):
        """
            :param img: Preprocessed 28x28 normalized image from preprocess_scoreboard_region
            :return: Digit 0-9, or -1 for blank
            """

        img_arr = self._prepare_digit(img)
        return np.argmax(self.model.predict(img_arr, verbose=0))