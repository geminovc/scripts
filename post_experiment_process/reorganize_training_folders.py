import glob
import os

fixed_bitrate_exps = False
model_comparisons = False
encoder_effect = True
base_dir = '/video-conf/scratch/vibhaa_lam1/encoder_fixed_bitrate'
target_folder = '/video-conf/scratch/vibhaa_lam2/final_results/encoder_effect'
model_types = ['fomm', 'fomm_skip_connections', 'fomm_skip_connections_lr_in_decoder', \
        'fomm_3_pathways_with_occlusion', 'sme_3_pathways_with_occlusion', 'pure_upsampling']

for speaker in ['adam_neely', 'needle_drop', 'xiran', 'fancy_fueko', 'kayleigh']:
    if fixed_bitrate_exps:
        for lr_size in [64, 128, 256, 512]:
            for bitrate in [15, 45, 75, 105, 180, 420]:
                for folder in glob.glob(f'{base_dir}/{speaker}1024_{lr_size}lr_tgt{bitrate}Kb*'):
                    if os.path.exists(os.path.join(folder, '00000029-checkpoint.pth.tar')):
                        if not os.path.exists(f'{target_folder}/lr{lr_size}_tgt{bitrate}/{speaker}'):
                            print(f'copying {folder} to {target_folder}')
                            os.system(f'cp -r "{folder}" {target_folder}/lr{lr_size}_tgt{bitrate}/{speaker}')

    if model_comparisons:
        for model_type in model_types:
            cpk_num = '129' if model_type == 'fomm' else '029'
            for folder in glob.glob(f'{base_dir}/{speaker}1024_{model_type} *'):
                if os.path.exists(os.path.join(folder, f'00000{cpk_num}-checkpoint.pth.tar')):
                    if not os.path.exists(f'{target_folder}/{model_type}/{speaker}'):
                        print(f'copying {folder} to {target_folder}/{model_type}/{speaker}')
                        os.system(f'cp -r "{folder}" {target_folder}/{model_type}/{speaker}')

    if encoder_effect:
        lr_size = 128
        for bitrate in ['15Kb', '45Kb', '75Kb', '_random']:
            for folder in glob.glob(f'{base_dir}/{speaker}1024_{lr_size}lr_tgt{bitrate} *'):
                if os.path.exists(os.path.join(folder, f'00000029-checkpoint.pth.tar')):
                    if not os.path.exists(f'{target_folder}/{lr_size}_tgt{bitrate}/{speaker}'):
                        print(f'copying {folder} to {target_folder}')
                        os.system(f'cp -r "{folder}" {target_folder}/lr{lr_size}_tgt{bitrate[:-2]}/{speaker}')
