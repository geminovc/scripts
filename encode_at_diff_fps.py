import numpy
import argparse
import subprocess
import os
import numpy as np

parser = argparse.ArgumentParser(description='Reencodes videos at a whole bunch of fps to compress them')
parser.add_argument('--root-dir-name', metavar='n', type=str,
                    help='name of video directory to read data from.', default='/Users/vibhaa/Downloads/Videos/pantea_videos')
parser.add_argument('--frame-selection-frequency-list', metavar='fsfl', type=int, nargs='+',
                    help='list of intervals to select frames at', default=[10, 30, 60])
parser.add_argument('--speed-list', metavar='sl', type=int, nargs='+',
                    help='list of speeds to run realtime encoding at', default=[0, 2, 5, 8, 12, 15])
parser.add_argument('--deadline-list', type=str, nargs='+',
                    help='list of VP8 quality/deadline settings', default=['realtime', 'best', 'good'])
parser.add_argument('--csv-filename', type=str, 
                    help='name of csv to write to', default='fps_data')
parser.add_argument('--crf', type=int,
                    help='compression factor to use', default=35)

args = parser.parse_args()
root_dir = args.root_dir_name
frame_frequency_list = args.frame_selection_frequency_list
deadline_list = args.deadline_list
speed_list = args.speed_list
csv_filename = args.csv_filename
crf = args.crf

# take each video in the root directory, remove its audio
# and encode it at a series of different fps values
# also cleans up any intermediary files created
bitrates = {d: {n: {s: [] for s in speed_list} for n in frame_frequency_list} for d in deadline_list}
for video_name in os.listdir(root_dir):
    original_video_file = os.path.join(root_dir, video_name)
    video_file_without_audio = f'{video_name.split(".")[0]}_no_audio.mp4'
    ffmpeg_cmd = f'ffmpeg -i {original_video_file} -an {video_file_without_audio}'
    subprocess.run(ffmpeg_cmd, shell=True)

    for deadline in deadline_list:
        for n in frame_frequency_list:
            for speed in speed_list: 
                ffmpeg_cmd = f'ffmpeg -i {video_file_without_audio} -vf "select=not(mod(n\,{n}))"' + \
                        f' -vsync vfr -c:v libvpx -deadline {deadline} -speed {speed}' + \
                        f' every_{n}frames.webm'
                print(ffmpeg_cmd)
                subprocess.check_output(ffmpeg_cmd, shell=True)
                
                ffprobe_cmd = f'ffprobe -v quiet -print_format json -show_format' + \
                        f' -show_streams every_{n}frames.webm | grep "bit_rate"'
                bitrate_byte_obj = subprocess.check_output(ffprobe_cmd, shell=True)
                bitrate_val = float(str(bitrate_byte_obj).split(' ')[-1].split('"')[1])
                bitrate_kbps = bitrate_val / 1000.0
                bitrates[deadline][n][speed].append(bitrate_kbps)

                print(f'{video_name} {deadline} {n} {speed} {bitrate_kbps}')
                subprocess.run(f'rm every_{n}frames.webm', shell=True)

    subprocess.run(f'rm {video_file_without_audio}', shell=True)
    first = False


# postprocess averages
f = open(csv_filename, "w+")
f.write('deadline,frame_frequency,speed,bitrate\n')
for deadline in deadline_list:
    for n in frame_frequency_list:
        for s in speed_list:
            avg_bitrate = np.mean(bitrates[deadline][n][s])
            f.write(f'{deadline},{n},{s},{avg_bitrate}\n')
f.close()
