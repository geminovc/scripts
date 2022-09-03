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

parser = argparse.ArgumentParser(description='VPX Setting Variations (resolution, quantization, and bitrate).')
parser.add_argument('--resolutions', type=str, nargs='+',
                    help='set of resolutions to try',
                    default=['128x128', '256x256', '512x512', '1024x1024'])
parser.add_argument('--quantizer-list', type=int, nargs='+',
                    help='set of quantizers to quantize at. -1 means full range',
                    default=[-1, 2, 16, 32, 45, 50, 55, 63])
parser.add_argument('--default-bitrate-list', type=int, nargs='+',
                    help='list of default vpx bitrate levels to run on (assumes bps)',
                    default=[100000, 200000, 500000, 1000000])
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
                    help='duration to aggregate bitrate over (in miliseconds)',
                    default=1000)
parser.add_argument('--runs', type=int,
                    help='number of runs to average over per experiment',
                    default=1)
parser.add_argument('--root-dir', type=str,
                    help='name of default video directory', 
                    default="sundar_pichai.mp4")
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
                    default="data/vpx_baseline")
parser.add_argument('--video-num-range', type=int, nargs=2,
                    help='video start and end range', default=[0, 4])
parser.add_argument('--just-aggregate', action='store_true',
                    help='only aggregate final stats')
parser.add_argument('--just-run', action='store_true',
                    help='only run experiments')
parser.add_argument('--disable-mahimahi', action='store_true',
                    help='If used, traces will not be appliled to the sender')
parser.add_argument('--enable-gcc', action='store_true',
                    help='If used, gcc bitrate implications will be applied')

args = parser.parse_args()

