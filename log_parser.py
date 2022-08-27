import datetime as dt
import sys
""" go through log and compute bits_sent

    Arguments: 
        log_filename: name of the log file
        window: aggregation window for bitrate info (ms)

    Returns:
        frame data - dictionary with frame timestamps, size and type
        bits_sent - timeseries of bits sent in sequence of windows separated
                    by type
"""
def gather_trace_statistics(log_path, window):
    measured_value = {'video': 0, 'audio': 0, 'keypoints':0, 'lr_video':0,
                    'estimated_max_bw_video':0, 'estimated_max_bw_lr_video':0}
    bits_sent = {'video': [], 'audio': [], 'keypoints': [], 'lr_video':[],
            'estimated_max_bw_video':[], 'estimated_max_bw_lr_video':[]}
    count = 0
    count_kp = count_video = count_lr_video = 0
    num_bw = {'estimated_max_bw_video':0, 'estimated_max_bw_lr_video':0}
    last_window_start = -1

    with open(f'{log_path}') as log_file:
        for line in log_file:
            parts = line.split(" ")
            date_str = None
            if len(parts) > 3:
                if parts[1] == ">" and parts[3].startswith("RtpPacket") and "retransmission" not in line:
                    packet_type = parts[0].split("(")[1][:-1]
                    packet_value = 8 * int(line.split(", ")[-1].split(" ")[0]) # in bits

                    if packet_type == "video":
                        count_video += 1
                    elif packet_type == "lr_video":
                        count_lr_video += 1
                    elif packet_type == "keypoints":
                        count_kp += 1

                    date_str = line.split(") ")[-1][:-1]

            if "maximum bitrate" in line:
                if 'lr_video' in line:
                    packet_type = "estimated_max_bw_lr_video"
                else:
                    packet_type = "estimated_max_bw_video"

                num_bw[packet_type] += 1
                packet_value = float(parts[6]) # in bits/s
                date_str = line.split("time ")[-1][:-1]

            if date_str is not None:
                date_str = date_str + '.0' if '.' not in date_str else date_str
                time_object = dt.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
                if last_window_start == -1:
                    last_window_start = time_object
                    first_packet_time = time_object

                if ((time_object - last_window_start).total_seconds() > window):
                    for p in bits_sent.keys():
                        if p in num_bw.keys():
                            if num_bw[p] != 0:
                                bits_sent[p].append(measured_value[p]/num_bw[p])
                            else:
                                bits_sent[p].append(0)
                            num_bw[p] = 0
                        else:
                            bits_sent[p].append(measured_value[p])
                        measured_value[p] = 0
                    last_window_start += dt.timedelta(0, window)

                measured_value[packet_type] += packet_value
                count += 1

    for p in bits_sent.keys():
        if p in num_bw.keys():
            if num_bw[p] != 0:
                bits_sent[p].append(measured_value[p]/num_bw[p])
            else:
                bits_sent[p].append(0)
            num_bw[p] = 0
        else:
            bits_sent[p].append(measured_value[p])
        measured_value[p] = 0

    # adjust window if the elapsed time is less than the window length
    elapsed_time =  (time_object - first_packet_time).total_seconds()
    if elapsed_time < window:
        window = elapsed_time

    log_file.close()
    return {'bits_sent': bits_sent, 'window': window, 'elapsed_time': elapsed_time, 'first_packet_time': first_packet_time}


def gather_encoder_statistics(log_filename, window=1):
    compression_values = {'video': [], 'video_time': [], 'lr_video':[], 'lr_video_time':[]}
    first_time = None
    log_file = open(log_filename, 'r')

    while True:
        line = log_file.readline()

        if not line:
            break

        if "is encoded with timestamp" in line:
            parts = line.strip().split(" ")
            compression_size = int(parts[10])
            date_str = parts[13] + " " + parts[14]
            date_str = date_str + '.0' if '.' not in date_str else date_str
            time_object = dt.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
            if first_time is None:
                first_time = time_object
                compression_time = 0
            else:
                compression_time = (time_object - first_time).total_seconds()
            if "lr_video" in line:
                packet_type = 'lr_video'
            else:
                packet_type = 'video'

            compression_values[packet_type].append(compression_size)
            compression_values[f'{packet_type}_time'].append(compression_time)

    log_file.close()
    return compression_values
