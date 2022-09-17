import argparse
import pandas as pd
import numpy as np
import matplotlib.image
import os
from PIL import Image, ImageDraw, ImageFont

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
parser.add_argument('--summarize', action='store_true')
parser.add_argument('--cdf', action='store_true')
args = parser.parse_args()


main_settings = ['lr128_tgt15Kb', 'lr256_tgt45Kb', 'lr256_tgt75Kb', 'lr256_tgt105Kb', 'lr512_tgt180Kb', 'lr512_tgt420Kb']
encoder_exp_settings = ['15Kb', '45Kb', '75Kb']
settings = {
        'main_exp:ours': main_settings,
        'main_exp:bicubic': main_settings,
        'main_exp:fomm': ['fomm'],
        'main_exp:vpx': ['tgt1000Kb', 'tgt200Kb', 'tgt400Kb', 'tgt600Kb', 'tgt800Kb'],
        'main_exp:SwinIR': main_settings, 
        'encoder_effect:tgt15Kb': encoder_exp_settings,
        'encoder_effect:tgt45Kb': encoder_exp_settings,
        'encoder_effect:tgt75Kb': encoder_exp_settings,
        'encoder_effect:tgt_random': encoder_exp_settings,
        'encoder_effect:no_encoder': encoder_exp_settings,
        'personalization': ['personalization', 'generic'],
        'model_ablation': ['fomm', 'fomm_skip_connections', 'fomm_skip_connections_lr_in_decoder', \
                'fomm_3_pathways_with_occlusion', 'sme_3_pathways_with_occlusion', 'pure_upsampling'],
        'resolution_comparison': ['lr64_tgt45Kb', 'lr128_tgt45Kb', 'lr256_tgt45Kb'],
        'design_model_comparison': ['fomm', 'fomm_3_pathways_with_occlusion']
}
metrics_of_interest = ['psnr', 'ssim_db', 'orig_lpips']

def get_label(setting, approach):
    """ get label for an approach and setting """
    if 'bicubic' in approach:
        label = 'Bicubic'
    elif 'SwinIR' in approach:
        label = 'SwinIR'
    elif 'ours' in approach:
        label = 'Gemino'
    elif 'vpx' in approach:
        label = 'VP8 (Chromium)'
    elif setting == 'fomm':
        label = 'FOMM'
    elif 'personalization' in setting:
        label = 'Personalized'
    elif 'generic' in setting:
        label = 'Generic'
    elif setting == 'pure_upsampling':
        label = 'Pure Upsampling'
    elif 'lr_in_decoder' in setting:
        label = 'Cond. SR w/ Warped HR'
    elif 'sme' in setting:
        label = 'Gemino w/ RGB Warping'
    elif '3_pathways' in setting:
        label = 'Gemino'
    elif 'skip_connections' in setting:
        label = 'FOMM w/ Skip'
    else:
        label = setting
    return label


def make_label(labels):
    """ add a label row on top of figure """
    img_width = args.img_width
    total_width = len(labels) * img_width
    height = 170 if img_width == 1024 else 90
    white_background = np.full((height, total_width, 3), 255, dtype=np.uint8)
    white_img = Image.fromarray(white_background, "RGB")
    white_img_draw = ImageDraw.Draw(white_img)
    font_size = round(height / 2)
    desired_font = ImageFont.truetype('times.ttf', font_size)
    for i, l in enumerate(labels):
        if len(l) < 8:
            x_loc = round((i + 0.4)* img_width - 0.6*len(l))
        elif len(l) < 16:
            if img_width == 512:
                x_loc = round((i + 0.32)* img_width - 0.4*len(l))
            else:
                x_loc = round((i + 0.25)* img_width - 0.6*len(l))
        else:
            x_loc = round((i + 0.05)* img_width)
        white_img_draw.text((x_loc, round(0.43*height)), l, fill=(0, 0, 0), font=desired_font)
    array = np.array(white_img)
    return array


def get_offset(setting, approach):
    """ return offset at which prediction is found based on setting """
    if approach in ['main_exp:bicubic', 'main_exp:vpx']:
        offset = 0
    elif 'personalization' in setting or 'generic' in setting:
        offset = 7
    elif 'pure_upsampling' in setting or approach == 'main_exp:SwinIR':
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

def extract_prediction(person, frame_id, video_num, offset, folder, setting, approach):
    """ retrieve the prediction from strip consisting of all intermediates """
    prefix = f'{video_num}.mp4_frame{frame_id}.npy'
    img = np.load(f'{folder}/visualization/{prefix}')
    prediction = img[:, offset*args.img_width: (offset + 1)*args.img_width, :]
    if offset == 0:
        prediction *= 255
        prediction = prediction.astype(np.uint8)
    matplotlib.image.imsave(f'{args.save_prefix}/full_prediction_{setting}_{approach}.pdf', img)
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

