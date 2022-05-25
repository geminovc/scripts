import sys
sys.path.append('../')
import pandas as pd
import subprocess as sh
import argparse
import os
import log_parser
import numpy as np
from utils import *
import shutil
from time import perf_counter
import math


parser = argparse.ArgumentParser(description='Reference Frame Frequency Variation.')
parser.add_argument('--reference-frame-frequency-list', type=int, nargs='+',
                    help='interval between reference frame in frames',
                    default=[10, 60, 300, 900, 30000])
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
                    default=16)
parser.add_argument('--window', type=int,
                    help='duration to aggregate bitrate over (in seconds)', 
                    default=1)
parser.add_argument('--num-runs', type=int,
                    help='number of runs to average over per experiment',
                    default=1)
parser.add_argument('--people', type=str, nargs='+',
                    help='person who will be resized', default=['xiran'])
parser.add_argument('--root-dir', type=str,
                    help='name of default video directory', 
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
parser.add_argument('--quantizer', type=int,
                    help='quantizer to quantize video stream at',
                    default=32)
parser.add_argument('--resolution', type=str,
                    help='resolution of the image',
                    default='512x512')
parser.add_argument('--video-num-range', type=int, nargs=2,
                    help='video start and end range', default=[0, 4])
parser.add_argument('--setting', type=str,
                    help='personalized vs. generic', 
                    default="personalized")
parser.add_argument('--aggregate', action='store_true',
                    help='only aggregate final stats')
parser.add_argument('--run', action='store_true',
                    help='only run experiments')


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
    params['executable_dir'] = args.executable_dir 
    params['duration'] = args.duration
    params['jacobian_bits'] = args.jacobian_bits
    params['enable_prediction'] = True
    params['runs'] = 1
    setting = args.setting 
    params['quantizer'] = args.quantizer
    params['socket_path'] = f'{setting}.sock'
    vid_start, vid_end = args.video_num_range
    assert(vid_end >= vid_start)
    width, height = args.resolution.split("x")
    
    for person in args.people:
        for freq in args.reference_frame_frequency_list:
            params['reference_update_freq'] = freq
            
            video_dir = os.path.join(args.root_dir, person, "test")
            if setting == 'personalized':
                params['checkpoint'] = checkpoint_dict[width][person]
            else:
                params['checkpoint'] = checkpoint_dict[width]['generic']
            
            for i, video_name in enumerate(os.listdir(video_dir)):
                if i not in range(vid_start, vid_end + 1):
                    continue
                
                video_file = os.path.join(video_dir, video_name)
                params['save_dir'] = f'{save_prefix}_{setting}/resolution{args.resolution}/{person}/reference_freq{freq}/' + \
                        f'{os.path.basename(video_name)}'
                params['video_file'] = f'{params["save_dir"]}/{video_name}'

                start = perf_counter()
                shutil.rmtree(params['save_dir'], ignore_errors=True)
                os.makedirs(params['save_dir'])
                end = perf_counter()
                print("rm command took", end - start)

                start = perf_counter()
                cp_cmd = f'cp {video_file} {params["video_file"]}'
                print(cp_cmd)
                os.system(cp_cmd)
                end = perf_counter()
                print("video copy command took", end - start)

                print(f'Run {video_name} for person {person} reference frame freq {freq} setting {setting}')
                run_single_experiment(params)
                end = perf_counter()
                print("single experiment took", end - start)


""" gets bitrate info from pcap file 
    and puts it into csv for R
"""
def aggregate_data():
    first = True
    save_prefix = args.save_prefix
    setting = args.setting
    vid_start, vid_end = args.video_num_range
    fps = 30
    width, height = args.resolution.split("x")
    frame_size = float(width) * float(height)
    assert(vid_end >= vid_start)
    
    for freq in args.reference_frame_frequency_list:
        combined_df = pd.DataFrame()

        for person in args.people:
            video_dir = os.path.join(args.root_dir, person, "test")

            for i, video_name in enumerate(os.listdir(video_dir)):
                if i not in range(vid_start, vid_end + 1):
                    continue
                
                start = perf_counter()
                print(f'Run {video_name} for person {person} reference frame freq {freq} setting {setting}')
                save_dir = f'{save_prefix}_{setting}/resolution{args.resolution}/{person}/reference_freq{freq}/' + \
                        f'{os.path.basename(video_name)}/run0'
                dump_file = f'{save_dir}/sender.log'
                saved_video_file = f'{save_dir}/received.mp4'
                print(save_dir)

                stats = log_parser.gather_trace_statistics(dump_file, args.window)
                num_windows = len(stats['bitrates']['video'])
                streams = list(stats['bitrates'].keys())
                stats['bitrates']['time'] = np.arange(1, num_windows + 1)
                window = stats['window']
                
                df = pd.DataFrame.from_dict(stats['bitrates'])
                for s in streams:
                    df[s] = (df[s] / 1000.0 / window)
                df['kbps'] = df.iloc[:, 0:3].sum(axis=1)
                df['bpp'] = df['kbps'] * 1000 / fps /frame_size
                df['jbits'] = args.jacobian_bits

                per_frame_metrics = np.load(f'{save_dir}/metrics.npy', allow_pickle='TRUE').item()
                if len(per_frame_metrics) == 0:
                    print("PROBLEM!!!!")
                    continue
                averages = get_average_metrics(list(per_frame_metrics.values()))
                metrics = {'psnr': [], 'ssim': [], 'lpips': [], 'latency': [], 'old_lpips': []}
                for i, k in enumerate(metrics.keys()):
                        metrics[k].append(averages[i])

                for m in metrics.keys():
                    while len(metrics[m]) < df.shape[0]:
                        metrics[m].append(metrics[m][0])
                    df[m] = metrics[m]
                
                combined_df = pd.concat([df, combined_df], ignore_index=True)
                end = perf_counter()
                print("aggregating one piece of data", end - start)


        mean_df = pd.DataFrame(combined_df.mean(axis=0).to_dict(), index=[df.index.values[-1]])
        mean_df['reference_freq'] = freq
        mean_df['setting'] = args.setting
        mean_df['ssim_db'] = 10 * math.log10(1 / (1-mean_df['ssim']))
        if first:
            mean_df.to_csv(args.csv_name, header=True, index=False, mode="w")
            first = False
        else:
            mean_df.to_csv(args.csv_name, header=False, index=False, mode="a+")

if args.aggregate:
    aggregate_data()
elif args.run:
    run_experiments()
else:
    run_experiments()
    aggregate_data()
