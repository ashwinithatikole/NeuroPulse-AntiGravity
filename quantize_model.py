import tensorflow as tf
import numpy as np
import os

def fuse_layers(model):
    """
    Fuses Conv1D + BatchNorm + ReLU into a single Conv1D layer.
    """
    print("Performing Layer Fusion (Conv1D + BN + ReLU)...")
    fused_model = tf.keras.models.Sequential()
    fused_model.add(tf.keras.layers.InputLayer(input_shape=model.input_shape[1:]))

    i = 0
    while i < len(model.layers):
        layer = model.layers[i]
        
        if isinstance(layer, tf.keras.layers.Conv1D) and i + 1 < len(model.layers) and isinstance(model.layers[i+1], tf.keras.layers.BatchNormalization):
            # Fuse Conv1D and BN
            bn = model.layers[i+1]
            conv_weights = layer.get_weights() # [kernel, bias] if bias exists
            bn_weights = bn.get_weights() # [gamma, beta, mean, variance]
            
            w = conv_weights[0]
            b = conv_weights[1] if len(conv_weights) > 1 else np.zeros(w.shape[-1])
            
            gamma, beta, mean, var = bn_weights
            eps = bn.epsilon
            
            # BN Fusion logic
            scale = gamma / np.sqrt(var + eps)
            w_fused = w * scale
            b_fused = (b - mean) * scale + beta
            
            # Create new fused Conv1D
            new_layer = tf.keras.layers.Conv1D(
                filters=layer.filters,
                kernel_size=layer.kernel_size,
                strides=layer.strides,
                padding=layer.padding,
                activation=model.layers[i+2].activation if i+2 < len(model.layers) and isinstance(model.layers[i+2], tf.keras.layers.Activation) else None,
                name=f"{layer.name}_fused"
            )
            fused_model.add(new_layer)
            # We need to build the model or set weights after adding
            # But it's easier to just set weights after adding to sequential
            fused_model.layers[-1].set_weights([w_fused, b_fused])
            
            i += 3 if i+2 < len(model.layers) and isinstance(model.layers[i+2], tf.keras.layers.Activation) else 2
        else:
            fused_model.add(layer)
            i += 1
            
    return fused_model

def apply_custom_4bit_quantization(model):
    """
    Applies 4-bit symmetric weight quantization with per-layer scaling.
    Target range: [-8, 7]
    """
    print("Applying Aggressive 4-Bit Weight Quantization...")
    scales = {}
    for layer in model.layers:
        if isinstance(layer, (tf.keras.layers.Conv1D, tf.keras.layers.Dense)):
            weights = layer.get_weights()
            if not weights: continue
            
            w = weights[0]
            # Symmetric quantization: find max abs value
            max_val = np.max(np.abs(w))
            if max_val == 0: 
                scale = 1.0
            else:
                scale = 7.0 / max_val  # Map max_val to 7
            
            # Quantize
            w_q = np.round(w * scale)
            w_q = np.clip(w_q, -8, 7)
            
            # Set quantized weights back (de-quantized for inference simulation)
            weights[0] = w_q / scale
            layer.set_weights(weights)
            scales[layer.name] = scale
            
            print(f"  {layer.name}: Scale={scale:.6f}, Bits=4, Range=[{np.min(w_q)}, {np.max(w_q)}]")
            
    return model, scales

def quantize_model_micro(model, x_train_path, tflite_model_path):
    print("Converting to TFLite (Full Integer INT8)...")
    X_train = np.load(x_train_path).astype(np.float32)
    
    def representative_dataset():
        for i in range(100):
            data = np.expand_dims(X_train[i], axis=0)
            yield [data]

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_dataset
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    
    tflite_model = converter.convert()

    with open(tflite_model_path, 'wb') as f:
        f.write(tflite_model)
    
    print(f"Final Micro Model saved to {tflite_model_path}")

def print_report(keras_model_path, tflite_model_path):
    orig_size = os.path.getsize(keras_model_path) / 1024
    new_size = os.path.getsize(tflite_model_path) / 1024
    
    print("\n" + "="*40)
    print("      MICRO MODEL EFFICIENCY REPORT")
    print("="*40)
    print(f"Original Model: {orig_size/1024:.2f} MB")
    print(f"Micro TFLite:   {new_size:.2f} KB")
    print(f"Reduction:      {100*(orig_size-new_size)/orig_size:.2f}%")
    print("-" * 40)
    if new_size < 500:
        print("STATUS: SUCCESS (< 500KB target met)")
    else:
        print("STATUS: WARNING (> 500KB target NOT met)")
    print("="*40 + "\n")

if __name__ == "__main__":
    import model_arch
    
    X_TRAIN = "X_train.npy"
    Y_TRAIN = "y_train.npy"
    TFLITE_NAME = "seizure_detector_micro.tflite"
    
    if not os.path.exists(X_TRAIN):
        print("Error: X_train.npy not found.")
    else:
        # 1. Load data
        X = np.load(X_TRAIN)
        Y = np.load(Y_TRAIN)
        
        # 2. Create and Train Micro Model
        print("Training Pruned Micro Model...")
        model = model_arch.create_micro_model(input_shape=(1024, 1))
        model.fit(X, Y, epochs=5, batch_size=32, validation_split=0.2, verbose=1)
        
        # 3. Fuse Layers
        model_fused = fuse_layers(model)
        
        # 4. Apply 4-Bit Quantization
        model_quant, scales = apply_custom_4bit_quantization(model_fused)
        
        # 5. Convert to TFLite
        quantize_model_micro(model_quant, X_TRAIN, TFLITE_NAME)
        
        # 6. Report
        print_report("seizure_detector_v1.keras", TFLITE_NAME)
