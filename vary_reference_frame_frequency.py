import pandas as pd
import subprocess as sh
import argparse
import os
import packet_parser
import numpy as np
from utils import *
import shutil


parser = argparse.ArgumentParser(description='Compression Factor Variation.')
parser.add_argument('--reference-frame-frequency-list', type=int, nargs='+',
                    help='interval between reference frame in frames',
                    default=[10, 20, 30, 50, 100, 200])
parser.add_argument('--uplink-trace', type=str,
                    help='uplink trace path for mahimahi', 
                    default="traces/12mbps_trace")
parser.add_argument('--downlink-trace', type=str,
                    help='downlink trace path for mahimahi', 
                    default="traces/12mbps_trace")
parser.add_argument('--duration', type=int,
                    help='duration of experiment (in seconds)', 
                    default=310)
parser.add_argument('--jacobian-bits', type=int,
                    help='number of bits to assign to jacobian',
                    default=6)
parser.add_argument('--window', type=int,
                    help='duration to aggregate bitrate over (in seconds)', 
                    default=1)
parser.add_argument('--video-file', type=str,
                    help='name of video', 
                    default="sundar_pichai.mp4")
parser.add_argument('--save-prefix', type=str,
                    help='prefix to save logs and files in', 
                    required=True)
parser.add_argument('--executable-dir', type=str,
                    help='folder where the video-stream cli.py executable lies', 
                    required=True)
parser.add_argument('--csv-name', type=str,
                    help='file to save final data in', 
                    default="data/frame_rate_data")

args = parser.parse_args()

""" runs video conference with different bits per jacobian
    capturing tcpdumps to measure bitrates from
    WARNING: overwrites existing data
"""
def run_experiments():
    params = {}
    save_prefix = args.save_prefix
    params['uplink_trace'] = args.uplink_trace
    params['downlink_trace'] = args.downlink_trace
    params['video_file'] = args.video_file
    params['executable_dir'] = args.executable_dir 
    params['duration'] = args.duration
    params['jacobian_bits'] = args.jacobian_bits
    params['enable_prediction'] = False
    
    for freq in args.reference_frame_frequency_list:
        params['save_dir'] = f'{save_prefix}_ref_every_{freq}frames'
        params['reference_update_freq'] = freq

        shutil.rmtree(params['save_dir'], ignore_errors=True)
        os.makedirs(params['save_dir'])

        run_single_experiment(params)


""" gets bitrate info from pcap file 
    and puts it into csv for R
"""
def aggregate_data():
    first = True
    save_prefix = args.save_prefix
    
    for freq in args.reference_frame_frequency_list:
        save_dir = f'{save_prefix}_ref_every_{freq}frames'
        dump_file = f'{save_dir}/tcpdump.pcap'
        saved_video_file = f'{save_dir}/received.mp4'
        print(save_dir)

        stats = packet_parser.gather_trace_statistics(dump_file, args.window)
        num_windows = len(stats['bitrates']['video'])
        streams = list(stats['bitrates'].keys())
        stats['bitrates']['time'] = np.arange(1, num_windows + 1)
        window = stats['window']
        
        df = pd.DataFrame.from_dict(stats['bitrates'])
        for s in streams:
            df[s] = (df[s] / 1000.0 / window).round(2)
        df['kbps'] = df.iloc[:, 0:3].sum(axis=1).round(2) 
        #df['fps'] = get_fps_from_video(saved_video_file)
        df['jbits'] = args.jacobian_bits
        df['reference_freq'] = freq

        metrics = get_video_quality_latency_over_windows(save_dir, args.window)
        for m in metrics.keys():
            while len(metrics[m]) < df.shape[0]:
                metrics[m].append(0)
            df[m] = metrics[m]
        
        if first:
            df.to_csv(args.csv_name, header=True, index=False, mode="w")
            first = False
        else:
            df.to_csv(args.csv_name, header=False, index=False, mode="a+")

run_experiments()
aggregate_data()