""" Extracts the desired frame number from the videos and compares their PSNR
"""
import sys
sys.path.append('../')
import os
import numpy as np 
import cv2
import argparse
import pickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
from utils import get_quality

parser = argparse.ArgumentParser(description='Comparison tool to evaluate frames across different experiments')
parser.add_argument('--reference-video', metavar='r', type=str, required=True, 
                    help='path to ground truth.')
parser.add_argument('--comparison-list', metavar='cl', type=str, nargs='+', required=True,
                    help='list of files to extract frames from')
parser.add_argument('--frame-num', metavar='n', type=int, required=True, 
                    help='frame number to extract')
parser.add_argument('--img-width', metavar='n', type=int, default=512, 
                    help='width of frame')
parser.add_argument('--name-list', metavar='nl', type=str, nargs='+', required=True,
                    help='list of names for experiments')
parser.add_argument('--output-file', metavar='o', type=str, required=True, 
                    help='output file name')

args = parser.parse_args()
video_name = args.reference_video
img_width = args.img_width
name_list = ["Reference"] + args.name_list

""" get reference ground-truth frame
"""
images = []
cap = cv2.VideoCapture(video_name)
cap.set(1, args.frame_num - 1)
ret, img = cap.read()
if ret == False:
    print("Error with file", v)
    exit()
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
images.append(img)
cap.release()
cv2.destroyAllWindows()
metrics_list =[{'ssim': 1, 'psnr': float('inf'), 'lpips': 0}]

""" iterate through generated video list extracting prediction
"""
for v in args.comparison_list:
    cap = cv2.VideoCapture(v)
    cap.set(1, args.frame_num - 1)
    ret, img = cap.read()
    if ret == False:
        print("Error with file", v)
        continue
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    predicted_img = img[:, 5*img_width:6*img_width, :]
    images.append(predicted_img)
    metrics = get_quality(predicted_img, images[0])
    metrics_list.append(metrics)
    cap.release()
    cv2.destroyAllWindows()

""" combine into figure with title and metrics 
"""
fig = plt.figure(figsize=(20, 5.))
grid = ImageGrid(fig, 111,  # similar to subplot(111)
                 nrows_ncols=(1, len(name_list)),  # creates 1ximages grid of axes
                 axes_pad=1,  # pad between axes in inch.
                 )
for ax, im, name, metrics in zip(grid, images, name_list, metrics_list):
    ax.imshow(im, aspect='auto')
    metrics_str = ",".join([str(round(v, 2)) for v in metrics.values()])
    ax.set_title(name + "\n" + metrics_str)
fig.savefig(args.output_file)
