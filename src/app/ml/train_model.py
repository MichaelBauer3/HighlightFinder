import tensorflow as tf
from keras import layers
from tensorflow import keras

from app.config.config import DIGITS_DIR

DATA_DIR = DIGITS_DIR / "labeled"
MODEL_NAME = "digit_model"

# -----------------------------
# 1. Load Dataset
# -----------------------------
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="training",
    seed=42,
    color_mode='grayscale',
    image_size=(28, 28),
    batch_size=32,
    label_mode='categorical'
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="validation",
    seed=42,
    color_mode='grayscale',
    image_size=(28, 28),
    batch_size=32,
    label_mode='categorical'
)

# -----------------------------
# 2. Augmentation
# Simulates 1px drift in any direction at 28x28 scale
# height_factor/width_factor of 1/28 ≈ 0.036 = exactly 1 pixel
# -----------------------------
augmentation = keras.Sequential([
    layers.RandomTranslation(
        height_factor=(-1/28, 1/28),
        width_factor=(-1/28, 1/28),
        fill_mode='constant',
        fill_value=0.0
    ),
])

def scale_and_augment(image, label):
    image = tf.cast(image, tf.float32) / 255.0
    image = augmentation(image, training=True)
    return image, label

def scale_images(image, label):
    return tf.cast(image, tf.float32) / 255.0, label

train_ds = train_ds.map(scale_and_augment).cache().prefetch(buffer_size=tf.data.AUTOTUNE)
val_ds = val_ds.map(scale_images).cache().prefetch(buffer_size=tf.data.AUTOTUNE)

# -----------------------------
# 3. Load existing model
# -----------------------------
model = keras.models.load_model(f"{MODEL_NAME}.keras")

# -----------------------------
# 4. Train
# -----------------------------
early_stop = keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=100,
    callbacks=[early_stop]
)

model.save(f"{MODEL_NAME}.keras")

# -----------------------------
# 5. Convert to TFLite with optimization
# -----------------------------

# Representative dataset for quantization calibration
def representative_dataset():
    for images, _ in train_ds.unbatch().batch(1).take(200):
        yield [tf.cast(images, tf.float32)]

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.float32
converter.inference_output_type = tf.float32

tflite_model = converter.convert()

with open(f"{MODEL_NAME}.tflite", "wb") as f:
    f.write(tflite_model)

print(f"Saved {MODEL_NAME}.keras and {MODEL_NAME}.tflite")