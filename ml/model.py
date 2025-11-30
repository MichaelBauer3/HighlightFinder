import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras

DATA_DIR = "../dataset_digits"

# -----------------------------
# 1. Load Dataset
# -----------------------------
dataset = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    labels='inferred',
    label_mode='categorical',
    color_mode='grayscale',     # Your frames should be grayscale; change to 'rgb' if needed
    batch_size=32,
    image_size=(28, 28),        # Resize frames consistently
    shuffle=True,
    seed=42
)

# -----------------------------
# 2. Train/Validation Split
# -----------------------------
train_ds = dataset.take(int(len(dataset) * 0.8))
val_ds = dataset.skip(int(len(dataset) * 0.8))

# Improve performance
train_ds = train_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)

# -----------------------------
# 3. Build Model
# -----------------------------
"""
model = keras.Sequential([
    layers.Flatten(input_shape=(28, 28)),
    layers.Dense(128, activation='relu'),
    layers.Dense(128, activation='relu'),
    layers.Dense(10, activation='softmax'),
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()
"""

# -----------------------------
# 4. Train
# -----------------------------
"""history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10
)

model.save("digit_model.keras")
"""

model = keras.models.load_model("digit_model.keras")

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10
)

model.save("digit_model.keras")

# -----------------------------
# 5. Plot Performance
# -----------------------------
plt.plot(history.history['accuracy'], label='accuracy')
plt.plot(history.history['val_accuracy'], label='val_accuracy')
plt.legend()
plt.show()