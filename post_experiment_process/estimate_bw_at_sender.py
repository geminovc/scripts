""" get bandwidth estimation at sender over windows of time 
    using received acks from the receiver
"""
import numpy as np
import datetime as dt
from scipy import stats
import matplotlib.pyplot as plt
import argparse
from process_utils import *
import os


parser = argparse.ArgumentParser(description='Collect logs info.')
parser.add_argument('--save-dir', type=str,
                    help='directory to save logs and files in',
                    default='./bw_results')
parser.add_argument('--output-name', type=str,
                    help='file to save final graph in',
                    default="bw")
parser.add_argument('--log-path', type=str,
                    help='path to the log file', required=True)
parser.add_argument('--trace-path', type=str,
                    help='path to the trace file', required=True)
parser.add_argument('--uplink-bw-list', type=int, nargs='+',
                    help='list of uplink bws to run on (assumes kpbs)',
                    default=[])
args = parser.parse_args()


def get_bw_over_windows(save_dir, window=1):
    sent_rtp_packets = []
    received_rtp_packets = []
    sent_rtcp_packets = []
    received_rtcp_sr_packets = []
    received_rtcp_rr_packets = []
    estimated_max_bws = []
    received_estimated_time = []

    with open(f'{save_dir}') as receiver_log:
        for line in receiver_log:
            words = line.strip()
            words_split = words.split()
            if " > RTP" in words:
                pass
                #sent_rtp_packets.append(get_RtpPacket(words_split))
            #elif " < RTP " in words:
            #    received_rtp_packets.append(words_split[3:])
            #elif " > RTCP" in words:
            #    sent_rtcp_packets.append(words_split[3:])
            #elif " < RTCP " in words:
            #    if "RtcpSrPacket" in words:
            #        received_rtcp_sr_packets.append(get_RtcpSrPacket(words_split))
            #    elif "RtcpRrPacket" in words:
            #        #print(words)
            #       received_rtcp_rr_packets.append(get_RtcpRrPacket(words_split))
            elif "maximum bitrate" in words:
                estimated_max_bws.append(float(words_split[6]) / 1000)
                received_estimated_time.append(dt.datetime.strptime(words_split[10] + \
                        " " + words_split[11], '%Y-%m-%d %H:%M:%S.%f'))

    prev_lsr = 0
    prev_highest_seq = 0
    for packet in received_rtcp_rr_packets:
        print((packet.arrival_time >> 16) & 0xFFFFFFFF - packet.dlsr - packet.lsr)
        #print(((packet.highest_seq - packet.packet_lost) - (prev_highest_seq)) * 1300 * 8 
        #        / ((packet.arrival_time >> 16) & 0xFFFFFFFF - packet.dlsr - packet.lsr))
        prev_lsr = packet.lsr
        prev_highest_seq = packet.highest_seq
    
    prev_octet_count = 0
    prev_arrival_time = 0
    prev_rtp_timestamp = 0
    for packet in received_rtcp_sr_packets:
        #print((packet.octet_count - prev_octet_count) * 8 /(packet.rtp_timestamp - packet.arrival_time), "kbps")
        prev_octet_count = packet.octet_count
        prev_arrival_time = packet.arrival_time
        prev_rtp_timestamp = packet.rtp_timestamp
    
    total_num_bytes = 0
    prev_send_time = 0
    for packet in sent_rtp_packets:
        for x in received_rtcp_sr_packets:
            if x.rtp_timestamp == packet.time_stamp:
                pass
                #print(x.rtp_timestamp, packet.time_stamp)
    print("estimated_max_bws", np.mean(estimated_max_bws))
    times = []
    first_time = received_estimated_time[0]
    for time in received_estimated_time:
        times.append((time - first_time).total_seconds())
    return estimated_max_bws, times


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


def get_trace_samples(kbits_per_ms, received_estimated_time):
    bws = []
    for i in received_estimated_time:
        bws.append(kbits_per_ms[int(1000 * i)])
    return bws


def get_average_bw_over_window(kbits_per_ms, window=1000):
    # window = 1000 ms
    windowed_bw = []
    last_window_start = 0
    current_window = []
    for k, v in kbits_per_ms.items():
        if k <= last_window_start + window:
            current_window.append(v)
        else:
            windowed_bw.append(np.mean(current_window))
            current_window = [v]
            last_window_start = k
    
    if len(current_window) > 0: # last window
        windowed_bw.append(np.mean(current_window)) 
    
    return windowed_bw


if __name__ == "__main__":
    if len(args.uplink_bw_list):
        x = []
        y = []
        yerr = []
        for bw in args.uplink_bw_list:
            try:
                print(os.path.join(args.log_path, f'{args.output_name}_{bw}kbps', 'run0/sender.log'))
                estimated_max_bws, received_estimated_time = get_bw_over_windows(
                        os.path.join(args.log_path, f'{args.output_name}_{bw}kbps', 'run0/sender.log')
                        )
                if len(estimated_max_bws) > 0:
                    x.append(bw)
                    y.append(np.mean(estimated_max_bws))  # compute mean
                    yerr.append([np.mean(estimated_max_bws) - min(estimated_max_bws), \
                            max(estimated_max_bws) - np.mean(estimated_max_bws)])
                    #print(stats.describe(estimated_max_bws))
            except Exception as e:
                print(e)
                pass
        yerr = np.transpose(yerr)
        os.makedirs(args.save_dir, exist_ok=True)
        plt.figure()
        plt.errorbar(x, y, yerr=yerr, fmt='b^', color='b', label= 'sender bw estimations')
        plt.plot(x, x , label = 'original', color='r')
        plt.xlabel("link bandwidth (kbps)")
        plt.ylabel('estimated bw (kbps)')
        plt.title("Max estimated bw by sender")
        plt.legend()
        plt.savefig(f'{args.save_dir}/{args.output_name}_all.png')

    else:
        try:
            estimated_max_bws, received_estimated_time = get_bw_over_windows(args.log_path)
            if len(estimated_max_bws) > 0:
                trace_bws = get_trace_samples(
                        get_full_trace(args.trace_path,
                                        int(1000 * max(received_estimated_time) + 1)),
                                        received_estimated_time)

                plot_graph(received_estimated_time,\
                          [estimated_max_bws, get_emwa(estimated_max_bws), trace_bws],\
                          ['estimated bw', 'emwa estimated bw', 'original'], \
                          ['b', 'g', 'r'], 'time (s)', 'bw estimated (kbps)', 'Estimation of max estimated bitrate',\
                          args.save_dir, args.output_name)
        except Exception as e:
            print(e)
            pass


