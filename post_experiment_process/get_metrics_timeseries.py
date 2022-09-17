import argparse
import sys
sys.path.append('../')
import log_parser
import numpy as np
from nets_utils import *
from process_utils import *
import csv
import imageio
from video_utils import *

parser = argparse.ArgumentParser(description='metrics logs info.')
parser.add_argument('--template-output', type=str,
                    help='duration to aggregate data (assumes ms)',
                    default=200)
parser.add_argument('--save-dir', type=str,
                    help='directory to save graph in', default='./metric_graphs')
parser.add_argument('--video-path-1', type=str,
                    help='path to the first video file', required=True)
parser.add_argument('--video-path-2', type=str,
                    help='path to the second video file', required=True)
args = parser.parse_args()


def get_windowed_metrics(metrics_dict, output_len, vid1_len):
    windowed_psnrs = []
    windowed_ssims = []
    windowed_lpips = []

    while len(metrics_dict) < vid1_len:
        metrics_dict.append({'psnr': 0, 'ssim': 0, 'lpips': 0, 'ssim_db': 0,
                        'orig_lpips': 0, 'face_lpips': 0, 'latency': 0})

    psnrs = [m['psnr'] for m in metrics_dict]
    ssims = [m['ssim'] for m in metrics_dict]
    if 'orig_lpips' in metrics_dict[0]:
        orig_lpips = [m['orig_lpips'] for m in metrics_dict]
    else:
        orig_lpips = [0 for i in psnrs]

    window_size = max(int(len(psnrs)/output_len), 1)
    while len(psnrs) < window_size * output_len:
        psnrs.append(0)
        ssims.append(0)
        orig_lpips.append(0)

    for i in range(output_len):
        windowed_psnrs.append(np.average(psnrs[i*window_size: (i+1) * window_size]))
        windowed_ssims.append(np.average(ssims[i*window_size: (i+1) * window_size]))
        windowed_lpips.append(np.average(orig_lpips[i*window_size: (i+1) * window_size]))
 
    return windowed_psnrs, windowed_ssims, windowed_lpips


def get_per_frame_metrics(video_path_1, video_path_2):
    video_frames1 = []
    metrics = []
    frame_count = 0
    loss_fn_vgg = get_loss_fn_vgg()

    reader1 = imageio.get_reader(video_path_1, "ffmpeg")
    reader2 = imageio.get_reader(video_path_2, "ffmpeg")

    for frame in reader1:
        video_frames1.append(frame)

    for frame2 in reader2:
        try:
            frame1 = video_frames1[frame_count]
            metric = visual_metrics(frame1, frame2, loss_fn_vgg)
            metrics.append(metric)
            frame_count += 1
            if frame_count % 100 == 0:
                print(frame_count)
        except Exception as e:
            print(e)
            pass

    return metrics, len(video_frames1)


if __name__ == "__main__":
    metrics_dict, vid1_len = get_per_frame_metrics(args.video_path_1, args.video_path_2)

    with open(args.template_output) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        output_len = -1
        for row in csv_reader:
            output_len += 1

    windowed_psnrs, windowed_ssims, windowed_lpips = get_windowed_metrics(metrics_dict, \
                                                        output_len, vid1_len)
    # dump timeseries
    timeseries_file = open(os.path.join(args.save_dir, \
                        f'visual_timeseries.csv'), 'wt')
    writer = csv.writer(timeseries_file)
    writer.writerow(['psnr', 'ssim', 'lpips'])
    for i in range(len(windowed_psnrs)):
        writer.writerow([windowed_psnrs[i], windowed_ssims[i], windowed_lpips[i]])

    timeseries_file.close()
