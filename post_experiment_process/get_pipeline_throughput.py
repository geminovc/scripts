""" get throughput aggregated over windows of the experiment
"""
import numpy as np
def get_throughput(filepath, window):
    windowed_throughput = []
    last_window_start = -1
    current_window_len = 0
    total_predicted_frames = 0
    old_end_of_prediction_time = 0
    first_prediction_time = 0
    last_prediction_time = 0
    prediction_times = []
    with open(filepath) as fp:
        line = fp.readline()
        while line:
            x = line.strip()
            if "Prediction time for received keypoints" in x:
                total_predicted_frames += 1
                x_split = x.split()
                end_of_prediction_time = float(x_split[10])
                prediction_times.append(float(x_split[7]))
                if first_prediction_time == 0:
                    first_prediction_time = end_of_prediction_time
                print("time diff", (end_of_prediction_time - old_end_of_prediction_time) * 1000)
                old_end_of_prediction_time = end_of_prediction_time
                if end_of_prediction_time - last_window_start > window:
                    if current_window_len > 0:
                        windowed_throughput.append(current_window_len)
                    current_window_len = 1
                    last_window_start = end_of_prediction_time
                else:
                    current_window_len += 1

            line = fp.readline()

    last_prediction_time = end_of_prediction_time
    if current_window_len > 0:
        windowed_throughput.append(current_window_len)
    #print("windowed_throughput", [i/window for i in windowed_throughput])
    print("average windowed_throughput", np.average([i/window for i in windowed_throughput]))
    print("total_predicted_frames", total_predicted_frames)
    print("average prediction time", np.average(prediction_times))
    print("total_throughput", total_predicted_frames / (last_prediction_time - first_prediction_time))

def get_throughput_over_windows(save_dir, window):
    windowed_received = []
    last_window_start = -1
    current_window_len = 0
    total_predicted_frames = 0
    with open(f'{save_dir}/receiver.log') as receiver_log:
        for line in receiver_log:
            words = line.strip()
            if "Prediction time for received keypoints" in words:
                total_predicted_frames += 1
                words_split = words.split()
                end_of_prediction_time = float(words_split[10])
                if end_of_prediction_time - last_window_start > window:
                    if current_window_len > 0:
                        windowed_received.append(current_window_len)
                    current_window_len = 1
                    last_window_start = end_of_prediction_time
                else:
                    current_window_len += 1

    if current_window_len > 0:
        windowed_received.append(current_window_len)
    windowed_throughput = [i/window for i in windowed_received]
    print("windowed_throughput", windowed_throughput)
    return  windowed_throughput

window = 0.5
#get_throughput("/data4/pantea/aiortc/examples/videostream-cli/xiran_1024_with_skip/receiver_output", window)
get_throughput("/data4/pantea/nets_scripts/xiran_1024_resolution1024_without_hr_skip_connections/xiran/0_1.mp4/run0/receiver.log", window)    
