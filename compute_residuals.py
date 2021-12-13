""" Computes the residual sizes by compressing using JPEG2000

    Needs a video strip from the FOM model reconstruction to read frames
    and residuals from
"""
import os
import numpy as np
import cv2
import argparse
import glymur
import matplotlib.pyplot as plt
from utils import *
from imageio import imread
import glob

parser = argparse.ArgumentParser(description='Tool to understand residuals')
parser.add_argument('--name', metavar='n', type=str,
                    help='name of video strip to infer data from.')
parser.add_argument('--dir', metavar='d', type=str,
                    help='directory with frames.')
parser.add_argument('--save-directory', metavar='s', type=str,
                    help='folder where residuals are to be saved', default='residuals')
parser.add_argument('--compression-factor-list', metavar='c', type=int, nargs='+',
                    help='list of factors to compress by', required=True)
parser.add_argument('--save-frequency', metavar='sf', type=int,
                    help='interval between frames that are saved', default=10)

args = parser.parse_args()
video_name = args.name
compression_factor_list = args.compression_factor_list

count = 0
width = 256
sizes = {factor:[] for factor in compression_factor_list}

# iterate through video frames fetching residuals and compressing it
pre_residual_metrics = []
qualities = {f:[] for f in compression_factor_list}

file_list = glob.glob(os.path.join(args.dir, video_name + '*.png'))
for f in file_list:
    img = imread(f)
    count += 1

    source_img = img[:, :width, :]
    driving_img = img[:, 2*width:3*width, :]
    predicted_img = img[:, 5*width:6*width, :]
    residual = img[:, 6*width:7*width, :]
    
    pre_residual_metrics.append(get_quality(predicted_img, driving_img))

    # compress and find file size
    for factor in compression_factor_list:
        basename = f'residual_compression{factor}_frame{count}.jp2'
        filename = os.path.join(args.save_directory, basename)
        glymur.Jp2k(filename, residual, cratios=[factor])
        
        file_size = os.path.getsize(filename)
        sizes[factor].append(file_size)

        # uncompress and normalize residual
        reconstructed_residual = glymur.Jp2k(filename)[:]
        reconstructed_residual = reconstructed_residual.astype(int)
        blacks = 255 * np.ones_like(reconstructed_residual).astype(int)
        normalized_residual = reconstructed_residual * 2 - blacks
        
        # adjust prediction and clip incorrect values
        final_prediction = predicted_img + normalized_residual
        final_prediction[final_prediction > 255] = 255
        final_prediction[final_prediction < 0] = 0
        final_prediction = final_prediction.astype(np.uint8)
        
        metrics = get_quality(final_prediction, driving_img)
        qualities[factor].append(metrics)

        # cleanup
        if count % args.save_frequency != 0:
            rm_cmd = f'rm {filename}'
            os.system(rm_cmd)

# get final stats
psnr, ssim, lpips, _ = get_average_metrics(pre_residual_metrics)
print(f"Without residual: PSNR: {psnr}, SSIM: {ssim}, LPIPS: {lpips}")

for factor in compression_factor_list:
    bw = np.average(sizes[factor]) * 8 * 30/1000.0
    psnr, ssim, lpips, _ = get_average_metrics(qualities[factor])

    print(factor, "x")
    print(f"BW: {bw}kbps, PSNR: {psnr}, SSIM: {ssim}, LPIPS: {lpips}")
