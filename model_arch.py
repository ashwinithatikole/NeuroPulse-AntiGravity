import tensorflow as tf
from tensorflow.keras import layers, models

def create_model(input_shape=(1000, 1)):
    """
    Creates a 1D-CNN architecture optimized for FPGA implementation.
    Uses only Conv1D, Flatten, and Dense layers as requested.
    """
    model = models.Sequential([
        # First Convolutional Layer
        # Filters: 16, Kernel Size: 3, Activation: ReLU
        layers.Conv1D(filters=16, kernel_size=3, activation='relu', input_shape=input_shape),
        
        # Second Convolutional Layer
        # Filters: 32, Kernel Size: 3, Activation: ReLU
        layers.Conv1D(filters=32, kernel_size=3, activation='relu'),
        
        # Flatten the output for the Dense layers
        layers.Flatten(),
        
        # Fully Connected Layer
        # Units: 64, Activation: ReLU
        layers.Dense(64, activation='relu'),
        
        # Output Layer (Seizure vs No Seizure)
        # Units: 1, Activation: Sigmoid for binary classification
        layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    
    return model

def create_micro_model(input_shape=(1024, 1)):
    """
    Highly optimized for Zynq-7000 BRAM (< 500KB).
    Applies 50% filter reduction (16->8, 32->16) and BatchNormalization for fusion.
    """
    model = models.Sequential([
        # First Conv Block: Conv1D -> BatchNorm -> ReLU
        layers.Conv1D(filters=8, kernel_size=3, padding='same', input_shape=input_shape, name='conv1'),
        layers.BatchNormalization(name='bn1'),
        layers.Activation('relu', name='relu1'),
        
        # Second Conv Block: Conv1D -> BatchNorm -> ReLU
        layers.Conv1D(filters=16, kernel_size=3, padding='same', name='conv2'),
        layers.BatchNormalization(name='bn2'),
        layers.Activation('relu', name='relu2'),
        
        layers.Flatten(),
        
        # Pruned Dense layer
        layers.Dense(16, activation='relu', name='dense1'),
        layers.Dense(1, activation='sigmoid', name='output')
    ])
    
    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    
    return model

if __name__ == "__main__":
    # Instantiate both models for comparison if needed
    model = create_model((1024, 1))
    micro_model = create_micro_model((1024, 1))
    
    print("\nOriginal Model Summary:")
    model.summary()
    
    print("\nMicro Model Summary (Pruned):")
    micro_model.summary()
