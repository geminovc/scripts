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
    estimated_rtts = []
    received_time = []
    fraction_lost = []
    lsr_list = []

    with open(f'{save_dir}') as receiver_log:
        for line in receiver_log:
            words = line.strip()
            if "estimated rtt is" in words:
                words_split = words.split()
                estimated_rtts.append(float(words_split[4].split(',')[0]))
                fraction_lost.append(float(words_split[6].split(',')[0]))
                time = float(words_split[11])
                lsr_list.append(int(words_split[8].split(',')[0]))
                if len(received_time) == 0:
                    first_time = time
                    received_time.append(0)
                else:
                    received_time.append(time - first_time)
    count = 0
    if len(lsr_list) > 1:
        while lsr_list[-(count + 2)] == lsr_list[-1]:
            count += 1

        if count > 0:
            estimated_rtts, fraction_lost, received_time = estimated_rtts[:-count], \
                                                           fraction_lost[:-count], \
                                                           received_time[:-count]
        print("Average estimated rtt", np.mean(estimated_rtts))

    return estimated_rtts, fraction_lost, received_time


if __name__ == "__main__":
    try:
        estimated_rtts, fraction_lost, received_time = get_rtt_over_windows(args.log_path)
        if len(estimated_rtts) > 0:
            os.makedirs(args.save_dir, exist_ok=True)

            plt.figure()
            plt.scatter(received_time, estimated_rtts, label='estimated rtt', s=1, color='r')
            plt.plot(received_time, [np.mean(estimated_rtts) for x in estimated_rtts],\
                    label='avergae estimated rtt', color='b')
            plt.xlabel('time(s)')
            plt.ylabel('rtt(s)')
            plt.title(f'RTT {args.output_name}')
            plt.legend()
            plt.savefig(f'{args.save_dir}/rtt_{args.output_name}.png')

            plt.figure()
            plt.scatter(received_time, fraction_lost, label='fraction lost', s=1, color='r')
            plt.xlabel('time(s)')
            plt.ylabel('lost')
            plt.title(f'Fraction lost {args.output_name}')
            plt.legend()
            plt.savefig(f'{args.save_dir}/fraction_lost_{args.output_name}.png')


    except Exception as e:
        print(e)
        pass

