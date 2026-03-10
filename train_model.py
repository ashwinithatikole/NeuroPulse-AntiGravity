import numpy as np
import matplotlib.pyplot as plt
from model_arch import create_model
import tensorflow as tf

def train_seizure_model():
    # 1. Load data
    print("Loading data...")
    X_train = np.load("X_train.npy")
    y_train = np.load("y_train.npy")
    print(f"Loaded X_train: {X_train.shape}, y_train: {y_train.shape}")

    # 2. Create and compile model
    # input_shape is (1024, 1) based on data_loader.py output
    model = create_model(input_shape=(1024, 1))
    
    # adam, binary_crossentropy, accuracy are already set in model_arch.py, 
    # but we can re-compile to be sure or just use the default.
    # The requirement says "Compile the model (use Adam optimizer, binary crossentropy, and track 'accuracy')"
    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    # 3. Train the model
    print("Starting training...")
    history = model.fit(
        X_train, y_train,
        epochs=20,
        batch_size=32,
        validation_split=0.2,
        verbose=1
    )

    # 4. Save the model
    model.save("seizure_detector_v1.keras")
    print("Model saved as seizure_detector_v1.keras")

    # 5. Plot training results
    print("Generating training plots...")
    plt.figure(figsize=(12, 5))

    # Plot Accuracy
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)

    # Plot Loss
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("Day4_Training_Results.png", dpi=300)
    print("Plot saved as Day4_Training_Results.png")

if __name__ == "__main__":
    train_seizure_model()
