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
                    default="bw_data")
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
    save_prefix = args.save_prefix
    uplink_trace = args.uplink_trace
    for run_num in range(args.runs):
        save_dir = f'{save_prefix}/run{run_num}'
        dump_file = f'{save_dir}/sender.log'
        saved_video_file = f'{save_dir}/received.mp4'
        '''
        stats = log_parser.gather_trace_statistics(dump_file, args.window)
        num_windows = len(stats['bitrates']['video'])
        streams = list(stats['bitrates'].keys())
        stats['bitrates']['time'] = np.arange(1, num_windows + 1)
        
        df = pd.DataFrame.from_dict(stats['bitrates'])
        for s in streams:
            df[s] = (df[s] / 1000.0 / args.window).round(2)
        df['kbps'] = df.iloc[:, 0:3].sum(axis=1).round(2) 
        df['fps'] = get_fps_from_video(saved_video_file)
        df['uplink_bw'] = bw

        metrics = get_video_quality_latency_over_windows(save_dir, args.window)
        for m in metrics.keys():
            while len(metrics[m]) < df.shape[0]:
                metrics[m].append(0)
            df[m] = metrics[m]

        if first:
            df.to_csv(f'{save_dir}/{args.csv_name}', header=True, index=False, mode="w")
            first = False
        else:
            df.to_csv(f'{save_dir}/{args.csv_name}', header=False, index=False, mode="a+")
        '''

        if os.path.isfile(f'{save_dir}/mahimahi.log'):
            sh.run(f'mm-graph {save_dir}/mahimahi.log {args.duration} --no-port \
                    --xrange \"0:{args.duration}\" --yrange \"0:3\" --y2range \"0:2000\" \
                    > {save_dir}/mahimahi.eps 2> {save_dir}/mmgraph.log', shell=True)

        print(f"\033[92mSender side \033[0m")
        os.system(f'python3 ../post_experiment_process/plot_bw_trace_vs_estimation.py \
                --log-path {save_dir}/sender.log --trace-path {uplink_trace} \
                --save-dir {save_dir} --output-name sender --window 500')

        os.system(f'python3 ../post_experiment_process/estimate_rtt_at_sender.py \
                --log-path {save_dir}/sender.log \
                --save-dir {save_dir} --output-name estimation_at_sender')

        print(f"\033[92mReceiver side \033[0m")
        os.system(f'python3 ../post_experiment_process/plot_bw_trace_vs_estimation.py \
                --log-path {save_dir}/receiver.log --trace-path {args.downlink_trace} \
                --save-dir {save_dir} --output-name receriver --window 500')

        os.system(f'python3 ../post_experiment_process/estimate_rtt_at_sender.py \
                --log-path {save_dir}/receiver.log \
                --save-dir {save_dir} --output-name estimation_at_receiver')

run_experiments()
aggregate_data()
