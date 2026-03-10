import numpy as np
import tensorflow as tf

def extract_weights_to_hex(tflite_path, tensor_index, output_hex):
    interpreter = tf.lite.Interpreter(model_path=tflite_path)
    interpreter.allocate_tensors()
    
    # Get weight data
    weights = interpreter.get_tensor(tensor_index)
    weights_flat = weights.flatten()
    
    # Convert to hex strings (8-bit signed)
    with open(output_hex, 'w') as f:
        for w in weights_flat:
            # Handle signed 8-bit hex conversion
            hex_val = format(w & 0xFF, '02x')
            f.write(f"{hex_val}\n")
    
    print(f"Extracted {len(weights_flat)} weights to {output_hex}")

if __name__ == "__main__":
    # Example usage for Layer 1
    # Tensor index for first conv layer weights is 4 according to weights.txt
    extract_weights_to_hex('seizure_detector_micro.tflite', 4, 'weights_layer1.hex')
