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
parser.add_argument('--window', type=int,
                    help='window to aggregate the results over (assumns ms)', default=1000)
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

    window_size = int(30 * args.window / 1000) #assumes a video with 30fps

    while len(psnrs) < window_size * output_len:
        psnrs.append(0)
        ssims.append(0)
        orig_lpips.append(0)

    for i in range(output_len):
        windowed_psnrs.append(np.average(psnrs[i*window_size: (i+1) * window_size]))
        windowed_ssims.append(np.average(ssims[i*window_size: (i+1) * window_size]))
        windowed_lpips.append(np.average(orig_lpips[i*window_size: (i+1) * window_size]))
 
    return windowed_psnrs[0:output_len], windowed_ssims[0:output_len], windowed_lpips[0:output_len], psnrs, ssims, orig_lpips


def get_num_frames(filename):
    cmd = f"ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -print_format csv {filename}"
    num_frames = os.popen(cmd).read()
    num_frames = int(num_frames.split(',')[1])
    return num_frames


def get_per_frame_metrics(video_path_1, video_path_2):
    video_frames1 = []
    metrics = []
    frame_count = 0
    loss_fn_vgg = get_loss_fn_vgg()

    num_frames_1 = get_num_frames(video_path_1)
    num_frames_2 = get_num_frames(video_path_2)
    reader1 = imageio.get_reader(video_path_1, "ffmpeg")
    reader1.set_image_index(0)
    reader2 = imageio.get_reader(video_path_2, "ffmpeg")
    reader2.set_image_index(0)
 
    for frame_index in range(min(num_frames_1, num_frames_2)):
        frame1 = reader1.get_next_data()
        frame2 = reader2.get_next_data()
        metric = visual_metrics(frame1, frame2, loss_fn_vgg)
        metrics.append(metric)
        if frame_index % 100 == 0:
            print(frame_index)
    return metrics, num_frames_1


if __name__ == "__main__":
    metrics_dict, vid1_len = get_per_frame_metrics(args.video_path_1, args.video_path_2)

    with open(args.template_output) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        output_len = -1
        for row in csv_reader:
            output_len += 1

    windowed_psnrs, windowed_ssims, windowed_lpips, psnrs, ssims, orig_lpips = get_windowed_metrics(metrics_dict, \
                                                        output_len, vid1_len)
    # dump per frame metrics
    timeseries_file = open(os.path.join(args.save_dir, \
            f'per_frame_visual_timeseries.csv'), 'wt')

    writer = csv.writer(timeseries_file)
    writer.writerow(['psnr', 'ssim', 'lpips'])
    for i in range(len(psnrs)):
        writer.writerow([psnrs[i], ssims[i], orig_lpips[i]])
    timeseries_file.close()

    # dump windowed timeseries
    timeseries_file = open(os.path.join(args.save_dir, \
                        f'windowed_visual_timeseries.csv'), 'wt')    
    writer = csv.writer(timeseries_file)
    writer.writerow(['psnr', 'ssim', 'lpips'])
    for i in range(len(windowed_psnrs)):
        writer.writerow([windowed_psnrs[i], windowed_ssims[i], windowed_lpips[i]])
    timeseries_file.close()

    plot_graph(range(0, len(windowed_psnrs)), [windowed_psnrs],\
          ['PSNR'], \
          ['r'], 'time (s)', f'psnr',\
          f'vidual quality comparison',\
          args.save_dir, f'windowed_psnr_using_encoder')

    plot_graph(range(0, len(windowed_ssims)), [windowed_ssims],\
          ['SSIM'], \
          ['r'], 'time (s)', f'ssim',\
          f'vidual quality comparison',\
          args.save_dir, f'windowed_ssim_using_encoder')

    plot_graph(range(0, len(windowed_lpips)), [windowed_lpips],\
          ['LPIPS'], \
          ['r'], 'time (s)', f'lpips',\
          f'vidual quality comparison',\
          args.save_dir, f'windowed_lpips_using_encoder')

