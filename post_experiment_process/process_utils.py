import matplotlib.pyplot as plt
import numpy as np
import os
import datetime as dt

class RtcpSrPacket:
    def __init__(self, rtp_timestamp=0, packet_count=0, octet_count=0, arrival_time=0):
        self.packet_count = packet_count
        self.octet_count = octet_count
        self.arrival_time = arrival_time
        self.rtp_timestamp = rtp_timestamp


class RtcpRrPacket:
    def __init__(self, fraction_lost=0, packet_lost=0, highest_seq=0, lsr=0, dlsr=0, arrival_time=0):
        """
        lsr = last_sr_timestamp
        dlsr = delay_since_last_sr_timestamp
        arrival_time is at the receiver of the packet
        ■ Last sender report (LSR) time stamp—Indicates the middle 32 bits out of the 64-bit ntp_timestamp
        included in the most recent RTCP SR packet received form the source SSRC. 
        This field is set to 0 if no SR has been received.

        ■ Delay since last SR (DLSR)—Indicates the delay, expressed in units of 1/65,536 seconds,
        between receiving the last SR packet from the source SSRC and sending this RR block.
        This field is set to 0 if no SR packet has been received.
        """
        self.fraction_lost = fraction_lost
        self.packet_lost = packet_lost
        self.highest_seq = highest_seq
        self.lsr = lsr
        self.dlsr = dlsr
        self.arrival_time = arrival_time


class RtpPacket:
    def __init__(self, seq=0, time_stamp=0, payload=0, num_bytes=0, send_time=0):
        self.seq = seq
        self.time_stamp = time_stamp
        self.payload = payload
        self.num_bytes = num_bytes
        self.send_time = send_time


def get_RtpPacket(words_split):
    rtp_packet = RtpPacket()
    for word in words_split:
        if "seq" in word:
            rtp_packet.seq = int(word.split('=')[1][:-1])
        elif "ts=" in word:
            rtp_packet.time_stamp = int(word.split('=')[1][:-1])
        elif "payload" in word:
            rtp_packet.payload = int(word.split('=')[1][:-1])
    
    rtp_packet.send_time = dt.datetime.strptime(words_split[-2] + " " + words_split[-1], '%Y-%m-%d %H:%M:%S.%f')
    rtp_packet.num_bytes = int(words_split[7])
    return rtp_packet


def get_RtcpSrPacket(words_split):
    """
    ■ NTP Time Stamp field is a 64-bit value that indicates the time of the RTP time stamp
    that is included in the report. The format of the NTP packet is a 64-bit number: the top
    32 bits indicate the value in seconds, and the bottom 32 bits indicate the fraction of a second

    ■ RTP time stamp—The RTP time stamp in the header corresponds to the same instance of time as the
    NTP time stamp above it, but the RTP time stamp is represented in the same units of the sample clock
    of the RTP stream. This RTP-to-NTP correspondence allows for audio and video lip sync.

    ■ Sender packet count—The sender packet count indicates the total number of RTP packets sent since the
    stream started transmission, until the time this RTCP SR packet is generated.

    ■ Sender octet count—The sender octet count indicates the number of RTP payload octets sent since the stream
    started transmission, until the time this SR packet is generated. The sender resets the counter if the SSRC
    changes. This value can be used to estimate the average payload rate. The sender octet count does not include
    the length of the header or padding.
    """
    rtp_timestamp = int(words_split[5].split('=')[1][:-1])
    packet_count = int(words_split[6].split('=')[1][:-1])
    octet_count = int(words_split[7].split('=')[1][:-2])
    arrival_time = int(words_split[10].split(':')[1])
    return RtcpSrPacket(rtp_timestamp, packet_count, octet_count, arrival_time)


def get_RtcpRrPacket(words_split):
    rr_packet = RtcpRrPacket()
    for word in words_split:
        if "fraction_lost" in word:
            rr_packet.fraction_lost = int(word.split('=')[1][:-1])
        elif "packet_lost" in word:
            rr_packet.packet_lost = int(word.split('=')[1][:-1])
        elif "highest_seq" in word:
            rr_packet.highest_seq = int(word.split('=')[1][:-1])
        elif "dlsr" in word:
            rr_packet.dlsr = int(word.split('=')[1][:-3])
        elif "lsr" in word and "dlsr" not in word:
            rr_packet.lsr = int(word.split('=')[1][:-1])
        elif "time" in word:
            rr_packet.arrival_time = int(word.split(':')[1])
    return rr_packet


