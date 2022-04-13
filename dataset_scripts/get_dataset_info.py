"""
This script records the following information for videos in --video_root:

    'number_of_videos','width','height', 
    'durations' (as a npy list),
    'frame_rate' (min, avg, max),
    'bit_rates'

Inputs
----------

video_root: root to the video directory..
csv_file_name: name of csv file to write results out to

Outputs
----------

The output is a csv file called csv_file_name that contains the coulmns: 

'num_videos','width','height', 'min_frame_rate','avg_frame_rate','max_frame_rate', 'min_bit_rate',
'avg_bit_rate', 'max_bit_rate', 'min_duration','avg_duration', 'max_duration'

Sample usage:

python get_videos_info.py --video_root '/path/to/videos' --results_dir /path/to/save/results --save_name tucker_train


"""

from __future__ import unicode_literals, print_function
import argparse
import ffmpeg
import sys
import glob
import os
import pathlib
import numpy as np

parser = argparse.ArgumentParser(description='Get video information')
parser.add_argument('--video_root',
                        type = str,
                        default = '/video-conf/vedantha/voxceleb2/dev/mp4',
                        help = 'root directory of the videos')
parser.add_argument('--save_name',
                       type = str,
                       required = True,
                       help = 'name to write results out to')
parser.add_argument('--save_dir',
                       type = str,
                       required = True,
                       help = 'directory to save results out to')

def get_video_info (in_filename):
    try:
        probe = ffmpeg.probe(in_filename)
    except Exception as e:
        print(e)

    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream is None:
        print('No video stream found', file=sys.stderr)
        width, height, num_frames, avg_frame_rate, bit_rate, duration = '0', '0', '0', '0', '0', '0'
    else:
        width = int(video_stream['width'])
        height = int(video_stream['height'])
        num_frames = int(video_stream['nb_frames'])
        bit_rate = int(video_stream['bit_rate'])
        duration = float(video_stream['duration'])
        avg_frame_rate = video_stream['avg_frame_rate']
        if '/' in avg_frame_rate:
            parts = avg_frame_rate.split('/')
            avg_frame_rate = float(parts[0])/float(parts[1])

    print('width: {} , height: {}, num_frames: {}, avg_frame_rate: {}, bit_rate: {}, duration: {} s'.format(width, height, num_frames,
                                                                                                     avg_frame_rate, bit_rate, duration))
    return width, height, num_frames, avg_frame_rate, bit_rate, duration

if __name__ == '__main__':
    args = parser.parse_args()
    video_paths = pathlib.Path(args.video_root).glob('*')
    save_dir = args.save_dir
    print("save_dir", save_dir)
    save_name = args.save_name
    os.makedirs(save_dir, exist_ok=True)
    count = 0
    durations = []
    bit_rates = []
    frame_rates = []
    num_frames = []
    widths = []
    heights = []

    for video_path in video_paths:
        try:
            width, height, num_frame, frame_rate, bit_rate, duration = get_video_info(video_path)
            durations.append(duration)
            bit_rates.append(bit_rate)
            frame_rates.append(frame_rate)
            num_frames.append(num_frame)
            widths.append(width)
            heights.append(height)
	    count += 1
        except Exception as e:
            print(e)

    # write to csv
    with open(f'{save_dir}/{save_name}_stats.csv', 'w') as f:
        f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"%('num_videos', 'width', 'height','min_num_frames',
        'avg_num_frames','max_num_frames', 'min_frame_rate','avg_frame_rate','max_frame_rate',
        'min_bit_rate','avg_bit_rate', 'max_bit_rate', 'min_duration','avg_duration', 'max_duration'))

        f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (count, np.average(widths), np.average(heights), min(num_frames), 
                    np.average(num_frames), max(num_frames), min(frame_rates), np.average(frame_rates), max(frame_rates),
                    min(bit_rates), np.average(bit_rates), max(bit_rates), min(durations), np.average(durations), max(durations)))


    np.save(f'{save_dir}/{save_name}_durations.npy', durations)
    np.save(f'{save_dir}/{save_name}_bit_rates.npy', bit_rates)


    
