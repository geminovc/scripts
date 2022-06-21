""" Interactive tool that lets you draw bounding boxes on the predicted 
    image on the right and shows you which part of the source image it
    maps to

    Needs a video strip from the FOM model reconstruction to read frames
    and flows from
"""
import numpy as np 
import cv2
import argparse
import matplotlib.pyplot as plt
from matplotlib.widgets  import RectangleSelector
import signal
from skimage.metrics import structural_similarity as compare_ssim

parser = argparse.ArgumentParser(description='Interactive tool to visualize flows based on bounding boxes')
parser.add_argument('--name', metavar='n', type=str,
                    help='name of video strip to infer data from.')

args = parser.parse_args()
video_name = args.name
video_size = 1024

rows = cols = 8

""" iterate through video frames fetching grids and finding its source patch
"""
cap = cv2.VideoCapture(video_name)
count = 0
prev_rect = None
prev_patch = None
current = []
plt.rcParams["figure.figsize"] = [16, 9]
while cap.isOpened():
    ret, img = cap.read()
    if ret == False:
        break
    count += 1
    ssim_list = []
    predicted_patch_list, original_patch_list = [], []

    # extract the source, predicted and flow
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    source_img = img[:, :video_size, :]
    driving_img = img[:, video_size:2*video_size, :]
    deformed_img = img[:, 3*video_size:4*video_size, :]
    flow = img[:, 4*video_size:5*video_size, :]
    predicted_img = img[:, 5*video_size:6*video_size, :]
    
    # display source and predicted, register call back
    for i in range(0, rows):
        for j in range(0, cols):
            x_start = i*video_size // rows
            x_end = i*video_size // rows + video_size // rows
            y_start = j*video_size // cols
            y_end = j*video_size // cols + video_size // cols
            
            predicted_patch = predicted_img[x_start:x_end, y_start:y_end]
            original_patch = driving_img[x_start:x_end, y_start:y_end]

            patch_ssim, _ = compare_ssim(predicted_patch, original_patch, multichannel=True, full=True)

            ssim_list.append(patch_ssim)
            
            if patch_ssim < 0.4:
                predicted_patch_list.append(predicted_patch)
                original_patch_list.append(original_patch)
    
    print(np.mean(ssim_list))
    x = np.arange(0, rows * cols)
    plt.scatter(x, ssim_list)
    plt.xlabel("Patch #")
    plt.ylabel("SSIM")
    plt.title(f'Frame Number: {count}')
    plt.show()

    if len(predicted_patch_list) > 0:
        predicted_img = np.concatenate(predicted_patch_list, axis=1)
        original_img = np.concatenate(original_patch_list, axis=1)
        final_img = np.concatenate((predicted_img, original_img), axis=0)
        plt.imshow(final_img)
        plt.show()

cap.release()
cv2.destroyAllWindows()