def get_emwa(array, alpha = 0.9):
    ewma = [array[0]]
    for i in range(1, len(array)):
        ewma.append(alpha * array[i] + (1 - alpha) * ewma[i-1])
    return ewma


def plot_graph(x, y_list, label_list, color_list, x_label, y_label, title, save_dir, output_name,
                is_scatter=False):
    os.makedirs(save_dir, exist_ok=True)
    plt.figure()
    for i in range(0, len(y_list)):
        if is_scatter:
            plt.scatter(x, y_list[i] , label=label_list[i], color=color_list[i], s=2)
        else:
            plt.plot(x, y_list[i] , label=label_list[i], color=color_list[i])
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend()
    plt.savefig(f'{save_dir}/{output_name}.png')


def get_full_trace(trace_path, length):
    # length is in ms
    file1 = open(trace_path, 'r')
    kbits_per_ms = {}
    prev_key = 0
    count = 1
    for line in file1.readlines():
      key = int(line.strip())
      if key == prev_key:
        count += 1
      else:
        for i in range(prev_key, key + 1):
          kbits_per_ms[i] = count * 12000 / (key - prev_key)
        count = 1
        prev_key = key

    original_length = len(kbits_per_ms)
    if original_length <= length:
        for t in range(1, length + 1):
            kbits_per_ms[t] = kbits_per_ms[t % original_length]
    else:
        for t in range(length, original_length):
            kbits_per_ms.pop(t)

    return kbits_per_ms


def get_kbits_per_ms(estimated_max_bws, received_estimated_time, is_ms=False, is_kbits=True):
    kbits_per_ms = {}
    for i in range(len(received_estimated_time)):
        t = received_estimated_time[i]
        kbits_per_ms[(((1- int(is_ms)) * 900 + 1) * t)] =  ((1-int(is_kbits)) * 900 + 1) * estimated_max_bws[i]
    return kbits_per_ms


def get_trace_samples(kbits_per_ms, received_estimated_time):
    bws = []
    for i in received_estimated_time:
        bws.append(kbits_per_ms[int(1000 * i)])
    return bws


def get_average_bw_over_window(kbits_per_ms, window=1000):
    # window = 1000 ms
    windowed_bw = []
    current_window = []
    num_windows = int(max(kbits_per_ms.keys())/window) + 1
    for i in range(num_windows):
        current_window = []
        for k, v in kbits_per_ms.items():
            if k > (i+1) * window:
                break
            elif k > i* window and k <= (i+1) * window:
                current_window.append(v)

        if len(current_window) > 0:
            windowed_bw.append(np.mean(current_window))
        else:
            windowed_bw.append(0)
    return windowed_bw

#TODO: complete this function. use fixed windows in time, no elapse
def get_log_statistics(log_path, window):
    measured_value = {'video': 0, 'audio': 0, 'keypoints':0, 'lr_video':0,
                      'estimated_max_bw_video':0, 'estimated_max_bw_lr_video':0,
                      'recv_video': 0}
    bits_sent = {'video': [], 'audio': [], 'keypoints': [], 'lr_video':[],
                 'estimated_max_bw_video':[], 'estimated_max_bw_lr_video':[],
                 'recv_video': []}
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

                if parts[1] == "<" and parts[3].startswith("RtpPacket") and "retransmission" not in line:
                    packet_type = 'recv_video'
                    packet_value = 8 * int(line.split(", ")[-1].split(" ")[0]) # in bits

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
                try:
                    time_object = dt.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
                except:
                    print(line)
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
    return {'bitrates': bits_sent, 'window': window, 'elapsed_time': elapsed_time, 'first_packet_time': first_packet_time}


def get_shell_init_timestamp(mahimahi_log_path):
    log_file = open(mahimahi_log_path, 'r')
    init_timestamp = None
    while True:
        line = log_file.readline()
        if not line:
            break

        if "init timestamp" in line:
            parts = line.strip().split(" ")
            init_timestamp = int(parts[3])
            break

    log_file.close()
    return init_timestamp
