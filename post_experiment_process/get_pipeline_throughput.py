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
            if "Prediction time for" in x:
                total_predicted_frames += 1
                x_split = x.split()
                try:
                    end_of_prediction_time = float(x_split[10])
                    prediction_times.append(float(x_split[7]))
                except:
                    continue
                if first_prediction_time == 0:
                    first_prediction_time = end_of_prediction_time
                #print("time diff", (end_of_prediction_time - old_end_of_prediction_time) * 1000, "ms")
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
    #print("average windowed_throughput", np.average([i/window for i in windowed_throughput]))
    print("total_predicted_frames", total_predicted_frames)
    print("average prediction time", np.average(prediction_times[100:]))
    print("total_throughput", total_predicted_frames / (last_prediction_time - first_prediction_time))

window = 0.5
get_throughput("/data1/pantea/measure_time_no_av/lrresolution256x256/xiran/5.mp4/lrquantizer-1/quantizer32/lr_target_bitrate75Kb/run0/receiver.log", window)
