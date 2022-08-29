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

parser = argparse.ArgumentParser(description='Low-resolution experiments.')
parser.add_argument('--downlink-trace', type=str,
                    help='downlink trace path for mahimahi (assumed to be bottleneck-free)', 
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
                    default="data/low_res_video")
parser.add_argument("--quantizer", type=int,
                    help="quantizer to compress video stream with",
                    default=32)
parser.add_argument("--lr-quantizer", type=int,
                    help="quantizer to compress low-res video stream with",
                    default=32)
parser.add_argument("--reference-update-freq", type=int,
                    help="the frequency that the reference frame is updated",
                    default=32)
parser.add_argument('--disable-mahimahi', action='store_true',
                    help='If used, traces will not be appliled to the sender')
parser.add_argument('--use_bicubic', action='store_true',
                    help='If used, used bicubic upsampling instead of prediction')
args = parser.parse_args()

""" runs video conference at different bandwidth levels
    capturing tcpdumps to measure bitrates from
    WARNING: overwrites existing data
"""
def run_experiments():
    params = {}
    save_prefix = args.save_prefix
    params['downlink_trace'] = args.downlink_trace
    params['video_file'] = args.video_file
    params['executable_dir'] = args.executable_dir 
    params['duration'] = args.duration
    params['runs'] = args.runs
    params['enable_prediction'] = True
    params['prediction_type'] = 'bicubic' if args.use_bicubic else 'use_low_res_video'
    params['quantizer'] = args.quantizer
    params['lr_quantizer'] = args.lr_quantizer
    params['reference_update_freq'] = args.reference_update_freq
    params['fps'] = 30
    params['disable_mahimahi'] = args.disable_mahimahi
    params['uplink_trace'] = args.uplink_trace
    params['save_dir'] = args.save_prefix

    shutil.rmtree(params['save_dir'], ignore_errors=True)
    os.makedirs(params['save_dir'])

    run_single_experiment(params)


""" gets bitrate info from pcap file 
    and puts it into csv for R
"""
def aggregate_data():
    first = True
    combined_df = pd.DataFrame()
    params = {}
    params['save_prefix'] = args.save_prefix
    params['runs'] = args.runs
    params['window'] = args.window
    params['duration'] = args.duration
    params['fps'] = 30

    start = perf_counter()
    combined_df = gather_data_single_experiment(params, combined_df)
    end = perf_counter()
    print("aggregating one piece of data", end - start)

    mean_df = pd.DataFrame(combined_df.mean(axis=0).to_dict(), index=[combined_df.index.values[-1]])
    mean_df['lr_resolution'] = 256
    mean_df['lr-quantizer'] = args.lr_quantizer
    mean_df['ssim_db'] = - 20 * math.log10(1-mean_df['ssim'])
    print(mean_df)
    if first:
        mean_df.to_csv(args.csv_name, header=True, index=False, mode="w")
        first = False
    else:
        mean_df.to_csv(args.csv_name, header=False, index=False, mode="a+")

run_experiments()
aggregate_data()
