import os
import urllib.request
import mne
import numpy as np

def download_data():
    base_url = "https://physionet.org/files/chbmit/1.0.0/chb01/"
    files = ["chb01_03.edf", "chb01-summary.txt"]
    
    for file in files:
        if not os.path.exists(file):
            print(f"Downloading {file}...")
            urllib.request.urlretrieve(base_url + file, file)
            print(f"Downloaded {file}.")
        else:
            print(f"{file} already exists.")

def parse_summary(summary_file):
    """
    Parses the summary file to get seizure start and end times for chb01_03.edf.
    """
    seizure_times = []
    with open(summary_file, 'r') as f:
        lines = f.readlines()
        
    in_target_file = False
    for i, line in enumerate(lines):
        l = line.strip()
        if "File Name:" in l:
            filename = l.split(":")[1].strip()
            if filename == "chb01_03.edf":
                in_target_file = True
            else:
                in_target_file = False
        
        if in_target_file:
            if "Seizure" in l and "Start Time:" in l:
                # Extract numeric part before "seconds"
                parts = l.split(":")[1].strip().split()
                if parts:
                    start_time = int(parts[0])
                    # Look for end time in subsequent lines
                    for k in range(1, 4):
                        if i + k < len(lines):
                            next_line = lines[i + k].strip()
                            if "Seizure" in next_line and "End Time:" in next_line:
                                end_parts = next_line.split(":")[1].strip().split()
                                if end_parts:
                                    end_time = int(end_parts[0])
                                    seizure_times.append((start_time, end_time))
                                    break
    return seizure_times

def process_data(edf_file, seizure_times):
    # Load EDF file
    raw = mne.io.read_raw_edf(edf_file, preload=True, verbose=False)
    
    # Extract 'FP1-F7' channel
    # Note: CHB-MIT channels are typically named like 'FP1-F7' or 'EEG FP1-F7'
    # We'll search for the exact match or similar
    target_channel = 'FP1-F7'
    if target_channel not in raw.ch_names:
        # Try to find it if there's a prefix
        possible_channels = [ch for ch in raw.ch_names if target_channel in ch]
        if possible_channels:
            target_channel = possible_channels[0]
        else:
            raise ValueError(f"Channel {target_channel} not found in {raw.ch_names}")
    
    raw.pick_channels([target_channel])
    
    # Get data and sampling rate
    data, times = raw.get_data(return_times=True)
    sfreq = raw.info['sfreq'] # Should be 256Hz
    
    # Slicing parameters
    window_duration = 4 # seconds
    window_size = int(window_duration * sfreq) # 1024 samples
    
    X = []
    y = []
    
    num_windows = data.shape[1] // window_size
    
    for i in range(num_windows):
        start_idx = i * window_size
        end_idx = start_idx + window_size
        
        window_data = data[0, start_idx:end_idx]
        
        # Check if this window overlaps with any seizure
        # A window is 'Seizure' if any part of it is within a seizure period
        window_start_time = times[start_idx]
        window_end_time = times[end_idx - 1]
        
        is_seizure = 0
        for s_start, s_end in seizure_times:
            if not (window_end_time < s_start or window_start_time > s_end):
                is_seizure = 1
                break
        
        X.append(window_data)
        y.append(is_seizure)
    
    return np.array(X), np.array(y)

if __name__ == "__main__":
    # 1. Download files
    download_data()
    
    # 2. Parse seizure times
    seizure_times = parse_summary("chb01-summary.txt")
    print(f"Seizure times for chb01_03.edf: {seizure_times}")
    
    # 3. Process EDF data
    X, y = process_data("chb01_03.edf", seizure_times)
    
    # 4. Reshape X to (samples, features, 1) or similar if needed for CNN
    # For Conv1D, (samples, 1024, 1) or (samples, 1, 1024)
    # The user's previous model arch used Conv1D(filters=16, kernel_size=3, input_shape=(1024, 1))
    X = X.reshape(-1, 1024, 1)
    
    # 5. Save arrays
    np.save("X_train.npy", X)
    np.save("y_train.npy", y)
    
    print(f"Processed {len(X)} windows.")
    print(f"X_train shape: {X.shape}")
    print(f"y_train shape: {y.shape}")
    print(f"Seizure windows: {np.sum(y)}")
    print("Optimization: Saved X_train.npy and y_train.npy.")
