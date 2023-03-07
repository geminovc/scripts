import argparse
import pandas as pd
import numpy as np
import matplotlib.image
import os
from ml_pipeline_utils import *

parser = argparse.ArgumentParser(description='Collect Overall Average Stats from ML Pipeline.')
parser.add_argument('--person-list', type=str, nargs='+',
                    help='people whose results will be aggregated', default=['xiran'])
parser.add_argument('--people-for-strip', type=str, nargs='+',
                    help='people whose visuals will be saved', default=['xiran'])
parser.add_argument('--save-prefix', type=str,
                    help='prefix to save logs and files in', 
                    required=True)
parser.add_argument('--csv-name', type=str,
                    help='file to save final data in', 
                    default="data/frame_rate_data")
parser.add_argument('--approaches-to-compare', type=str, nargs='+',
                    help='list of approaches (must map the base dir)', default=['personalized'])
parser.add_argument('--base-dir-list', type=str, nargs='+',
                    help='Path to results across approaches', 
                    default=['/video-conf/scratch/vibhaa_mm_log_directory/personalization'])
parser.add_argument('--frame-num', type=int,
                    help='Frame number extracted from all video strips', default=1786)
parser.add_argument('--img-width', type=int,
                    help='Frame width in pixels', default=1024)
parser.add_argument('--video-num', type=str,
                    help='Default video to use', default='/video_conf/scratch/vibhaa_mm_directory/personalization')
parser.add_argument('--summarize', action='store_true', 
                    help='summarize results')
parser.add_argument('--cdf', action='store_true',
                    help='generate cdf across frames/videos')
parser.add_argument('--per-video', action='store_true', 
                    help='use videos for cdf, else defaults to frames')
args = parser.parse_args()




final_df = pd.DataFrame()
strip = []
final_img = None
os.makedirs(args.save_prefix, exist_ok=True)
img_width = args.img_width

# adjust approaches if need be
if args.approaches_to_compare == ['encoder_in_training']:
    approaches_to_compare = [f'encoder_effect:{x}' for x in \
            ['no_encoder', 'tgt15Kb', 'tgt45Kb', 'tgt75Kb', 'tgt_random']]
    base_dir_list = args.base_dir_list * 5
else:
    approaches_to_compare = args.approaches_to_compare
    base_dir_list = args.base_dir_list


# aggregate results across all people for each setting for each approach
labels = ['Reference', 'Target']
if args.summarize:
    num = 0
    for (approach, base_dir) in zip(approaches_to_compare, base_dir_list):
        settings_to_compare = settings[approach]
        df_dict = {}
        for person in args.person_list:
            num += 1
            row_in_strip = []
            
            for setting in settings_to_compare:
                folder, prefix = get_folder_prefix(approach, setting, base_dir, person)
                metrics_file = f'{folder}/{prefix}_per_frame_metrics.txt'
                print(f'reading {metrics_file}')
                cur_frame = pd.read_csv(metrics_file)

                if setting not in df_dict:
                    df_dict[setting] = cur_frame
                else:
                    df_dict[setting] = pd.concat([df_dict[setting], cur_frame])

                # skip multiple settings for extracting strip for main exp
                if 'main_exp' in approach or 'encoder_effect' in approach or 'dropout' in approach:
                    continue

                prediction = extract_prediction(person, args.frame_num, args.video_num, \
                        get_offset(setting, approach), folder, setting, approach, \
                        img_width, args.save_prefix)
                if approach == "model_ablation" or approach == 'design_model_comparison':
                    if 'ours' in setting or 'fomm_3_pathways' in setting:
                        (src, tgt) = extract_src_tgt(person, args.frame_num, args.video_num, folder, 
                                img_width)
                        row_in_strip = [src, tgt] + row_in_strip
                elif len(row_in_strip) == 0:
                    (src, tgt) = extract_src_tgt(person, args.frame_num, args.video_num, folder, img_width)
                    row_in_strip = [src, tgt]
                row_in_strip.append(prediction)
                if num == 1:
                    labels.append(get_label(setting, approach))
        
            if person in args.people_for_strip and len(row_in_strip) > 0:
                if any(item is None for item in row_in_strip):
                    print('Some invalid offset, stopping')
                    quit()
                completed_row = np.concatenate(row_in_strip, axis=1)
                strip.append(completed_row)
        if len(strip) > 0:
            final_img = np.concatenate(strip, axis=0)
            
        # compute average + stddev for each setting
        for setting in settings_to_compare:
            average_df = pd.DataFrame(df_dict[setting].mean().to_dict(), \
                            index=[df_dict[setting].index.values[-1]])
            std_dev = df_dict[setting][metrics_of_interest].std()
            average_df['setting'] = setting
            average_df['approach'] = approach.split(':')[1] if ':' in approach else approach
            average_df['kbps'] = average_df['reference_kbps'] + average_df['lr_kbps']
            for m in metrics_of_interest:
                average_df[f'{m}_sd'] = std_dev[m]
            final_df = pd.concat([final_df, average_df])
    # same summary in csv
    final_df.to_csv(f'{args.save_prefix}/{args.csv_name}', index=False, header=True)


