import argparse
import numpy as np
import matplotlib.image
import os

parser = argparse.ArgumentParser(description='Save single npy as pdf for eay viewing/testing')
parser.add_argument('--file-name', type=str,
                    help='pdf to save in', default='temp.pdf')
parser.add_argument('--base-path', type=str,
                    help='Path to results', default='/video-conf/scratch/vibhaa_mm_log_directory/personalization')
parser.add_argument('--frame-num', type=int,
                    help='Frame number ', default=1786)
parser.add_argument('--video-num', type=int,
                    help='Default video to use', default=5)
args = parser.parse_args()

""" retrieve the prediction from strip consisting of all intermediates """
suffix = f'{args.video_num}.mp4_frame{args.frame_num}.npy'
folder = f'{args.base_path}'
img_file = f'{folder}/visualization/{suffix}'
print(f'loading {img_file}')
img = np.load(img_file)
matplotlib.image.imsave(args.file_name, img)