final_df = pd.DataFrame()
strip = []
final_img = None
os.makedirs(args.save_prefix, exist_ok=True)

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
                if setting == "generic":
                    folder = f'{base_dir}/{setting}/reconstruction_single_source_{person}'
                    prefix = f'single_source_{person}'
                elif "encoder_effect" in approach:
                    model_type = f'lr128_{approach.split(":")[-1]}'
                    folder = f'{base_dir}/{model_type}/{person}/reconstruction_single_source_{setting}'
                    prefix = f'single_source_{setting}'
                else:
                    folder = f'{base_dir}/{setting}/{person}/reconstruction_single_source'
                    prefix = f'single_source'

                metrics_file = f'{folder}/{prefix}_per_frame_metrics.txt'
                print(f'reading {metrics_file}')
                cur_frame = pd.read_csv(metrics_file)

                if setting not in df_dict:
                    df_dict[setting] = cur_frame
                else:
                    df_dict[setting] = pd.concat([df_dict[setting], cur_frame])

                # skip multiple settings for extracting strip for main exp
                if 'main_exp' in approach or 'encoder_effect' in approach:
                    continue

                prediction = extract_prediction(person, args.frame_num, args.video_num, \
                        get_offset(setting, approach), folder, setting, approach)
                if approach == "model_ablation" or approach == 'design_model_comparison':
                    if 'ours' in setting or 'fomm_3_pathways' in setting:
                        (src, tgt) = extract_src_tgt(person, args.frame_num, args.video_num, folder)
                        row_in_strip = [src, tgt] + row_in_strip
                elif len(row_in_strip) == 0:
                    (src, tgt) = extract_src_tgt(person, args.frame_num, args.video_num, folder)
                    row_in_strip = [src, tgt]
                row_in_strip.append(prediction)
                if num == 1:
                    labels.append(get_label(setting, approach))
        
            if person in args.people_for_strip and len(row_in_strip) > 0:
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

                if 'main_exp' in approach:
                    setting = 'lr256_tgt45Kb' if 'fomm' not in approach else 'fomm'
                    folder = f'{base_dir}/{setting}/{person}/reconstruction_single_source'
                    prefix = f'single_source'
                else:
                    model_type = f'lr128_{approach.split(":")[-1]}'
                    setting = '45Kb'
                    folder = f'{base_dir}/{model_type}/{person}/reconstruction_single_source_{setting}'
                    prefix = f'single_source_{setting}'

                prediction = extract_prediction(person, args.frame_num, args.video_num, \
                        get_offset(setting, approach), folder, setting, approach)
                if approach == 'main_exp:ours':
                    (src, tgt) = extract_src_tgt(person, args.frame_num, args.video_num, folder)
                    row_in_strip = [src, tgt] + row_in_strip
                elif 'encoder' in approach and len(row_in_strip) == 0:
                    (src, tgt) = extract_src_tgt(person, args.frame_num, args.video_num, folder)
                    row_in_strip = [src, tgt]
                
                if num == 1:
                    labels.append(get_label(setting, approach))
                row_in_strip.append(prediction)
            
            if person in args.people_for_strip and len(row_in_strip) > 0:
                completed_row = np.concatenate(row_in_strip, axis=1)
                strip.append(completed_row)
        if len(strip) > 0:
            final_img = np.concatenate(strip, axis=0)
            
    # save img data
    if final_img is not None:
        label = make_label(labels)
        final_img = np.concatenate([label, final_img], axis=0)
        matplotlib.image.imsave(f'{args.save_prefix}/strip.pdf', final_img)


# aggregate results across all people for each setting for each approach
elif args.cdf:
    for (approach, base_dir) in zip(approaches_to_compare, base_dir_list):
        settings_to_compare = settings[approach]
        df_dict = {}
        for person in args.person_list:
            for setting in settings_to_compare:
                if setting == "generic":
                    folder = f'{base_dir}/{setting}/reconstruction_single_source_{person}'
                    prefix = f'single_source_{person}'
                elif "encoder_effect" in approach:
                    model_type = f'lr128_{approach.split(":")[-1]}'
                    folder = f'{base_dir}/{model_type}/{person}/reconstruction_single_source_{setting}'
                    prefix = f'single_source_{setting}'
                else:
                    folder = f'{base_dir}/{setting}/{person}/reconstruction_single_source'
                    prefix = f'single_source'

                metrics_file = f'{folder}/{prefix}_per_frame_metrics.txt'
                print(f'reading {metrics_file}')
                cur_frame = pd.read_csv(metrics_file)
                #avg_df = pd.DataFrame(cur_frame.mean().to_dict(), \
                #            index=[cur_frame.index.values[-1]])
                avg_df = cur_frame.groupby('video_num').mean().reset_index()
                avg_df['person'] = person
                """
                avg_df = pd.DataFrame(cur_frame.groupby('video_num').mean().to_dict(), \
                            index=[cur_frame.index.values[-1]])
                """
                
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