# form strip separately for main experiment/encoder effect
    if 'main_exp' in approaches_to_compare[0] or 'encoder_effect' in approaches_to_compare[0]:
        num = 0
        for person in args.person_list:
            num += 1
            row_in_strip = []
            for (approach, base_dir) in zip(approaches_to_compare, base_dir_list):
                if 'vpx' in approach:
                    continue

                if 'dropout' in approach:
                    setting = settings[approach][0]
                    folder = f'{base_dir}/reconstruction_single_source_{person}'
                    prefix = f'single_source_{person}'
                elif 'main_exp' in approach:
                    setting = 'lr256_tgt75Kb' if 'fomm' not in approach else 'fomm'
                    folder = f'{base_dir}/{setting}/{person}/reconstruction_single_source'
                    prefix = f'single_source'
                else:
                    model_type = f'lr128_{approach.split(":")[-1]}'
                    setting = '45Kb'
                    folder = f'{base_dir}/{model_type}/{person}/reconstruction_single_source_{setting}'
                    prefix = f'single_source_{setting}'

                prediction = extract_prediction(person, args.frame_num, args.video_num, \
                        get_offset(setting, approach), folder, setting, approach, img_width, \
                        args.save_prefix)
                if approach == 'main_exp:ours' or approach == 'main_exp:no_dropout':
                    (src, tgt) = extract_src_tgt(person, args.frame_num, args.video_num, folder, img_width)
                    row_in_strip = [src, tgt] + row_in_strip
                elif 'encoder' in approach and len(row_in_strip) == 0:
                    (src, tgt) = extract_src_tgt(person, args.frame_num, args.video_num, folder, img_width)
                    row_in_strip = [src, tgt]

                
                if num == 1:
                    labels.append(get_label(setting, approach))
                row_in_strip.append(prediction)
            
            if person in args.people_for_strip and len(row_in_strip) > 0:
                if any(item is None for item in row_in_strip):
                    print('Some invalid offset, stopping')
                    quit()
                completed_row = np.concatenate(row_in_strip, axis=1)
                strip.append(completed_row)
        if len(strip) > 0:
            final_img = np.concatenate(strip, axis=0)
            
    # save img data
    if final_img is not None:
        label = make_label(labels, img_width)
        print(np.shape(label), np.shape(final_img))
        # final_img = np.concatenate([label, final_img], axis=0)
        matplotlib.image.imsave(f'{args.save_prefix}/video{args.video_num}_frame{args.frame_num}_75Kb.pdf', final_img)


# aggregate results across all people for each setting for each approach
elif args.cdf:
    for (approach, base_dir) in zip(approaches_to_compare, base_dir_list):
        settings_to_compare = settings[approach] 
        if 'main_exp' in approach:
            setting_to_compare = ['fomm'] if 'fomm' in approach else ['lr256_tgt45Kb']
        if 'vpx' in approach:
            continue
        
        df_dict = {}
        for person in args.person_list:
            for setting in settings_to_compare:
                folder, prefix = get_folder_prefix(approach, setting, base_dir, person)
                metrics_file = f'{folder}/{prefix}_per_frame_metrics.txt'
                print(f'reading {metrics_file}')
                cur_frame = pd.read_csv(metrics_file)
                if args.per_video:
                    avg_df = cur_frame.groupby('video_num').mean().reset_index()
                else:
                    avg_df = cur_frame
                avg_df['person'] = person
                
                if setting not in df_dict:
                    df_dict[setting] = avg_df
                else:
                    df_dict[setting] = pd.concat([df_dict[setting], avg_df])
        
        for setting in settings_to_compare:
            setting_df = df_dict[setting]
            setting_df['setting'] = setting
            setting_df['approach'] = approach.split(':')[1] if ':' in approach else approach
            setting_df['kbps'] = setting_df['reference_kbps'] + setting_df['lr_kbps']
            final_df = pd.concat([final_df, setting_df])
    # same summary in csv
    final_df.to_csv(f'{args.save_prefix}/{args.csv_name}', index=False, header=True)
