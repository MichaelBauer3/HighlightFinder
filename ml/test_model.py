import os
import random

import numpy as np
import tensorflow as tf


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
    class_names = sorted([d for d in os.listdir(dataset_root)
                          if os.path.isdir(os.path.join(dataset_root, d))])

    all_paths = []

    # collect image paths + labels
    for label_name in class_names:
        digit_dir = os.path.join(dataset_root, label_name)
        for fname in os.listdir(digit_dir):
            if fname.lower().endswith(".png"):
                all_paths.append((os.path.join(digit_dir, fname), label_name))

    # sample
    samples = random.sample(all_paths, min(num_samples, len(all_paths)))

    correct = 0
    wrong = []

    for img_path, true_label in samples:
        # Load and preprocess
        img = tf.keras.utils.load_img(img_path, color_mode="grayscale", target_size=(28, 28))
        arr = tf.keras.utils.img_to_array(img)
        arr = np.expand_dims(arr, axis=0)

        # Get prediction
        pred_probs = model.predict(arr, verbose=0)
        pred_idx = np.argmax(pred_probs[0])
        pred_label_name = class_names[pred_idx]

        if pred_label_name == true_label:
            correct += 1
        else:
            wrong.append((true_label, pred_label_name, img_path))

        print(
            f"{os.path.basename(img_path)} | True: {true_label} | Pred: {pred_label_name} | {'✓' if pred_label_name == true_label else '✗'}")

        if show_images:
            import matplotlib.pyplot as plt
            plt.imshow(img, cmap='gray')
            plt.title(f"True: {true_label}, Pred: {pred_label_name}")
            plt.axis('off')
            plt.show()

    accuracy = correct / len(samples)
    print(f"\nRandom Test Accuracy: {accuracy * 100:.2f}% ({correct}/{len(samples)})")

    if wrong:
        print("\nMisclassified images:")
        for true_label, pred_label, img_path in wrong:
            print(f"  True: {true_label}, Predicted: {pred_label} - {img_path}")

    return accuracy


def main():
    model = tf.keras.models.load_model("digit_model.keras")
    test_random_samples(model, num_samples=1000, show_images=False)


if __name__ == "__main__":
    main()