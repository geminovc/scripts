import glob
import os

base_dir = '/video-conf/scratch/vibhaa_lam2/encoder_fixed_bitrate'
target_folder = '/video-conf/scratch/vibhaa_tardy/final_results/training_with_encoder'

for speaker in ['needle_drop', 'xiran', 'fancy_fueko', 'kayleigh']:
    for lr_size in [64, 128, 256, 512]:
        for bitrate in [15, 45, 75, 105, 180, 420]:
            for folder in glob.glob(f'{base_dir}/{speaker}1024_{lr_size}lr_tgt{bitrate}Kb*'):
                if os.path.exists(os.path.join(folder, '00000029-checkpoint.pth.tar')):
                    if not os.path.exists(f'{target_folder}/lr{lr_size}_tgt{bitrate}/{speaker}'):
                        print(f'copying {folder} to {target_folder}')
                        os.system(f'cp -r "{folder}" {target_folder}/lr{lr_size}_tgt{bitrate}/{speaker}')
