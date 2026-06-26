import os
import random
import numpy as np
import tensorflow as tf
from ai_edge_litert.interpreter import Interpreter

from app.config.config import ML_DIR, DIGITS_DIR


def test_random_samples_tflite(interpreter, dataset_root=f"{str(DIGITS_DIR)}/labeled", num_samples=10):
    """
    Test a TFLite model against random samples from the dataset.
    """
    # Get input and output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    class_names = sorted([d for d in os.listdir(dataset_root)
                          if os.path.isdir(os.path.join(dataset_root, d))])

    all_paths = []
    for label_name in class_names:
        digit_dir = os.path.join(dataset_root, label_name)
        for fname in os.listdir(digit_dir):
            if fname.lower().endswith(".png"):
                all_paths.append((os.path.join(digit_dir, fname), label_name))

    samples = random.sample(all_paths, min(num_samples, len(all_paths)))
    correct = 0

    for img_path, true_label in samples:
        img = tf.keras.utils.load_img(img_path, color_mode="grayscale", target_size=(28, 28))
        arr = tf.keras.utils.img_to_array(img)

        arr = arr.astype(np.float32) / 255.0
        arr = np.expand_dims(arr, axis=0)

        interpreter.set_tensor(input_details[0]['index'], arr)
        interpreter.invoke()

        pred_probs = interpreter.get_tensor(output_details[0]['index'])
        pred_idx = np.argmax(pred_probs[0])
        pred_label_name = class_names[pred_idx]

        is_correct = pred_label_name == true_label
        if is_correct:
            correct += 1

        print(
            f"{os.path.basename(img_path)} | True: {true_label} | Pred: {pred_label_name} | {'✓' if is_correct else '✗'}")

    accuracy = correct / len(samples)
    print(f"\nTFLite Random Test Accuracy: {accuracy * 100:.2f}% ({correct}/{len(samples)})")
    return accuracy


def main():
    model_path = os.path.join(ML_DIR, "digit_model.tflite")

    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    test_random_samples_tflite(interpreter, dataset_root=f"{DIGITS_DIR}/labeled", num_samples=2000)


if __name__ == "__main__":
    main()