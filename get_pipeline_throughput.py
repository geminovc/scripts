""" get throughput aggregated over windows of the experiment
"""
def get_throughput(filepath, window):
    windowed_throughput = []
    last_window_start = -1
    current_window_len = 0
    total_predicted_frames = 0
    with open(filepath) as fp:
        line = fp.readline()
        while line:
            x = line.strip()
            if "Prediction time for received keypoints" in x:
                total_predicted_frames += 1
                x_split = x.split()
                end_of_prediction_time = float(x_split[10])
                if end_of_prediction_time - last_window_start > window:
                    if current_window_len > 0:
                        windowed_throughput.append(current_window_len)
                    current_window_len = 1
                    last_window_start = end_of_prediction_time
                else:
                    current_window_len += 1

            line = fp.readline()
    if current_window_len > 0:
        windowed_throughput.append(current_window_len)
    print("windowed_throughput", windowed_throughput)
    print("total_predicted_frames", total_predicted_frames)

get_throughput("/video-conf/scratch/pantea/sample_log_files/receiver_output", 3)    
