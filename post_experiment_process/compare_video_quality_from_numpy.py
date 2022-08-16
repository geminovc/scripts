import argparse
import imageio
import torch
import os
import glob
from skimage import img_as_float32
from first_order_model.logger import Logger
from first_order_model.modules.model import Vgg19
from first_order_model.reconstruction import frame_to_tensor, get_avg_visual_metrics
import numpy as np 
import av

parser = argparse.ArgumentParser(description='Compare visual qualities.')
parser.add_argument('--save-dir', type=str,
                    help='directory to save cvs in', required=True)
parser.add_argument('--output-name', type=str,
                    help='file to save final data in',
                    default="visual_metrics.txt")
parser.add_argument('--numpy-prefix-1', type=str,
                    help='full path prefix to the first video data', required=True)
parser.add_argument('--numpy-prefix-2', type=str,
                    help='full path prefix to the second video data', required=True)
parser.add_argument('--make-video', action='store_true',
                    help='make the video from the numpy files')
parser.add_argument('--remove-npy', action='store_true',
                    help='remove the numpy files, only if the videos are saved')
args = parser.parse_args()

def visual_metrics(frame1, frame2, loss_fn_vgg):
    tensor1 = frame_to_tensor(img_as_float32(frame1), device)
    tensor2 = frame_to_tensor(img_as_float32(frame2), device)
    return Logger.get_visual_metrics(tensor1, tensor2, loss_fn_vgg)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
metrics_file = open(os.path.join(args.save_dir, args.output_name), 'wt')
vgg_model = Vgg19()
if torch.cuda.is_available():
    vgg_model = vgg_model.cuda()
loss_fn_vgg = vgg_model.compute_loss
video_frames1 = []
metrics = []
frame_count = 0
video_frames1 = {}
video_frames2 = {}

def get_frame_num_from_path(path):
    base_name = os.path.basename(path)
    return base_name.split('_')[-1].split('.')[0]
    
def get_video_frames(pattern, video_frames):
    for filename in glob.glob(pattern):
        frame_num = get_frame_num_from_path(filename)
        video_frames[frame_num] = np.load(filename, allow_pickle=True)
    return video_frames

def convert_numpy_list_to_video(frames_list, save_name, fps=30):
    container = av.open(save_name, mode="w")
    stream = container.add_stream("libx264", rate=fps)
    stream.width = frames_list[0].shape[1]
    stream.height = frames_list[0].shape[1]
    stream.pix_fmt = "yuv420p"

    for frame in frames_list:
        av_frame = av.VideoFrame.from_ndarray(frame, format="rgb24")
        for packet in stream.encode(av_frame):
            container.mux(packet)

    # Flush stream
    for packet in stream.encode():
        container.mux(packet)

    # Close the file
    container.close()
    print(f'Completed video {save_name}')

def get_sorted_video_array(video_frames):
    sorted_keys = sorted(video_frames.keys())
    return [video_frames[i] for i in sorted_keys]

video_frames1 = get_video_frames(f'{args.numpy_prefix_1}_*.npy', video_frames1)
video_frames2 = get_video_frames(f'{args.numpy_prefix_2}_*.npy', video_frames2)

for frame_num in video_frames2.keys():
    try:
        frame1 = video_frames1[frame_num]
        frame2 = video_frames2[frame_num]
        metrics.append(visual_metrics(frame1, frame2, loss_fn_vgg))
        frame_count += 1
        if frame_count % 100 == 0:
            print(frame_count)
    except Exception as e:
        print(e)
        pass

psnr, ssim, lpips_val, ssim_db = get_avg_visual_metrics(metrics)
print(f'PSNR: {psnr}, SSIM: {ssim}, SSIM_DB: {ssim_db}, LPIPS: {lpips_val} \n')
metrics_file.write(f'PSNR: {psnr}, SSIM: {ssim}, SSIM_DB: {ssim_db}, LPIPS: {lpips_val}')
metrics_file.flush()
metrics_file.close()

if args.make_video:
    convert_numpy_list_to_video(get_sorted_video_array(video_frames1),
            f'{args.numpy_prefix_1}.mp4', fps=30)
    convert_numpy_list_to_video(get_sorted_video_array(video_frames2),
            f'{args.numpy_prefix_2}.mp4', fps=30)
'''
if args.remove_numpy:
    if os.path.exists(path)
'''
