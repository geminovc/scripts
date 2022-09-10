import argparse
import pandas as pd
import numpy as np
import matplotlib.image
import os


parser = argparse.ArgumentParser(description='Collect Overall Average Stats from ML Pipeline.')
parser.add_argument('--person-list', type=str, nargs='+',
                    help='people whose results will be aggregated', default=['xiran'])
parser.add_argument('--save-prefix', type=str,
                    help='prefix to save logs and files in', 
                    required=True)
parser.add_argument('--csv-name', type=str,
                    help='file to save final data in', 
                    default="data/frame_rate_data")
parser.add_argument('--approaches-to-compare', type=str, nargs='+',
                    help='list of approaches', default=['personalized', 'generic'])
parser.add_argument('--base-dir', type=str,
                    help='Path to results', default='/video-conf/scratch/vibhaa_mm_log_directory/personalization')
parser.add_argument('--frame-num', type=int,
                    help='Frame number extracted from all video strips', default=1786)
parser.add_argument('--img-width', type=int,
                    help='Frame width in pixels', default=1024)
parser.add_argument('--video-num', type=str,
                    help='Default video to use', default='/video_conf/scratch/vibhaa_mm_directory/personalization')
args = parser.parse_args()


def get_offset(approach):
    """ return offset at which prediction is found based on approach """
    if 'personalization' in approach or 'generic' in approach:
        offset = 6
    elif 'pure_upsampling' in approach:
        offset = 2
    elif '3_pathways' in approach or 'lr_decoder' in approach:
        offset = 6
    elif 'bicubic' in approach:
        offset = 0
    else: 
        # standard FOMM or with skip connections
        offset = 6
    return offset

def extract_prediction(person, frame_id, video_num, offset, folder):
    """ retrieve the prediction from strip consisting of all intermediates """
    prefix = f'{video_num}.mp4_frame{frame_id}.npy'
    img = np.load(f'{folder}/visualization/{prefix}')
    prediction = img[:, offset*args.img_width: (offset + 1)*args.img_width, :]
    if offset == 0:
        prediction *= 255
        prediction = prediction.astype(np.uint8)
    matplotlib.image.imsave(f'{args.save_prefix}/full_prediction.pdf', img)
    return prediction


df_dict = {}
strip = []
base_dir = args.base_dir
# aggregate results across all people for each approach
for person in args.person_list:
    row_in_strip = []
    for approach in args.approaches_to_compare:
        if approach == "generic":
            folder = f'{base_dir}/{approach}/reconstruction_single_source_{person}'
            prefix = f'single_source_{person}'
        else:
            folder = f'{base_dir}/{approach}/{person}/reconstruction_single_source'
            prefix = f'single_source'

        metrics_file = f'{folder}/{prefix}_per_frame_metrics.txt'
        cur_frame = pd.read_csv(metrics_file)
        cur_frame['approach'] = approach

        if approach not in df_dict:
            df_dict[approach] = cur_frame
        else:
            df_dict[approach] = pd.concat([df_dict[approach], cur_frame])

        prediction = extract_prediction(person, args.frame_num, args.video_num, get_offset(approach), folder)
        row_in_strip.append(prediction)
    
    completed_row = np.concatenate(row_in_strip, axis=1)
    strip.append(completed_row)
final_img = np.concatenate(strip, axis=0)
    
# compute average for each approach
final_df = pd.DataFrame()
for approach in args.approaches_to_compare:
    average_df = pd.DataFrame(df_dict[approach].mean().to_dict(), \
                    index=[df_dict[approach].index.values[-1]])
    average_df['approach'] = approach
    final_df = pd.concat([final_df, average_df])

# save all data
os.makedirs(args.save_prefix, exist_ok=True)  
final_df.to_csv(f'{args.save_prefix}/{args.csv_name}', index=False, header=True)
matplotlib.image.imsave(f'{args.save_prefix}/strip.pdf', final_img)
