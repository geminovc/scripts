import argparse
import numpy as np
import os
import imageio
import matplotlib
import matplotlib.pyplot as plt
import torch
import math
from skimage.metrics import structural_similarity as compare_ssim

CUTOFF = 20
FRAME_CHUNK_SIZE = 50
BATCH_SIZE=10
fig = plt.figure()


def get_frame_from_video(video_name, index, offset=0, frame_size=1024):
    """ get numpy array corresponding to frame at specific index 
        offset is responsible for indexing the right frame when
        there's a strip with reconstruction, source, target, etc.
    """
    reader = imageio.get_reader(video_name, "ffmpeg")
    reader.set_image_index(index)
    frame = np.array(reader.get_next_data())
    reader.close()
    return frame[:, offset*frame_size:(offset + 1)*frame_size, :]


def rgb(minimum, maximum, value):
    """ get rgb given the min/max and value to use for a heatmap
    """
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value-minimum) / (maximum - minimum)
    r = int(max(0, 255*(1 - ratio)))
    g = int(max(0, 255*(ratio - 1)))
    b = 0
    return np.array([r, g, b])

def get_heatmap_of_quality_diff(model_frame, vpx_frame, gt_frame):
    """ get a heatmap of patches where the difference between the model
        and the VPX frames' qualities is worst
    """
    video_size = model_frame.shape[0]
    rows, cols = 8, 8
    model_heatmap = np.zeros((video_size, video_size))
    vpx_heatmap = np.zeros((video_size, video_size))
    for i in range(0, rows):
        for j in range(0, cols):
            x_start = i*video_size // rows
            x_end = i*video_size // rows + video_size // rows
            y_start = j*video_size // cols
            y_end = j*video_size // cols + video_size // cols
            
            predicted_patch = model_frame[x_start:x_end, y_start:y_end]
            vpx_patch = vpx_frame[x_start:x_end, y_start:y_end]
            gt_patch = gt_frame[x_start:x_end, y_start:y_end]

            patch_ssim, _ = compare_ssim(predicted_patch, gt_patch, multichannel=True, full=True)
            model_heatmap[x_start:x_end, y_start:y_end] = patch_ssim
            
            patch_ssim, _ = compare_ssim(vpx_patch, gt_patch, multichannel=True, full=True)
            vpx_heatmap[x_start:x_end, y_start:y_end] = patch_ssim
    
    model_rgb_data = np.zeros((video_size, video_size, 3), dtype=np.uint8)
    vpx_rgb_data = np.zeros((video_size, video_size, 3), dtype=np.uint8)
    max_val = 1
    min_val = min(np.amin(model_heatmap), np.amin(vpx_heatmap))
    print(f'Min in data {np.amin(model_heatmap)}, {np.amin(vpx_heatmap)}. ' + \
            f'Max in data {np.amax(model_heatmap)}, {np.amax(vpx_heatmap)}')
    
    for i in range(0, video_size):
        for j in range(0, video_size):
            model_rgb_data[i][j] = rgb(min_val, max_val, model_heatmap[i][j])
            vpx_rgb_data[i][j] = rgb(min_val, max_val, vpx_heatmap[i][j])
    return model_rgb_data, vpx_rgb_data


def get_weighted_PSNR(gt_frame, cur_frame, seg):
    """ get PSNR by weighing the associated segmentation value """
    size = gt_frame.shape[0]
    nr, dr = 0, 0
    max_val = 256
    for i in range(size):
        for j in range(size):
            se = np.mean(np.square(gt_frame[i][j][:] - cur_frame[i][j][:]))
            nr += seg[i][j] * se
            dr += seg[i][j]

    psnr_val = 10 * math.log((max_val * max_val * dr)/nr, 10)
    return psnr_val


