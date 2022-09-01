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
from checkpoints import structure_based_checkpoint_dict
from time import perf_counter
import math

parser = argparse.ArgumentParser(description='Compare different structures of learned keypoint-based models.')
parser.add_argument('--uplink-trace', type=str,
                    help='uplink trace path for mahimahi', 
                    default="traces/12mbps_trace")
parser.add_argument('--downlink-trace', type=str,
                    help='downlink trace path for mahimahi', 
                    default="traces/12mbps_trace")
parser.add_argument('--duration', type=int,
                    help='duration of experiment (in seconds)', 
                    default=310)
parser.add_argument('--window', type=float,
                    help='duration to aggregate bitrate over (in miliseconds)',
                    default=1000)
parser.add_argument('--runs', type=int,
                    help='number of runs to loop through per experiment',
                    default=1)
parser.add_argument('--root-dir', type=str,
                    help='name of default video directory', 
                    default="sundar_pichai.mp4")
parser.add_argument('--people', type=str, nargs='+',
                    help='list of people', default=['jen_psaki'])
parser.add_argument('--save-prefix', type=str,
                    help='prefix to save logs and files in', 
                    required=True)
parser.add_argument('--configs-dir', type=str,
                    help='path to config files', 
                    default='../paper_configs')
parser.add_argument('--executable-dir', type=str,
                    help='folder where the video-stream cli.py executable lies', 
                    required=True)
parser.add_argument('--csv-name', type=str,
                    help='file to save final data in', 
                    default="data/fom_baseline")
parser.add_argument('--resolution', type=str,
                    help='video resolution',
                    default="512")
parser.add_argument('--video-num-range', type=int, nargs=2,
                    help='video start and end range', default=[0, 4])
parser.add_argument('--setting-list', type=str, nargs='+',
                    help='list of settings',
                    default=['without_hr_skip_connections', 'fom_standard',
                            'only_upsample_blocks', 'with_hr_skip_connections'])
parser.add_argument('--quantizer-list', type=int, nargs='+',
                    help='set of quantizers to compress video stream with. -1 means full range',
                    default=[-1, 2, 16, 32, 45, 50, 55, 63])
parser.add_argument("--reference-update-freq-list", type=int, nargs='+',
                    help="the list of frequency that the reference frame is updated",
                    default=[0])
parser.add_argument('--disable-mahimahi', action='store_true',
                    help='If used, traces will not be appliled to the sender')
parser.add_argument('--just-aggregate', action='store_true',
                    help='only aggregate final stats')
parser.add_argument('--just-run', action='store_true',
                    help='only run experiments')
args = parser.parse_args()

""" runs video conference with different setting for keypoint-based models
    capturing tcpdumps to measure bitrates from
    WARNING: overwrites existing data
"""
settings = [f"resolution{args.resolution}_{setting}" for setting in args.setting_list]
print(settings)
def run_experiments():
    params = {}
    params['uplink_trace'] = args.uplink_trace
    params['downlink_trace'] = args.downlink_trace
    params['executable_dir'] = args.executable_dir
    params['duration'] = args.duration
    params['runs'] = args.runs
    params['enable_prediction'] = True
    params['prediction_type'] = 'keypoints'
    params['checkpoint'] = 'None'
    params['reference_update_freq'] = args.reference_update_freq
    params['disable_mahimahi'] = args.disable_mahimahi
    vid_start, vid_end = args.video_num_range
    assert(vid_end >= vid_start)

    for setting in settings:
        print(setting)
        params['socket_path'] = f'kp_{setting}.sock'
        params['config_path'] = f'{args.configs_dir}/{setting}.yaml'
        for person in args.people:
            params['checkpoint'] = structure_based_checkpoint_dict[setting][person]
            video_dir = os.path.join(args.root_dir, person, "test")
            for i, video_name in enumerate(os.listdir(video_dir)):
                if i not in range(vid_start, vid_end + 1):
                    continue

                video_file = os.path.join(video_dir, video_name)
                params['video_file'] = video_file
                #ffmpeg_cmd = f'ffmpeg -hide_banner -loglevel error -y -stream_loop {args.runs} -i {video_file} ' + \
                #        f'{params["video_file"]}'
                #print(ffmpeg_cmd)
                #os.system(ffmpeg_cmd)
                for quantizer in args.quantizer_list:
                    for reference_update_freq in args.reference_update_freq_list:
                        params['reference_update_freq'] = reference_update_freq
                        params['quantizer'] = quantizer
                        params['save_dir'] = f'{args.save_prefix}/{setting}/{person}/' + \
                        f'{os.path.basename(video_name)}/quantizer{quantizer}/reference_update_freq{reference_update_freq}'
                        shutil.rmtree(params['save_dir'], ignore_errors=True)
                        os.makedirs(params['save_dir'])
                        print(f'Run {video_name} for person {person} quantizer {quantizer}')

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
        for setting in settings:
            for reference_update_freq in args.reference_update_freq_list:
                # average the data over multiple people, and their multiple videos
                combined_df = pd.DataFrame()
                for person in args.people:
                    video_dir = os.path.join(args.root_dir, person, "test")
                    
                    for i, video_name in enumerate(os.listdir(video_dir)):
                        if i not in range(vid_start, vid_end + 1):
                            continue

                        video_file = os.path.join(video_dir, video_name)
                        params = {}
                        params['save_prefix'] = f'{args.save_prefix}/{setting}/{person}/' + \
                        f'{os.path.basename(video_name)}/quantizer{quantizer}/reference_update_freq{reference_update_freq}'
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
                    mean_df = pd.DataFrame(combined_df.mean(axis=0).to_dict(), index=[combined_df.index.values[-1]])
                    mean_df['ssim_db'] = - 20 * math.log10(1-mean_df['ssim'])
                    mean_df['quantizer'] = quantizer
                    mean_df['kp_model'] = setting
                    mean_df['reference_update_freq'] = reference_update_freq

                    print(mean_df)
                    if first:
                        mean_df.to_csv(args.csv_name, header=True, index=False, mode="w")
                        first = False
                    else:
                        mean_df.to_csv(args.csv_name, header=False, index=False, mode="a+")


if args.just_aggregate:
    aggregate_data()
elif args.just_run:
    run_experiments()
else:
    run_experiments()
    aggregate_data()
