""" get rtt estimation at sender over windows of time 
    using received acks from the receiver
"""
import numpy as np
import datetime as dt
from scipy import stats
import argparse
from process_utils import get_emwa, plot_graph
from matplotlib import pyplot as plt
import os


parser = argparse.ArgumentParser(description='Collect logs info.')
parser.add_argument('--save-dir', type=str,
                    help='directory to save logs and files in',
                    default='./rtt_results')
parser.add_argument('--output-name', type=str,
                    help='file to save final graph in',
                    default="rtt")
parser.add_argument('--log-path', type=str,
                    help='path to the log file', required=True)

args = parser.parse_args()


def get_rtt_over_windows(save_dir, window=1):
    sent_rtp_packets = []
    received_rtp_packets = []
    sent_rtcp_packets = []
    received_rtcp_sr_packets = []
    received_rtcp_rr_packets = []
    estimated_rtts = []
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
            elif "estimated rtt is" in words:
                estimated_rtts.append(float(words_split[4].split(',')[0]))

    print("Average estimated rtt", np.mean(estimated_rtts))
    return estimated_rtts


if __name__ == "__main__":
    try:
        estimated_rtts = get_rtt_over_windows(args.log_path)
        if len(estimated_rtts) > 0:
            os.makedirs(args.save_dir, exist_ok=True)
            plt.figure()
            plt.scatter(range(1, len(estimated_rtts) + 1), estimated_rtts, label='estimated rtt', s=1, color='b')
            plt.xlabel('#')
            plt.ylabel('rtt(s)')
            plt.title('Estimation of rtt in log')
            plt.legend()
            plt.savefig(f'{args.save_dir}/{args.output_name}.png')
    except Exception as e:
        print(e)
        pass

