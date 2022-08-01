import datetime as dt
import sys
""" go through log and compute bits_sent

    Arguments: 
        log_filename: name of the log file
        window: aggregation window for bitrate info (s)

    Returns:
        frame data - dictionary with frame timestamps, size and type
        bits_sent - timeseries of bits sent in sequence of windows separated
                    by type
"""
def gather_trace_statistics(log_filename, window=1):
    bytes_so_far = {'video': 0, 'audio': 0, 'keypoints':0, 'lr_video':0}
    bits_sent = {'video': [], 'audio': [], 'keypoints': [], 'lr_video':[]}
    count = 0
    count_kp = count_video = count_lr_video = 0
    cur_frame_size = 0
    window_num = 0
    last_window_start = -1
    log_file = open(log_filename, 'r')

    while True:
        line = log_file.readline()

        if not line:
            break
        
        parts = line.split(" ")
        if len(parts) > 3:
            if parts[1] == ">" and parts[3].startswith("RtpPacket"):
                packet_type = parts[0].split("(")[1][:-1]
                packet_size = int(line.split(", ")[-1].split(" ")[0])

                if packet_type == "video":
                    count_video += 1
                elif packet_type == "lr_video":
                    count_lr_video += 1
                elif packet_type == "keypoints":
                    count_kp += 1

                # dump last window's bitrate
                date_str = line.split(") ")[-1][:-1]
                if "retransmission" not in date_str:
                    date_str = date_str + '.0' if '.' not in date_str else date_str
                    time_object = dt.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
                    if last_window_start == -1:
                        last_window_start = time_object
                        first_packet_time = time_object

                    if ((time_object - last_window_start).total_seconds() > window):
                        for p in bits_sent.keys():
                            bits_sent[p].append(bytes_so_far[p] * 8)
                            bytes_so_far[p] = 0
                        last_window_start += dt.timedelta(0, window)
                
                bytes_so_far[packet_type] += packet_size
                count += 1

    for p in bits_sent.keys():
        bits_sent[p].append(bytes_so_far[p] * 8)
        bytes_so_far[p] = 0

    # adjust window if the elapsed time is less than the window length
    elapsed_time =  (time_object - first_packet_time).total_seconds()
    if elapsed_time < window:
        window = elapsed_time

    #print(f'Read {count} packets total {count_kp} kp {count_video} video')
    log_file.close()
    #print(bits_sent)
    return {'bitrates': bits_sent, 'window': window}


def gather_encoder_statistics(log_filename, window=1):
    compression_size = []
    compression_time = []
    log_file = open(log_filename, 'r')

    while True:
        line = log_file.readline()

        if not line:
            break

        if "is encoded with timestamp" in line:
            parts = line.strip().split(" ")
            compression_size.append(int(parts[10]))
            date_str = parts[13] + " " + parts[14]
            time_object = dt.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
            if len(compression_time) == 0:
                first_time = time_object
                compression_time.append(0)
            else:
                compression_time.append((time_object - first_time).total_seconds())

    log_file.close()
    return compression_size, compression_time
