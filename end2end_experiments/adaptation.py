import sys
sys.path.append('../')
import pandas as pd
import subprocess as sh
import argparse
import os
import log_parser
import numpy as np
from nets_utils import *
import shutil
import math
from time import perf_counter
import yaml
"""
This experiment conducts the adaptation overlay on top of gcc in aiortc.
"""
parser = argparse.ArgumentParser(description='Adaptation experiments.')
parser.add_argument('--downlink-trace', type=str,
                    help='downlink trace path for mahimahi', 
                    default="../traces/12mbps_trace")
parser.add_argument('--uplink-trace', type=str,
                    help='uplink trace path for mahimahi',
                    default="../traces/12mbps_trace")
parser.add_argument('--duration', type=int,
                    help='duration of experiment (in seconds)', 
                    default=310)
parser.add_argument('--runs', type=int,
                    help='number of runs to repeat the experiment',
                    default=1)
parser.add_argument('--window', type=int,
                    help='duration to aggregate bitrate over (in miliseconds)',
                    default=1000)
parser.add_argument('--root-dir', type=str,
                    help='name of default video directory',
                    default="/video-conf/scratch/pantea/fom_personalized_1024/")
parser.add_argument('--people', type=str, nargs='+',
                    help='person who will be resized', default=['xiran'])
parser.add_argument('--save-prefix', type=str,
                    help='prefix to save logs and files in', 
                    required=True)
parser.add_argument('--executable-dir', type=str,
                    help='folder where the video-stream cli.py executable lies', 
                    required=True)
parser.add_argument('--csv-name', type=str,
                    help='file to save final data in', 
                    default="data/adaptation")
parser.add_argument('--video-num-range', type=int, nargs=2,
                    help='video start and end range', default=[0, 4])
parser.add_argument('--quantizer-list', type=int, nargs='+',
                    help='set of quantizers to compress video stream with. -1 means full range',
                    default=[-1, 2, 16, 32, 45, 50, 55, 63])
parser.add_argument("--lr-quantizer-list", type=int, nargs='+',
                    help="set of quantizers to compress low-res video stream with",
                    default=[45, 50, 55, 63])
parser.add_argument("--reference-update-freq", type=int,
                    help="the frequency that the reference frame is updated",
                    default=18000000)
parser.add_argument('--disable-mahimahi', action='store_true',
                    help='If used, traces will not be appliled to the sender')
parser.add_argument('--generator-type', type=str, required=True,
                    help='type of the generator used for prediction')
parser.add_argument('--just-aggregate', action='store_true',
                    help='only aggregate final stats')
parser.add_argument('--just-run', action='store_true',
                    help='only run experiments')
parser.add_argument('--lr-enable-gcc', action='store_true',
                    help='If used, gcc bitrate implications will be applied')
parser.add_argument('--configs-dir', type=str,
                    help='path to config files',
                    default='../paper_configs')
parser.add_argument('--resolution', type=str,
                    help='final video resolution',
                    default='1024')

args = parser.parse_args()

""" runs video conference at different bandwidth levels
    capturing tcpdumps to measure bitrates from
    WARNING: overwrites existing data
"""
def run_experiments():
    params = {}
    save_prefix = args.save_prefix
    params['downlink_trace'] = args.downlink_trace
    params['executable_dir'] = args.executable_dir 
    params['duration'] = args.duration
    params['runs'] = args.runs
    params['enable_prediction'] = True
    params['prediction_type'] = 'use_low_res_video'
    params['reference_update_freq'] = args.reference_update_freq
    params['fps'] = 30
    params['disable_mahimahi'] = args.disable_mahimahi
    params['uplink_trace'] = args.uplink_trace
    params['lr_enable_gcc'] = args.lr_enable_gcc
    params['socket_path'] = 'adaptation.sock'
    vid_start, vid_end = args.video_num_range 
    assert(vid_end >= vid_start)

    for person in args.people:
        params['person'] = person
        video_dir = os.path.join(args.root_dir, person, "test")
        for i, video_name in enumerate(os.listdir(video_dir)):
            if i not in range(vid_start, vid_end + 1):
                continue

            video_file = os.path.join(video_dir, video_name)
            params['video_file'] = video_file
            for quantizer in args.quantizer_list:
                for lr_quantizer in args.lr_quantizer_list:
                    params['lr_quantizer'] = lr_quantizer
                    params['quantizer'] = quantizer
                    params['save_dir'] = f'{args.save_prefix}/{person}/' + \
                        f'{os.path.basename(video_name)}/' + \
                        f'lrquantizer{lr_quantizer}/quantizer{quantizer}'

                    shutil.rmtree(params['save_dir'], ignore_errors=True)
                    os.makedirs(params['save_dir'])
                    print(f'Run {video_name} for person {person} quantizer {quantizer} lr_quantizer {lr_quantizer}')

                    start = perf_counter()
                    run_single_experiment(params)
                    end = perf_counter()
                    print("single experiment took", end - start)


""" gets bitrate info from pcap file 
    and puts it into csv for R
"""
def aggregate_data():
    first = True
    vid_start, vid_end = args.video_num_range
    assert(vid_end >= vid_start)

    for quantizer in args.quantizer_list:
        for lr_quantizer in args.lr_quantizer_list:
            # average the data over multiple people, and their multiple videos
            combined_df = pd.DataFrame()
            for person in args.people:
                video_dir = os.path.join(args.root_dir, person, "test")
                for i, video_name in enumerate(os.listdir(video_dir)):
                    if i not in range(vid_start, vid_end + 1):
                        continue

                    video_file = os.path.join(video_dir, video_name)
                    params = {}
                    params['save_prefix'] = f'{args.save_prefix}/{person}/' + \
                            f'{os.path.basename(video_name)}/' + \
                            f'lrquantizer{lr_quantizer}/quantizer{quantizer}'
                    params['runs'] = args.runs
                    params['window'] = args.window
                    params['duration'] = args.duration
                    params['fps'] = 30
                    try:
                        start = perf_counter()
                        df = gather_data_single_experiment(params)
                        end = perf_counter()
                        print("aggregating one piece of data", end - start)
                        combined_df = pd.concat([df, combined_df], ignore_index=True)
                    except Exception as e:
                        print(e)

            if len(combined_df) > 0:
                mean_df = pd.DataFrame(combined_df.mean(axis=0).to_dict(),
                                    index=[combined_df.index.values[-1]])

                for metric in ['psnr', 'ssim', 'lpips', 'latency', 'orig_lpips', 'face_lpips']:
                    mean_df[f'{metric}_min'] = combined_df[f'{metric}_min'].min()
                    mean_df[f'{metric}_max'] = combined_df[f'{metric}_max'].max()

                    mean_df[f'{metric}_std'] = combined_df[metric].std()

                mean_df['ssim_db'] = - 10 * math.log10(1-mean_df['ssim'])
                mean_df['lr_quantizer'] = lr_quantizer
                mean_df['quantizer'] = quantizer

                print(mean_df)
                if first:
                    mean_df.to_csv(args.csv_name, header=True, index=False, mode="w")
                    first = False
                else:
                    mean_df.to_csv(args.csv_name, header=False, index=False, mode="a+")

start_time = time.time()
if args.just_aggregate:
    aggregate_data()
elif args.just_run:
    run_experiments()
else:
    run_experiments()
    aggregate_data()

print("The whole experiment took", time.time() - start_time)
