import argparse
import imageio
from video_utils import *

parser = argparse.ArgumentParser(description='Compare visual qualities.')
parser.add_argument('--save-dir', type=str,
                    help='directory to save cvs in', required=True)
parser.add_argument('--output-name', type=str,
                    help='file to save final data in',
                    default="visual_metrics.txt")
parser.add_argument('--video-path-1', type=str,
                    help='path to the first video file', required=True)
parser.add_argument('--video-path-2', type=str,
                    help='path to the second video file', required=True)
args = parser.parse_args()

video_frames1 = []
metrics = []
frame_count = 0
loss_fn_vgg = get_loss_fn_vgg()

reader1 = imageio.get_reader(args.video_path_1, "ffmpeg")
reader2 = imageio.get_reader(args.video_path_2, "ffmpeg")

for frame in reader1:
    video_frames1.append(frame)

for frame2 in reader2:
    try:
        frame1 = video_frames1[frame_count]
        metrics.append(visual_metrics(frame1, frame2, loss_fn_vgg))
        frame_count += 1
        if frame_count % 100 == 0:
            print(frame_count)
    except Exception as e:
        pass

save_average_metrics(metrics, args.save_dir, args.output_name)
