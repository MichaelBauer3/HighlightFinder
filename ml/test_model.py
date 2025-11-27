import os
import random
import tensorflow as tf
import numpy as np
from PIL import Image


def test_random_samples(model, dataset_root="../dataset_digits", num_samples=10, show_images=False):
    """
    Randomly picks images from dataset_digits/0 ... dataset_digits/9
    and checks if the model predicts them correctly.

    Args:
        model: trained TensorFlow model
        dataset_root: root folder containing digit folders
        num_samples: number of random images to test
        show_images: if True, displays images inline (Jupyter)

    Returns:
        accuracy as float
    """

    all_paths = []

    # collect image paths + labels
    for digit in range(10):
        digit_dir = os.path.join(dataset_root, str(digit))
        for fname in os.listdir(digit_dir):
            if fname.endswith(".png"):
                all_paths.append((os.path.join(digit_dir, fname), digit))

    # sample
    samples = random.sample(all_paths, num_samples)

    correct = 0

    wrong = []
    for img_path, true_label in samples:
        # Load and preprocess
        img = tf.keras.utils.load_img(img_path, color_mode="grayscale", target_size=(28, 28))
        arr = tf.keras.utils.img_to_array(img)
        arr = arr / 255.0
        arr = np.expand_dims(arr, axis=0)

        pred = np.argmax(model.predict(arr, verbose=0))


        if pred == true_label:
            correct += 1
        else:
            wrong.append((true_label, pred, img_path))

        print(
            f"{os.path.basename(img_path)} | True: {true_label} | Pred: {pred} | {'✓' if pred == true_label else '✗'}")

        if show_images:
            import matplotlib.pyplot as plt
            plt.imshow(img, cmap='gray')
            plt.title(f"True: {true_label}, Pred: {pred}")
            plt.axis('off')
            plt.show()

    accuracy = correct / num_samples
    print(f"\nRandom Test Accuracy: {accuracy * 100:.2f}% ({correct}/{num_samples})")

    for wrong_label in wrong:
        print(f"Thought {wrong_label[0]} was a {wrong_label[1]} - PIC PATH={wrong_label[2]}")

    return accuracy


def main():
    model = tf.keras.models.load_model("digit_model.keras")
    test_random_samples(model, num_samples=1000, show_images=False)

if __name__ == "__main__":
    main()

