import argparse
import numpy as np
import os
import imageio
import matplotlib
import matplotlib.pyplot as plt


CUTOFF = 20
FRAME_CHUNK_SIZE = 50
FRAME_SIZE = 1024


def get_frame_from_video(video_name, index, offset=0):
    """ get numpy array corresponding to frame at specific index 
        offset is responsible for indexing the right frame when
        there's a strip with reconstruction, source, target, etc.
    """
    reader = imageio.get_reader(video_name, "ffmpeg")
    reader.set_image_index(index)
    frame = np.array(reader.get_next_data())
    reader.close()
    return frame[:, offset*FRAME_SIZE:(offset + 1)*FRAME_SIZE, :]


parser = argparse.ArgumentParser(description='Find worst reconstructions')
parser.add_argument('--home-dir', metavar='h', type=str,
                    help='name of home directory to look for data in.')
parser.add_argument('--vpx-prefix', metavar='v', type=str,
                    help='prefix for vpx data')
parser.add_argument('--model-prefix', metavar='m', type=str,
                    help='prefix for model data')
args = parser.parse_args()

# read the vpx file first
frame_data = {}
vpx_filename = os.path.join(args.home_dir, f'reconstruction_{args.vpx_prefix}',
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
model_filename = os.path.join(args.home_dir, 
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
        diff[video_num].append((i, info['vpx'] - info['model']))
    diff[video_num].sort(key=lambda i: i[1], reverse=True)

# map it back to the appropriate frames and save them as pdfs
output_dir = os.path.join(args.home_dir, 'worst_frame_list')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for video_num in frame_data.keys():
    worst_frames = diff[video_num][:CUTOFF]
    total_frames = len(diff[video_num])
    print(worst_frames)

    gt_frames, vpx_frames, model_frames = [], [], []
    for (i, val) in worst_frames:
        video_index = min((i // FRAME_CHUNK_SIZE + 1) * FRAME_CHUNK_SIZE, 
                          total_frames)
        frame_index = i % FRAME_CHUNK_SIZE

        vpx_video_name = os.path.join(args.home_dir, 
                                      f'reconstruction_{args.vpx_prefix}',
                                      f'0_{video_num}.mp4_{video_index}_.mp4')
        vpx_frame = get_frame_from_video(vpx_video_name, frame_index, 2)
        vpx_frames.append(vpx_frame)
                                      
        model_video_name = os.path.join(args.home_dir, 
                                        f'reconstruction_{args.model_prefix}',
                                        f'0_{video_num}.mp4_{video_index}_.mp4')
        model_frame = get_frame_from_video(model_video_name, frame_index, 6)
        model_frames.append(model_frame)
        
        gt_filename = f'/video-conf/scratch/pantea/fom_personalized_1024/xiran/test/0_{video_num}.mp4'
        gt_frame = get_frame_from_video(gt_filename, i)
        gt_frames.append(gt_frame)

    vpx_strip = np.concatenate(vpx_frames, axis=1)
    model_strip = np.concatenate(model_frames, axis=1)
    gt_strip = np.concatenate(gt_frames, axis=1)
    final_strip = np.concatenate((gt_strip, vpx_strip, model_strip), axis=0)
    plt.imsave(f'{output_dir}/worst_frames_{video_num}.pdf', final_strip)

