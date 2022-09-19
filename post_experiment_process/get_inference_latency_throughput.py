""" get timings over the experiment
"""
import numpy as np
import datetime
import argparse

template_times = {'elapsed_time in decoder-worker': 0,
                  'elapsed_time in prediction-worker': 0,
                  'elapsed_time in display-worker': 0,
                  'elapsed_time in API': 0,
                  'elapsed_time convert_to_tensor in API': 0,
                  'elapsed_time extract_keypoints in API': 0,
                  'elapsed_time generator in API': 0,
                  'elapsed_time converts to VideoFrame in display-worker': 0,
                  'arrival in decoder-worker': 0,
                  'departure from display-worker': 0}


def get_timestamp_and_time(line_split):
    timestamp_index = line_split.index("timestamp") + 1
    logged_time = float(line_split[-1])

    return line_split[timestamp_index], logged_time


def get_timings(save_dir, window=0.5):
    frame_times_dict = {}
    total_displayed_frames = 0
    total_predicted_frames = 0
    first_displayed_time = None
    last_displayed_time = None

    measurements = {'elapsed_time in decoder-worker': [],
                    'elapsed_time in prediction-worker': [],
                    'elapsed_time in display-worker': [],
                    'elapsed_time converts to VideoFrame in display-worker': []}

    with open(f'{save_dir}/receiver.log') as fp:
        line = fp.readline()
        while line:
            line = line.strip()
            if "(latency)" in line:
                line_split = line.split()
                try:
                    timestamp, logged_time = get_timestamp_and_time(line_split)
                except Exception as e:
                    print(e)
                    break

                if timestamp != 'None':
                    for key in list(measurements.keys()) + ['first frame received', 'last frame received']:
                        if key in line:
                            if key == 'elapsed_time in prediction-worker':
                                total_predicted_frames += 1
                                measurements[key].append(logged_time)
                            elif key == 'elapsed_time in display-worker':
                                total_displayed_frames += 1
                                measurements[key].append(logged_time)
                            elif key == 'first frame received':
                                first_displayed_time =  logged_time
                            elif key == 'last frame received':
                                last_displayed_time = logged_time
                            else:
                                measurements[key].append(logged_time)

            line = fp.readline()

    for key in measurements.keys():
        if len(measurements[key]) > 100 :
            print(key, 1000 * np.average(measurements[key][100:]))

    total_frames = total_predicted_frames if total_predicted_frames > 0 else total_displayed_frames
    print("total_frames", total_frames)
    print("throughput", total_frames / (last_displayed_time - first_displayed_time))
    return frame_times_dict


def get_latency(save_dir):
    #latency
    sent_times = {}
    latencies = []
    last_window_start = -1

    # parse send times
    with open(f'{save_dir}/send_times.txt', 'r') as send_times_file:
        for line in send_times_file:
            words = line.split(' ')
            if len(words) > 5:
                continue
            frame_num = int(words[1])
            relevant_time = f'{words[3]} {words[4][:-1]}'
            relevant_time = relevant_time + '.0' if '.' not in relevant_time else relevant_time
            relevant_time = datetime.datetime.strptime(relevant_time, "%Y-%m-%d %H:%M:%S.%f")
            sent_times[frame_num] = relevant_time
    
    # get receive time, latency, metrics
    recv_times_file = open(f'{save_dir}/recv_times.txt', 'r')
    for line in recv_times_file:
        words = line.split(' ')
        frame_num = int(words[1])
        relevant_time = f'{words[3]} {words[4][:-1]}'
        relevant_time = relevant_time + '.0' if '.' not in relevant_time else relevant_time
        relevant_time = datetime.datetime.strptime(relevant_time, "%Y-%m-%d %H:%M:%S.%f")
        if frame_num in sent_times.keys():
            latency = (relevant_time - sent_times[frame_num]).total_seconds() * 1000
            latencies.append(latency)

    print("Average latency", np.average(latencies[100:]), 'ms')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='latency experiments.')
    parser.add_argument('--save-dir', type=str,
                    help='directory to read the log from',
                    required=True)

    args = parser.parse_args()
    save_dir = args.save_dir[:-1] if args.save_dir[-1] == '/' else args.save_dir
    frame_times_dict = get_timings(save_dir)
    get_latency(save_dir)
