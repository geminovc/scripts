import pandas as pd
import argparse
import numpy as np
from utils import *
import math
from time import perf_counter

parser = argparse.ArgumentParser(description='Collect per frame stats.')
parser.add_argument('--num-runs', type=int,
                    help='number of runs to average over per experiment',
                    default=10)
parser.add_argument('--person', type=str,
                    help='person who will be resized', default='xiran')
parser.add_argument('--save-prefix', type=str,
                    help='prefix to save logs and files in', 
                    required=True)
parser.add_argument('--csv-name', type=str,
                    help='file to save final data in', 
                    default="data/frame_rate_data")
parser.add_argument('--video-name', type=str,
                    help='video name', default="0_1.mp4")
parser.add_argument('--reference-frame-frequency-list', type=int, nargs='+',
                    help='interval between reference frame in frames',
                    default=[10, 60, 300, 900, 30000])
parser.add_argument('--vpx-quantizer-list', type=int, nargs='+',
                    help='set of quantizers to quantize at',
                    default=[2, 16, 32, 48, 63])
parser.add_argument('--setting', type=str,
                    help='personalized vs. generic', 
                    default="personalized")
parser.add_argument('--resolution', type=str,
                    help='resolution of the image',
                    default='512x512')

args = parser.parse_args()


def get_single_experiment_data(first, save_dir, setting, csv_name):
    """ aggregate single experiment data by reformating per frame metrics
        dict and dumping individual frames' qualities
    """
    start = perf_counter()
    per_frame_metrics = np.load(f'{save_dir}/metrics.npy', allow_pickle='TRUE').item()
    if len(per_frame_metrics) == 0:
        print("PROBLEM!!!!")
        return

    modified_dict = {}
    modified_dict['frame_num'] = list(per_frame_metrics.keys())
    for x in ['psnr', 'ssim', 'lpips', 'old_lpips']:
        modified_dict[x] = [v.get(x, 0) for v in per_frame_metrics.values()]

    df = pd.DataFrame.from_dict(modified_dict)
    df['setting'] = setting        
    end = perf_counter()
    print("aggregating one piece of data", end - start)

    if first:
        df.to_csv(csv_name, header=True, index=False, mode="w")
    else:
        df.to_csv(csv_name, header=False, index=False, mode="a+")


""" gets metrics from npy file 
    and puts it into csv for R
"""
def aggregate_data():
    first = True
    save_prefix = args.save_prefix
    setting = args.setting
    video_name = args.video_name
    person = args.person
    resolution = args.resolution
    width, height = args.resolution.split("x")
    first = True
    
    for freq in args.reference_frame_frequency_list:
        print(f'Run {video_name} for person {person} reference frame freq {freq} setting {setting}')
        save_dir = f'{save_prefix}_{setting}/{person}/reference_freq{freq}/' + \
                f'{os.path.basename(video_name)}/run0'
        print(save_dir)

        setting_info = f'{setting}_ref{freq}'
        get_single_experiment_data(first, save_dir, setting_info, args.csv_name)
        first = False

    for quantizer in args.vpx_quantizer_list:
        setting = 'vpx'
        print(f'Run {video_name} for person {person} reference frame freq {freq} setting {setting}')
        save_dir = f'{save_prefix}_{width}_comparison_{setting}/{person}/resolution{resolution}/quantizer{quantizer}/' + \
                f'{os.path.basename(video_name)}/run0'
        print(save_dir)

        setting_info = f'{setting}_quantizer{quantizer}'
        get_single_experiment_data(first, save_dir, setting_info, args.csv_name)
        first = False


aggregate_data()
