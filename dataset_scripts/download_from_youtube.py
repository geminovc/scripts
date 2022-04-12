import os
import argparse

parser = argparse.ArgumentParser(description='Download videos.')
parser.add_argument('--output_folder', type=str,
                    help='path to the folder to store the videos.')
parser.add_argument('--urls_path', type=str,
                    help='path to the urls file containing: url, start, stop')

args = parser.parse_args()

output_folder = args.output_folder
urls_path = args.urls_path
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

with open(urls_path) as f:
    lines = f.readlines()

quality = '\'bestvideo[ext=mp4]/bestvideo+bestaudio\''
old_url = None
video_id = 0
session_id = 0
for line in lines:
    try:
        line = line.strip('\n')
        url, start, stop = line.split(',')
        if old_url == url:
            session_id += 1
        else:
            old_url = url
            video_id += 1
            session_id = 0
        name = f'{session_id}_{video_id}'
        download_command = 'yt-dlp -i -f ' + str(quality) + ' --merge-output-format mp4 --external-downloader ffmpeg --external-downloader-args \"ffmpeg_i:-ss ' + \
        start + ' -to ' + stop + '\" ' + url + ' -P ' + output_folder + ' -o ' + '\"' + f'{name}.%(ext)s' + '\"'
        os.system(download_command)
    except Exception as e:
        print(e)
