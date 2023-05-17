import numpy as np
import matplotlib.image
import os
from PIL import Image, ImageDraw, ImageFont

main_settings = ['lr128_tgt15Kb', 'lr256_tgt45Kb', 'lr256_tgt75Kb', 'lr256_tgt105Kb', 'lr512_tgt180Kb']
vp9_settings = ['lr256_tgt15Kb', 'lr256_tgt45Kb', 'lr512_tgt75Kb', 'lr512_tgt105Kb', 'lr512_tgt180Kb']
encoder_exp_settings = ['15Kb', '45Kb', '75Kb']
settings = {
        'main_exp:ours': main_settings,
        'main_exp:bicubic': main_settings,
        'main_exp:fomm': ['fomm'],
        'main_exp:vp9_bicubic': vp9_settings,
        'main_exp:vp9_ours': vp9_settings,
        'main_exp:vpx': ['tgt200Kb', 'tgt400Kb', 'tgt600Kb', 'tgt800Kb', 'tgt1000Kb'],
        'main_exp:vp9': ['lr1024_tgt100Kb', 'lr1024_tgt200Kb', 'lr1024_tgt300Kb', 'lr1024_tgt400Kb', 'lr1024_tgt500Kb', 'lr1024_tgt600Kb'],
        'main_exp:SwinIR': main_settings,
        'main_exp:SR': main_settings,
        'encoder_effect:tgt15Kb': encoder_exp_settings,
        'encoder_effect:tgt45Kb': encoder_exp_settings,
        'encoder_effect:tgt75Kb': encoder_exp_settings,
        'encoder_effect:tgt_random': encoder_exp_settings,
        'encoder_effect:no_encoder': encoder_exp_settings,
        'personalization': ['personalization', 'generic'],
        'netadapt_1024': ['depthwise_10', 'depthwise_1.5', 'normal_10', 'normal_1.5'],
        'model_ablation': ['pure_upsampling', 'fomm_3_pathways_with_occlusion'],
        'resolution_comparison': ['lr64_tgt45Kb', 'lr128_tgt45Kb', 'lr256_tgt45Kb'],
        'design_model_comparison': ['fomm', 'fomm_3_pathways_with_occlusion'],
        'dropout': ['dropout'], 
        'main_exp:no_dropout': ['no_dropout']
}
metrics_of_interest = ['psnr', 'ssim_db', 'orig_lpips']

def get_label(setting, approach):
    """ get label for an approach and setting """
    if 'vp9_bicubic' in approach:
        label = 'Bicubic (VP9)'
    elif 'bicubic' in approach:
        label = 'Bicubic (VP8)'
    elif 'SwinIR' in approach:
        label = 'SwinIR'
    elif 'vp9_ours' in approach:
        label = 'Gemino (VP9)'
    elif 'ours' in approach:
        label = 'Gemino (Ours)'
    elif 'vpx' in approach:
        label = 'VP8 (Chromium)'
    elif 'fomm' in approach:
        label = 'FOMM'
    elif 'no_dropout' in approach:
        label = 'No Dropout'
    elif 'dropout' in approach:
        label = 'Dropout'
    elif 'personalization' in setting:
        label = 'Personalized'
    elif 'generic' in setting:
        label = 'Generic'
    elif setting == 'pure_upsampling' or 'pure_upsampling' in approach or 'SR' in approach:
        label = 'Pure Upsampling'
    elif 'lr_in_decoder' in setting:
        label = 'Cond. SR w/ Warped HR'
    elif 'sme' in setting:
        label = 'Gemino w/ RGB Warp'
    elif '3_pathways' in setting:
        label = 'Gemino (Ours)'
    elif 'skip_connections' in setting:
        label = 'FOMM w/ Skip'
    else:
        label = setting
    return label


def make_label(labels, img_width):
    """ add a label row on top of figure """
    total_width = len(labels) * img_width
    height = 170 if img_width == 1024 else 90
    white_background = np.full((height, total_width, 3), 255, dtype=np.uint8)
    white_img = Image.fromarray(white_background, "RGB")
    white_img_draw = ImageDraw.Draw(white_img)
    font_size = round(0.8*height) if 'Pure Upsampling' not in labels else round(0.6*height)
    desired_font = ImageFont.truetype('times.ttf', font_size)
    for i, l in enumerate(labels):
        if len(l) < 8:
            x_loc = round((i + 0.4)* img_width - 0.6*len(l)) - 50
            if img_width != 512:
                x_loc -= 20
        elif len(l) < 16:
            if img_width == 512:
                x_loc = round((i + 0.2)* img_width - 0.5*len(l))
            else:
                x_loc = round((i + 0.25)* img_width - 0.8*len(l))
                x_loc -= 50
                if l == "Reference":
                    print("here")
                    x_loc += 40
        else:
            x_loc = round((i + 0.05)* img_width) + 60
        white_img_draw.text((x_loc, round(0.1*height)), l, fill=(0, 0, 0), font=desired_font)
    array = np.array(white_img)
    return array