""" runs non-neural video conference with different vpx settings
    capturing tcpdumps to measure bitrates from
    WARNING: overwrites existing data
"""
def run_experiments():
    params = {}
    params['uplink_trace'] = args.uplink_trace
    params['downlink_trace'] = args.downlink_trace
    params['executable_dir'] = args.executable_dir 
    params['duration'] = args.duration
    params['runs'] = args.runs
    params['enable_prediction'] = False
    params['fps'] = 30
    params['disable_mahimahi'] = args.disable_mahimahi
    params['socket_path'] = 'vpx_baseline.sock'
    vid_start, vid_end = args.video_num_range
    assert(vid_end >= vid_start)
    
    base_env = os.environ.copy()
    config_path = base_env['CONFIG_PATH']
    with open(config_path) as f:
        new_config = yaml.safe_load(f)
    for resolution in args.resolutions:
        # write a new config from the template CONFIG_PATH for vpx based on resolution
        width, height = resolution.split("x")
        new_config['dataset_params']['frame_shape'] = [int(width), int(width), 3]
        os.makedirs(f'{args.save_prefix}/resolution{resolution}', exist_ok=True)
        new_config_path = f'{args.save_prefix}/resolution{resolution}/resolution{resolution}_vpx.yaml'
        with open(new_config_path, 'w') as file:
            doc = yaml.dump(new_config, file)

        params['config_path'] = new_config_path

        for person in args.people:
            video_dir = os.path.join(args.root_dir, person, "test")
            
            for i, video_name in enumerate(os.listdir(video_dir)):
                if i not in range(vid_start, vid_end + 1):
                    continue
                
                video_file = os.path.join(video_dir, video_name)
                params['save_dir'] = f'{args.save_prefix}/resolution{resolution}/{person}/' + \
                        f'{os.path.basename(video_name)}'
                params['video_file'] = f'{params["save_dir"]}/{video_name}'

                os.makedirs(params['save_dir'], exist_ok=True)

                start = perf_counter()
                width, height = resolution.split("x")
                
                ffprobe_cmd = f'ffprobe -v error -select_streams v -show_entries ' + \
                        f'stream=width,height -of csv=p=0:s=x {video_file}'
                original_resolution = sh.check_output(ffprobe_cmd, shell=True).decode("utf-8")[:-1]
                original_width, original_height = original_resolution.split("x")

                if original_height == height and original_width == width:
                    cp_cmd = f'cp {video_file} {params["video_file"]}'
                    print(cp_cmd)
                    os.system(cp_cmd)
                    end = perf_counter()
                    print("cp command took", end - start)
                else:
                    ffmpeg_cmd = f'ffmpeg -hide_banner -loglevel error -y -i {video_file} ' + \
                            f'-vf scale={width}:{height} {params["video_file"]}'
                    print(ffmpeg_cmd)
                    os.system(ffmpeg_cmd)
                    end = perf_counter()
                    print("ffmpeg command took", end - start)

                for quantizer in args.quantizer_list:
                    for vpx_default_bitrate in args.default_bitrate_list:
                        if args.enable_gcc:
                            vpx_min_bitrate_range = [50000]
                            vpx_max_bitrate_range = [1500000]
                        else:
                            vpx_min_bitrate_range = [vpx_default_bitrate]
                            vpx_max_bitrate_range = [vpx_default_bitrate]

                        for vpx_min_bitrate in vpx_min_bitrate_range:
                            for vpx_max_bitrate in vpx_max_bitrate_range:

                                params['save_dir'] = f'{args.save_prefix}/resolution{resolution}/{person}/' + \
                                        f'{os.path.basename(video_name)}/quantizer{quantizer}/' + \
                                        f'vpx_min{vpx_min_bitrate}_default{vpx_default_bitrate}_max{vpx_max_bitrate}bitrate'

                                start = perf_counter()
                                shutil.rmtree(params['save_dir'], ignore_errors=True)
                                os.makedirs(params['save_dir'])
                                end = perf_counter()
                                print("rm command took", end - start)

                                params['quantizer'] = quantizer
                                params['vpx_default_bitrate'] = vpx_default_bitrate
                                params['vpx_min_bitrate'] = vpx_min_bitrate
                                params['vpx_max_bitrate'] = vpx_max_bitrate

                                start = perf_counter()
                                print(f'Run {video_name} for person {person} resolution {resolution} quantizer {quantizer}')
                                print(f'vpx bitrates: min {vpx_min_bitrate} default {vpx_default_bitrate} max {vpx_max_bitrate}')
                                print(params['save_dir'])
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
    fps = 30
 
    for resolution in args.resolutions:
        for quantizer in args.quantizer_list:
            for vpx_default_bitrate in args.default_bitrate_list:
                if args.enable_gcc:
                    vpx_min_bitrate_range = [50000]
                    vpx_max_bitrate_range = [1500000]
                else:
                    vpx_min_bitrate_range = [vpx_default_bitrate]
                    vpx_max_bitrate_range = [vpx_default_bitrate]

                for vpx_min_bitrate in vpx_min_bitrate_range:
                    for vpx_max_bitrate in vpx_max_bitrate_range:
                        # average over multiple videos of multiple people
                        combined_df = pd.DataFrame()
                        for person in args.people:

                            video_dir = os.path.join(args.root_dir, person, "test")
                            for i, video_name in enumerate(os.listdir(video_dir)):
                                if i not in range(vid_start, vid_end + 1):
                                    continue

                                print(f'Run {video_name} for person {person} resolution {resolution} quantizer {quantizer}')
                                print(f'vpx bitrates: min {vpx_min_bitrate} default {vpx_default_bitrate} max {vpx_max_bitrate}')
                                save_prefix =f'{args.save_prefix}/resolution{resolution}/{person}/' + \
                                    f'{os.path.basename(video_name)}/quantizer{quantizer}/' + \
                                    f'vpx_min{vpx_min_bitrate}_default{vpx_default_bitrate}_max{vpx_max_bitrate}bitrate'
                                params = {}
                                params['save_prefix'] = save_prefix
                                params['runs'] = args.runs
                                params['window'] = args.window
                                params['duration'] = args.duration
                                params['fps'] = fps
                                params['resolution'] = resolution
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
                            mean_df['ssim_db'] = - 20 * math.log10(1-mean_df['ssim'])

                            mean_df['resolution'] = resolution
                            mean_df['quantizer'] = quantizer
                            mean_df['vpx_default_bitrate'] = vpx_default_bitrate
                            mean_df['vpx_min_bitrate'] = vpx_min_bitrate
                            mean_df['vpx_max_bitrate'] = vpx_max_bitrate

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