def get_frame_strip(diff, frame_type):
    """ obtain relevant frame numbers for worst or best and
        map back to the appropriate frames and save them as pdfs
    """
    frame_size = args.frame_size
    output_dir = os.path.join(args.model_dir, f'{frame_type}_frame_list')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for video_num in diff.keys():
        if frame_type == 'worst':
            worst_frames = diff[video_num][:CUTOFF]
        else:
            worst_frames = diff[video_num][-CUTOFF:]
        total_frames = len(diff[video_num])
        print(worst_frames)

        if total_frames == 0:
            continue

        gt_frames, vpx_frames, model_frames, reference_frames = [], [], [], []
        model_heatmaps, vpx_heatmaps, warped_frames = [], [], []
        for (i, val) in worst_frames:
            video_index = min((i // FRAME_CHUNK_SIZE + 1) * FRAME_CHUNK_SIZE, 
                              total_frames)
            frame_index = i % FRAME_CHUNK_SIZE

            vpx_video_name = os.path.join(args.vpx_dir, 
                                          f'reconstruction_{args.vpx_prefix}',
                                          f'0_{video_num}.mp4_{video_index}_.mp4')
            vpx_frame = get_frame_from_video(vpx_video_name, frame_index, 1, frame_size)
            vpx_frames.append(vpx_frame)
                                          
            model_video_name = os.path.join(args.model_dir, 
                                            f'reconstruction_{args.model_prefix}',
                                            f'0_{video_num}.mp4_{video_index}_.mp4')
            model_frame = get_frame_from_video(model_video_name, frame_index, 5, frame_size)
            model_frames.append(model_frame)

            reference_frame = get_frame_from_video(model_video_name, frame_index, 0, frame_size)
            reference_frames.append(reference_frame)
            
            warped_ref = get_frame_from_video(model_video_name, frame_index, 3, frame_size)
            warped_frames.append(warped_ref)
            
            gt_filename = f'{args.ground_truth_folder}/0_{video_num}.mp4'
            gt_frame = get_frame_from_video(gt_filename, i, 0, frame_size)
            gt_frames.append(gt_frame)

            model_heatmap, vpx_heatmap = get_heatmap_of_quality_diff(model_frame, vpx_frame, gt_frame)
            model_heatmaps.append(model_heatmap)
            vpx_heatmaps.append(vpx_heatmap)

            segs_dir = f'{args.segs_prefix}_{video_num}'
            seg_for_batch = torch.load(f'{segs_dir}/{i//BATCH_SIZE}.pt')
            seg_for_frame = seg_for_batch[0, i%BATCH_SIZE, 0, :, :].cpu().detach().numpy()
            psnr = get_weighted_PSNR(gt_frame, model_frame, seg_for_frame)

        vpx_strip = np.concatenate(vpx_frames, axis=1)
        model_strip = np.concatenate(model_frames, axis=1)
        gt_strip = np.concatenate(gt_frames, axis=1)
        ref_strip = np.concatenate(reference_frames, axis=1)
        warped_strip = np.concatenate(warped_frames, axis=1)
        model_heatmap_strip = np.concatenate(model_heatmaps, axis=1)
        vpx_heatmap_strip = np.concatenate(vpx_heatmaps, axis=1)
        final_strip = np.concatenate((gt_strip, vpx_strip, vpx_heatmap_strip, model_strip, \
                                     model_heatmap_strip, ref_strip, warped_strip), axis=0)
        plt.imsave(f'{output_dir}/{frame_type}_frames_{video_num}.pdf', final_strip)


parser = argparse.ArgumentParser(description='Find worst reconstructions')
parser.add_argument('--vpx-dir', metavar='vd', type=str,
                    help='name of home directory to look for vpx data in.')
parser.add_argument('--ground-truth-folder', metavar='gt', type=str,
                    help='test directory with original videos')
parser.add_argument('--frame-size', metavar='f', type=int, default=1024,
                    help='size of square frame')
parser.add_argument('--model-dir', metavar='md', type=str,
                    help='name of home directory to look for model data in.')
parser.add_argument('--vpx-prefix', metavar='v', type=str,
                    help='prefix for vpx data')
parser.add_argument('--model-prefix', metavar='m', type=str,
                    help='prefix for model data')
parser.add_argument('--segs-prefix', metavar='s', type=str,
                    help='prefix for segmentation data')
args = parser.parse_args()

# read the vpx file first
frame_data = {}
vpx_filename = os.path.join(args.vpx_dir, f'reconstruction_{args.vpx_prefix}',
                            f'{args.vpx_prefix}_per_frame_metrics.txt')
vpx_file = open(vpx_filename)
vpx_file.readline()
last_video_num = -1
while True:
    line = vpx_file.readline()
    if not line:
        break

    parts = line.split(",")
    video_num = int(parts[0])
    frame_num = int(parts[1])
    ssim = float(parts[3])

    if last_video_num != video_num:
        frame_data[video_num] = {}

    last_video_num = video_num
    frame_data[video_num][frame_num] = {'vpx': ssim}
vpx_file.close()

# read the model file next
model_filename = os.path.join(args.model_dir, 
                              f'reconstruction_{args.model_prefix}',
                              f'{args.model_prefix}_per_frame_metrics.txt')
model_file = open(model_filename)
model_file.readline()
while True:
    line = model_file.readline()
    if not line:
        break

    parts = line.split(",")
    video_num = int(parts[0])
    frame_num = int(parts[1])
    ssim = float(parts[3])
    frame_data[video_num][frame_num]['model'] = ssim
model_file.close()

# compute diffs and the worst frames
diff = {}
for video_num in frame_data.keys():
    diff[video_num] = []
    for (i, info) in frame_data[video_num].items():
        if 'model' not in info:
            print(i, video_num)
            break
        diff[video_num].append((i, info['vpx'] - info['model']))
    diff[video_num].sort(key=lambda i: i[1], reverse=True)

get_frame_strip(diff, 'worst')
get_frame_strip(diff, 'best')