def make_metrics_label(metrics, img_width):
    """ add a label row on top of figure """
    total_width = (len(metrics['PSNR (dB):']) + 1) * img_width
    height = 300
    white_background = np.full((height, total_width, 3), 255, dtype=np.uint8)
    white_img = Image.fromarray(white_background, "RGB")
    white_img_draw = ImageDraw.Draw(white_img)
    font_size = round(0.8*height/3)
    desired_font = ImageFont.truetype('times.ttf', font_size)
    for j, m in enumerate(metrics):
        print(j, m)
        x_loc = 300
        white_img_draw.text((x_loc, round(j*height/3)), m, fill=(0, 0, 0), font=desired_font)
        for i, l in enumerate(metrics[m]):
            label = "{:.2f}".format(l)
            x_loc = round((i + 1 + 0.4)* img_width - 0.6*len(label)) - 20
            x_loc = x_loc + 30 if len(label) == 4 else x_loc
            white_img_draw.text((x_loc, round(j*height/3)), label, fill=(0, 0, 0), font=desired_font)
    array = np.array(white_img)
    return array


def get_offset(setting, approach):
    """ return offset at which prediction is found based on setting """
    if approach in ['main_exp:bicubic', 'main_exp:vpx', 'main_exp:vp9_bicubic']:
        offset = 0
    elif 'netadapt' in approach:
        offset = 7
    elif 'personalization' in setting or 'generic' in setting:
        offset = 7
    elif 'pure_upsampling' in setting or 'pure_upsampling' in approach \
            or approach == 'main_exp:SwinIR' or approach == 'main_exp:SR':
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


def extract_at_offset(full_array, offset, img_width):
    """ check if offset is within range and return image """
    if (offset + 1) * img_width <= full_array.shape[1]:
        return full_array[:, offset*img_width: (offset + 1)*img_width, :]
    else:
        print(f'Offset {offset} invalid for {img_width} image of ' + \
                f'full size {full_array.shape[1]}')
    return None


def extract_prediction(person, frame_id, video_num, offset, folder, setting, approach, img_width, save_prefix):
    """ retrieve the prediction from strip consisting of all intermediates """
    file_ext = 'mp4' #'y4m' if 'vp9' in approach else 'mp4'
    prefix = f'{video_num}.{file_ext}_frame{frame_id}.npy'
    img = np.load(f'{folder}/visualization/{prefix}')
    prediction = extract_at_offset(img, offset, img_width)
    if prediction is None:
        return None

    if offset == 0:
        prediction *= 255
        prediction = prediction.astype(np.uint8)
    matplotlib.image.imsave(f'{save_prefix}/full_prediction_{setting}_{approach}.pdf', img)
    return prediction


def extract_src_tgt(person, frame_id, video_num, folder, img_width):
    """ retrieve the source and target from strip consisting of all intermediates """
    prefix = f'{video_num}.mp4_frame{frame_id}.npy'
    img = np.load(f'{folder}/visualization/{prefix}')
    src_offset = 1
    tgt_offset = 4
    src = extract_at_offset(img, src_offset, img_width)
    tgt = extract_at_offset(img, tgt_offset, img_width)
    return src, tgt


def get_folder_prefix(approach, setting, base_dir, person):
    """ return folder and file prefix based on setting/person """
    if setting == 'generic':
        folder = f'{base_dir}/{setting}/reconstruction_single_source_{person}'
        prefix = f'single_source_{person}'
    elif 'encoder_effect' in approach:
        model_type = f'lr128_{approach.split(":")[-1]}'
        folder = f'{base_dir}/{model_type}/{person}/reconstruction_single_source_{setting}'
        prefix = f'single_source_{setting}'
    elif 'dropout' in approach:
        folder = f'{base_dir}/reconstruction_single_source_{person}'
        prefix = f'single_source_{person}'
    else:
        folder = f'{base_dir}/{setting}/{person}/reconstruction_single_source'
        prefix = f'single_source'
    return folder, prefix
