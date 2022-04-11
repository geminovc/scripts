import pandas as pd
import subprocess as sh
import argparse
import os
import log_parser
import numpy as np
from utils import *
import shutil


parser = argparse.ArgumentParser(description='Compression Factor Variation.')
parser.add_argument('--resolutions', type=str, nargs='+',
                    help='set of resolutions to try',
                    default=['256x256', '512x512', '768x768', '1024x1024'])
parser.add_argument('--quantizer-list', type=int, nargs='+',
                    help='set of quantizers to quantize at',
                    default=[2, 16, 32, 48, 62])
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
parser.add_argument('--num-runs', type=int,
                    help='number of runs to average over per experiment',
                    default=10)
parser.add_argument('--root-dir', type=str,
                    help='name of default video directory', 
                    default="sundar_pichai.mp4")
parser.add_argument('--person', type=str,
                    help='person who will be resized', default='xiran')
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
    params['executable_dir'] = args.executable_dir 
    params['duration'] = args.duration
    params['runs'] = 1
    params['enable_prediction'] = False
    person = args.person
    
    for resolution in args.resolutions:
        video_dir = os.path.join(args.root_dir, person, "test")
        
        for video_name in os.listdir(video_dir):
            video_file = os.path.join(video_dir, video_name)
            params['save_dir'] = f'{save_prefix}_vpx/{person}/resolution{resolution}/' + \
                    f'{os.path.basename(video_name)}'
            params['video_file'] = f'{params["save_dir"]}/{video_name}'

            shutil.rmtree(params['save_dir'], ignore_errors=True)
            os.makedirs(params['save_dir'])

            width, height = resolution.split("x")
            ffmpeg_cmd = f'ffmpeg -hide_banner -loglevel error -y -i {video_file} ' + \
                    f'-vf scale={width}:{height} {params["video_file"]}'
            print(ffmpeg_cmd)
            os.system(ffmpeg_cmd)

            for quantizer in args.quantizer_list:
                params['save_dir'] = f'{save_prefix}_vpx/{person}/resolution{resolution}/quantizer{quantizer}/' + \
                    f'{os.path.basename(video_name)}'
                shutil.rmtree(params['save_dir'], ignore_errors=True)
                os.makedirs(params['save_dir'])
                
                params['quantizer'] = quantizer
                run_single_experiment(params)


""" gets bitrate info from pcap file 
    and puts it into csv for R
"""
def aggregate_data():
    first = True
    save_prefix = args.save_prefix
    person = args.person
    
    for resolution in args.resolutions:
        for quantizer in args.quantizer_list:
            combined_df = pd.DataFrame()

            video_dir = os.path.join(args.root_dir, person, "test")
            
            for video_name in os.listdir(video_dir):
                print(f'Run {video_name} for person {person} resolution {resolution}')
                save_dir = f'{save_prefix}_vpx/{person}/resolution{resolution}/quantizer{quantizer}/' + \
                        f'{os.path.basename(video_name)}/run0/'
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
                    df[s] = (df[s] / 1000.0 / window).round(2)
                df['kbps'] = df.iloc[:, 0:3].sum(axis=1).round(2) 
                df['resolution'] = resolution

                per_frame_metrics = np.load(f'{save_dir}/metrics.npy', allow_pickle='TRUE').item()
                averages = get_average_metrics(list(per_frame_metrics.values()))
                metrics = {'psnr': [], 'ssim': [], 'lpips': [], 'latency': []}
                for i, k in enumerate(metrics.keys()):
                        metrics[k].append(averages[i])

                for m in metrics.keys():
                    while len(metrics[m]) < df.shape[0]:
                        metrics[m].append(0)
                    df[m] = metrics[m]
                
                combined_df = pd.concat([df, combined_df], ignore_index=True)

            mean_df = pd.DataFrame(combined_df.mean(axis=0).round(2).to_dict(), index=[df.index.values[-1]])
            mean_df['resolution'] = resolution
            mean_df['quantizer'] = quantizer
            if first:
                mean_df.to_csv(args.csv_name, header=True, index=False, mode="w")
                first = False
            else:
                mean_df.to_csv(args.csv_name, header=False, index=False, mode="a+")


run_experiments()
aggregate_data()
