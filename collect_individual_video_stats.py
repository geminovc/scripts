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
parser.add_argument('--reference-frame-frequency', type=int,
                    help='interval between reference frame in frames', default=300)
parser.add_argument('--vpx-quantizer', type=int,
                    help='quantizer to quantize at', default=32)
parser.add_argument('--setting', type=str,
                    help='personalized vs. generic', 
                    default="personalized")
parser.add_argument('--resolution', type=str,
                    help='resolution of the image',
                    default='512x512')
parser.add_argument('--video-num-range', type=int, nargs=2,
                    help='video start and end range', default=[0, 4])
parser.add_argument('--root-dir', type=str,
                    help='name of default video directory', 
                    default="sundar_pichai.mp4")
parser.add_argument('--people', type=str, nargs='+',
                    help='people whose data will be aggregated', default=['xiran'])

args = parser.parse_args()

def spell_check(person):
    if person == "trever_noah":
        return "Trevor Noah"
    elif person == "seth_meyer":
        return "Seth Meyers"
    elif person == "jen_psaki":
        return "Jen Psaki"
    elif person == "kayleigh":
        return "Kayleigh McEnany"
    elif person == "tucker":
        return "Tucker Carlson"
    
    return person


def get_single_experiment_data(first, save_dir, setting, csv_name, person, video_num):
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
    df['person'] = spell_check(person)
    df['video_num'] = video_num
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
    freq = args.reference_frame_frequency
    quantizer = args.vpx_quantizer
    resolution = args.resolution
    width, height = args.resolution.split("x")
    vid_start, vid_end = args.video_num_range
    first = True
    
    for person in args.people:
        video_dir = os.path.join(args.root_dir, person, "test")
        for i, video_name in enumerate(os.listdir(video_dir)):
            if i not in range(vid_start, vid_end + 1):
                continue
            
            print(f'Run {video_name} for person {person} reference frame freq {freq} setting {setting}')
            if setting in ["personalized", "generic"]:
                save_dir = f'{save_prefix}_{setting}/{person}/reference_freq{freq}/' + \
                    f'{os.path.basename(video_name)}/run0'
            else:
                save_dir = f'{save_prefix}_{width}_comparison_{setting}/{person}/resolution{resolution}/' + \
                    f'quantizer{quantizer}/{os.path.basename(video_name)}/run0'
            print(save_dir)

            setting_info = f'{person}_{i}'
            get_single_experiment_data(first, save_dir, setting_info, args.csv_name, person, i)
            first = False

aggregate_data()
