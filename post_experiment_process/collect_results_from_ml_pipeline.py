import argparse
import pandas as pd
import numpy as np
import matplotlib.image
import os


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
args = parser.parse_args()

main_settings = ['lr128_tgt15', 'lr256_tgt45', 'lr256_tgt75', 'lr256_tgt105', 'lr512_tgt180', 'lr512_tgt420']
settings = {
        'main_exp_ours': main_settings,
        'main_exp_bicubic': main_settings,
        'main_exp_fomm': ['fomm'],
        'main_exp_vpx': [],
        'main_exp_SwinIR': main_settings, 
        'personalization': ['personalization', 'generic'],
        'model_ablation': ['fomm', 'fomm_skip_connections', 'fomm_skip_connections_lr_in_decoder', \
                'fomm_3_pathways_with_occlusion', 'sme_3_pathways_with_occlusion', 'pure_upsampling'],
        'encoder_in_training': ['lr128_tgt15', 'lr128_tgt45', 'lr128_tgt75', 'lr128_tgt_random', 'no_encoder'],
        'resolution_comparison': ['lr64_tgt45', 'lr128_tgt45', 'lr256_tgt45']
}
metrics_of_interest = ['psnr', 'ssim_db', 'orig_lpips']
        

def get_offset(setting, approach):
    """ return offset at which prediction is found based on setting """
    if approach in ['bicubic', 'SwinIR', 'vpx']:
        offset = 0
    elif 'personalization' in setting or 'generic' in setting:
        offset = 6
    elif 'pure_upsampling' in setting:
        offset = 2
    elif '3_pathways' in setting or 'lr_decoder' in setting:
        offset = 7
    elif setting in ['fomm', 'fomm_skip_connections']:
        offset = 6
    else: 
        # standard FOMM or with skip connections
        offset = 7
    print(f'returning at offset {offset} for {setting} in {approach}')
    return offset

def extract_prediction(person, frame_id, video_num, offset, folder, setting):
    """ retrieve the prediction from strip consisting of all intermediates """
    prefix = f'{video_num}.mp4_frame{frame_id}.npy'
    img = np.load(f'{folder}/visualization/{prefix}')
    prediction = img[:, offset*args.img_width: (offset + 1)*args.img_width, :]
    if offset == 0:
        prediction *= 255
        prediction = prediction.astype(np.uint8)
    matplotlib.image.imsave(f'{args.save_prefix}/full_prediction_{setting}.pdf', img)
    return prediction

def extract_src_tgt(person, frame_id, video_num, folder):
    """ retrieve the source and target from strip consisting of all intermediates """
    prefix = f'{video_num}.mp4_frame{frame_id}.npy'
    img = np.load(f'{folder}/visualization/{prefix}')
    src_offset = 1
    tgt_offset = 4
    src = img[:, src_offset*args.img_width: (src_offset + 1)*args.img_width, :]
    tgt = img[:, tgt_offset*args.img_width: (tgt_offset + 1)*args.img_width, :]
    return src, tgt

df_dict = {}
strip = []
final_img = None
os.makedirs(args.save_prefix, exist_ok=True)  

print(args.base_dir_list)
# aggregate results across all people for each setting for each approach
for (approach, base_dir) in zip(args.approaches_to_compare, args.base_dir_list):
    settings_to_compare = settings[approach]
    for person in args.person_list:
        row_in_strip = []
        for setting in settings_to_compare:
            if setting == "generic":
                folder = f'{base_dir}/{setting}/reconstruction_single_source_{person}'
                prefix = f'single_source_{person}'
            else:
                folder = f'{base_dir}/{setting}/{person}/reconstruction_single_source'
                prefix = f'single_source'

            print('folder', folder)
            metrics_file = f'{folder}/{prefix}_per_frame_metrics.txt'
            print(f'reading {metrics_file}')
            cur_frame = pd.read_csv(metrics_file)

            if setting not in df_dict:
                df_dict[setting] = cur_frame
            else:
                df_dict[setting] = pd.concat([df_dict[setting], cur_frame])

            # skip multiple settings for extracting strip for main exp
            if 'main_exp' in approach:
                if setting != 'lr256_tgt45' and 'fomm' not in approach:
                    continue

            prediction = extract_prediction(person, args.frame_num, args.video_num, \
                    get_offset(setting, approach), folder, setting)
            if 'main_exp' in approach or approach == "model_ablation":
                if 'ours' in setting or 'fomm_3_pathways' in setting:
                    (src, tgt) = extract_src_tgt(person, args.frame_num, args.video_num, folder)
                    row_in_strip = [src, tgt] + row_in_strip
            elif len(row_in_strip) == 0:
                (src, tgt) = extract_src_tgt(person, args.frame_num, args.video_num, folder)
                row_in_strip = [src, tgt]
            row_in_strip.append(prediction)
        
        if person in args.people_for_strip:
            completed_row = np.concatenate(row_in_strip, axis=1)
            strip.append(completed_row)
    if len(strip) > 0:
        final_img = np.concatenate(strip, axis=0)
        
    # compute average + stddev for each setting
    final_df = pd.DataFrame()
    for setting in settings_to_compare:
        average_df = pd.DataFrame(df_dict[setting].mean().to_dict(), \
                        index=[df_dict[setting].index.values[-1]])
        std_dev = df_dict[setting][metrics_of_interest].std()
        average_df['setting'] = setting
        average_df['approach'] = approach
        for m in metrics_of_interest:
            average_df[f'{m}_sd'] = std_dev[m]
        final_df = pd.concat([final_df, average_df])

# save all data
final_df.to_csv(f'{args.save_prefix}/{args.csv_name}', index=False, header=True)
if final_img is not None:
    matplotlib.image.imsave(f'{args.save_prefix}/strip.pdf', final_img)
