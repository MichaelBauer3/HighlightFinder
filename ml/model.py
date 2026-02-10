import matplotlib.pyplot as plt
import tensorflow as tf
from keras import layers
from tensorflow import keras

DATA_DIR = "../dataset_digits"

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

# Improve performance
train_ds = train_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)

# -----------------------------
# 2. Build Model
# -----------------------------

model = keras.Sequential([
    # Input layer (28x28 grayscale)
    layers.Input(shape=(28, 28, 1)),
    layers.Rescaling(1. / 255),

    # First Convolutional block
    layers.Conv2D(32, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),

    # Second Convolutional block
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),

    # Flatten and Classify
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(10, activation='softmax'),
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()


# -----------------------------
# 4. Train
# -----------------------------
# Uncomment this for first time training
"""
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10
)

model.save("digit_model.keras")
"""

# Uncomment this for sequential training
model = keras.models.load_model("digit_model.keras")

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

model.save("digit_model.keras")

model.summary()
