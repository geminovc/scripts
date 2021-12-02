import pandas as pd
import subprocess as sh
import argparse
import os
import packet_parser
import numpy as np
from utils import *


parser = argparse.ArgumentParser(description='Frame Rate Variation.')
parser.add_argument('--fps-list', type=int, nargs='+',
                    help='list of frames per second', 
                    default=[1, 3, 5, 15, 30])
parser.add_argument('--uplink-trace', type=str,
                    help='uplink trace path for mahimahi', 
                    default="traces/12mbps_trace")
parser.add_argument('--downlink-trace', type=str,
                    help='downlink trace path for mahimahi', 
                    default="traces/12mbps_trace")
parser.add_argument('--duration', type=int,
                    help='duration of experiment (in seconds)', 
                    default=310)
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

""" runs video conference at different frame rates
    capturing tcpdumps to measure bitrates from
"""
def run_experiments():
    params = {}
    save_prefix = args.save_prefix
    params['uplink_trace'] = args.uplink_trace
    params['downlink_trace'] = args.downlink_trace
    params['video_file'] = args.video_file
    params['executable_dir'] = args.executable_dir 
    params['duration'] = args.duration
    
    for fps in args.fps_list:
        params['fps'] = fps
        params['save_dir'] = f'{save_prefix}_{fps}fps'

        if not os.path.exists(params['save_dir']):
            os.makedirs(params['save_dir'])

        run_single_experiment(params)


""" gets bitrate info from pcap file 
    and puts it into csv for R
"""
def aggregate_data():
    first = True
    save_prefix = args.save_prefix
    
    for fps in args.fps_list:
        save_dir = f'{save_prefix}_{fps}fps'
        dump_file = f'{save_dir}/tcpdump.pcap'
        saved_video_file = f'{save_dir}/received.mp4'

        stats = packet_parser.gather_trace_statistics(dump_file, args.window)
        num_windows = len(stats['bitrates']['video'])
        streams = list(stats['bitrates'].keys())
        stats['bitrates']['time'] = np.arange(1, num_windows + 1)
        
        df = pd.DataFrame.from_dict(stats['bitrates'])
        for s in streams:
            df[s] = (df[s] / 1000.0 / args.window).round(2)
        df['kbps'] = df.iloc[:, 0:3].sum(axis=1).round(2) 
        df['fps'] = get_fps_from_video(saved_video_file)

        if first:
            df.to_csv(args.csv_name, header=True, index=False, mode="w")
            first = False
        else:
            df.to_csv(args.csv_name, header=False, index=False, mode="a+")

run_experiments()
aggregate_data()
