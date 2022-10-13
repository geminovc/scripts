import argparse
import pandas as pd
import numpy as np
import matplotlib.image
import os
from ml_pipeline_utils import *

parser = argparse.ArgumentParser(description='Isolate frames based on metrics range')
parser.add_argument('--person-list', type=str, nargs='+',
                    help='people whose results will be aggregated', default=['xiran'])
parser.add_argument('--save-prefix', type=str,
                    help='prefix to save strip in', 
                    required=True)
parser.add_argument('--approaches-to-compare', type=str, nargs='+',
                    help='list of approaches (must map the base dir)', default=['personalized'])
parser.add_argument('--base-dir-list', type=str, nargs='+',
                    help='Path to results across approaches', 
                    default=['/video-conf/scratch/vibhaa_mm_log_directory/personalization'])
parser.add_argument('--img-width', type=int,
                    help='Frame width in pixels', default=1024)
parser.add_argument('--filter-setting', type=str,
                    help='setting to filter on', default='generic')
parser.add_argument('--filter-metric', type=str,
                    help='metric to filter by', default='orig_lpips', 
                    choices=['orig_lpips', 'ssim_db', 'psnr'])
parser.add_argument('--metric-low', type=float,
                    help='Lower end of metric', default=0)
parser.add_argument('--metric-high', type=float,
                    help='Higher end of metric', default=1)
args = parser.parse_args()


strip = []
labels = ['Reference', 'Target']
final_img = None
os.makedirs(args.save_prefix, exist_ok=True)
img_width = args.img_width

for (approach, base_dir) in zip(args.approaches_to_compare, args.base_dir_list):
    settings_to_compare = settings[approach] 
    if 'main_exp' in approach:
        setting_to_compare = ['fomm'] if 'fomm' in approach else ['lr256_tgt45Kb']
    if 'vpx' in approach:
        continue
    
    for person in args.person_list:
        folder, prefix = get_folder_prefix(approach, args.filter_setting, base_dir, person)
        metrics_file = f'{folder}/{prefix}_per_frame_metrics.txt'
        
        cur_frame = pd.read_csv(metrics_file)
        relevant_rows = cur_frame.loc[(cur_frame[args.filter_metric] >= args.metric_low) \
                & (cur_frame[args.filter_metric] <= args.metric_high)]
        
        if relevant_rows.shape[0] > 0:
            sample = relevant_rows.sample(n=20)
        else:
            continue

        num = 0
        for index, row in sample.iterrows():
            frame_num = row['frame']
            video_num = row['video_num']
            row_in_strip = []
            num += 1

            print(person, frame_num, video_num)
            continue
            
            for setting in settings_to_compare:
                folder, _ = get_folder_prefix(approach, setting, base_dir, person)
                
                prediction = extract_prediction(person, frame_num, video_num, \
                        get_offset(setting, approach), folder, setting, approach, img_width, \
                        args.save_prefix)
                if len(row_in_strip) == 0:
                    (src, tgt) = extract_src_tgt(person, frame_num, video_num, folder, img_width)
                    row_in_strip = [src, tgt]
                
                row_in_strip.append(prediction)
                if num == 1:
                    labels.append(get_label(setting, approach))

            completed_row = np.concatenate(row_in_strip, axis=1)
            strip.append(completed_row)

if len(strip) > 0:
    final_img = np.concatenate(strip, axis=0)
            
# save img data
if final_img is not None:
    label = make_label(labels, img_width)
    final_img = np.concatenate([label, final_img], axis=0)
    matplotlib.image.imsave(f'{args.save_prefix}/strip.pdf', final_img)
