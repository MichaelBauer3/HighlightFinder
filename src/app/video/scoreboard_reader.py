import logging
import os

import tensorflow as tf
import numpy as np

from config.config import ML_DIR

logger = logging.getLogger(__name__)

class ScoreboardReader:

    def __init__(self):
        model_path = os.path.join(ML_DIR, "digit_model.tflite")
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()


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

    def get_score(self, img):
        """
            :param img: Preprocessed 28x28 normalized image from preprocess_scoreboard_region
            :return: Digit 0-9, or -1 for blank
            """

        img_arr = self._prepare_digit(img)
        self.interpreter.set_tensor(self.input_details[0]["index"], img_arr)
        self.interpreter.invoke()
        predictions = self.interpreter.get_tensor(self.output_details[0]["index"])
        return int(np.argmax(predictions))