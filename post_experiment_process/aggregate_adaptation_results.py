import argparse
import pandas as pd
import numpy as np
import os

parser = argparse.ArgumentParser(description='Collect Overall Average Stats from ML Pipeline.')
parser.add_argument('--save-prefix', type=str,
                    help='prefix to save logs and files in', 
                    required=True)
parser.add_argument('--csv-name', type=str,
                    help='file to save final data in', 
                    default="summary.csv")
parser.add_argument('--approaches-to-compare', type=str, nargs='+',
                    help='list of approaches (must map the base dir)', default=['personalized'])
parser.add_argument('--base-dir-list', type=str, nargs='+',
                    help='Path to results across approaches', 
                    default=['/video-conf/scratch/vibhaa_mm_log_directory/personalization'])
args = parser.parse_args()

final_df = pd.DataFrame()
for approach, exp_folder in zip(args.approaches_to_compare, args.base_dir_list):
    bitrate_df = pd.read_csv(f'{exp_folder}/compression_timeseries_sender_w1000_ms.csv')
    metrics_df = pd.read_csv(f'{exp_folder}/windowed_visual_timeseries.csv')
    combined_df = pd.concat([bitrate_df, metrics_df], axis=1) 
    combined_df['time'] = np.arange(1, len(combined_df) + 1)
    combined_df['approach'] = approach
    final_df = pd.concat([final_df, combined_df])

    # add target line
    if approach == 'vpx':
        combined_df['approach'] = 'target'
        combined_df['total_video_bitrates'] = combined_df['actual_bitrate']
        combined_df['psnr'] = 0
        combined_df['lpips'] = 1 
        combined_df['ssim'] = 0
        final_df = pd.concat([final_df, combined_df])

os.makedirs(args.save_prefix, exist_ok=True)
final_df.to_csv(f'{args.save_prefix}/{args.csv_name}', index=False, header=True)
