import pandas as pd
import subprocess as sh
import argparse
import os
import log_parser
import numpy as np
from utils import *
import shutil


parser = argparse.ArgumentParser(description='Compare VPX to learned method.')
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
                    help='number of runs to loop through per experiment',
                    default=10)
parser.add_argument('--root-dir', type=str,
                    help='name of default video directory', 
                    default="sundar_pichai.mp4")
parser.add_argument('--person-list', type=str, nargs='+',
                    help='list of people', default=['jen_psaki'])
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
    for setting in ["personalized", "vpx" "generic", "personalized"]:
        params = {}
        save_prefix = f'{args.save_prefix}_{setting}'
        params['uplink_trace'] = args.uplink_trace
        params['downlink_trace'] = args.downlink_trace
        params['executable_dir'] = args.executable_dir 
        params['duration'] = args.duration
        params['enable_prediction'] = False if setting == "vpx" else True
        params['runs'] = 1
        params['checkpoint'] = 'None' if setting != "generic" else checkpoint_dict['generic']
        params['reference_update_freq'] = 30
        
        for person in args.person_list:
            video_dir = os.path.join(args.root_dir, person, "test")
            if setting == "personalized":
                params['checkpoint'] = checkpoint_dict[person]
            
            for video_name in os.listdir(video_dir):
                video_file = os.path.join(video_dir, video_name)
                params['save_dir'] = f'{save_prefix}/{person}/{os.path.basename(video_name)}'
                params['video_file'] = f'{params["save_dir"]}/{video_name}'

                shutil.rmtree(params['save_dir'], ignore_errors=True)
                os.makedirs(params['save_dir'])

                ffmpeg_cmd = f'ffmpeg -y -stream_loop {args.num_runs} -i {video_file} ' + \
                        f'{params["video_file"]}'
                print(ffmpeg_cmd)
                os.system(ffmpeg_cmd)

                run_single_experiment(params)

                break


""" gets bitrate info from pcap file 
    and puts it into csv for R
"""
def aggregate_data():
    first = True
    
    for setting in ["personalized", "vpx" "generic", "personalized"]:
        combined_df = pd.DataFrame()
        save_prefix = f'{args.save_prefix}_{setting}'

        for person in args.person_list:
            video_dir = os.path.join(args.root_dir, person, "test")
            
            for video_name in os.listdir(video_dir):
                print(f'Run {video_name} for setting {setting} for person {person}')
                save_dir = f'{save_prefix}/{person}/{os.path.basename(video_name)}/run0'
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
                df['video_name'] = video_name

                metrics = get_video_quality_latency_over_windows(save_dir, args.window)
                for m in metrics.keys():
                    while len(metrics[m]) < df.shape[0]:
                        metrics[m].append(0)
                    df[m] = metrics[m]
                
                combined_df = pd.concat([df, combined_df], ignore_index=True)

                break
        
        mean_df = pd.DataFrame(combined_df.mean(axis=0).round(2).to_dict(), index=[df.index.values[-1]])
        mean_df['setting'] = setting
        if first:
            mean_df.to_csv(args.csv_name, header=True, index=False, mode="w")
            first = False
        else:
            mean_df.to_csv(args.csv_name, header=False, index=False, mode="a+")


run_experiments()
aggregate_data()
