import pandas as pd
import time
import subprocess as sh
import argparse
import os
import signal
import shlex
import sys
import packet_parser
import numpy as np

EXAMPLE_DIR = "/home/vibhaa/aiortc/examples/videostream-cli"

parser = argparse.ArgumentParser(description='Frame Rate Variation.')
parser.add_argument('--fps-list', type=int, nargs='+',
                    help='list of frames per second', 
                    default=[1, 3, 5, 15, 30])
parser.add_argument('--uplink-trace', type=str,
                    help='uplink trace path for mahimahi', 
                    default="traces/12mbps_trace")
parser.add_argument('--downlink-trace', type=str,
                    help='downlink trace path for mahimahi', 
                    default="traces/12mbps_trace")
parser.add_argument('--duration', type=int,
                    help='duration of experiment (in seconds)', 
                    default=310)
parser.add_argument('--window', type=int,
                    help='duration to aggregate bitrate over (in seconds)', 
                    default=1)
parser.add_argument('--video-name', type=str,
                    help='name of video', 
                    default="sundar_pichai.mp4")
parser.add_argument('--csv-name', type=str,
                    help='file to save final data in', 
                    default="data/frame_rate_data")

args = parser.parse_args()

""" runs video conference at different frame rates
    capturing tcpdumps to measure bitrates from
"""
def run_experiments():
    for fps in args.fps_list:
        print('fps:', fps)
        sender_log = f'sender_noloss_{fps}fps.log'
        receiver_log = f'receiver_noloss_{fps}fps.log'
        dump_file = f'noloss_{fps}fps_dump.pcap'
        
        # run sender inside mm-shell
        mm_setup = 'sudo sysctl -w net.ipv4.ip_forward=1'
        sh.run(mm_setup, shell=True)

        mm_cmd = f'mm-link {args.uplink_trace} {args.downlink_trace} \
                ./offer.sh {EXAMPLE_DIR}/videos/{args.video_name} {fps} \
                {EXAMPLE_DIR}/logs/{sender_log}'
        mm_args = shlex.split(mm_cmd)
        mm_proc = sh.Popen(mm_args)

        # get tcpdump
        time.sleep(5)
        ifconfig_cmd = 'ifconfig | grep -oh "link-[0-9]*"'
        link_name = sh.check_output(ifconfig_cmd, shell=True)
        link_name = link_name.decode("utf-8")[:-1]
        print("Link Name:", link_name)

        rm_cmd = f'sudo rm {EXAMPLE_DIR}/tcpdumps/{dump_file}'
        sh.run(rm_cmd, shell=True)

        tcpdump_cmd = f'sudo tcpdump -i {link_name} \
                -w {EXAMPLE_DIR}/tcpdumps/{dump_file}'
        tcpdump_args = shlex.split(tcpdump_cmd)
        tcp_proc = sh.Popen(tcpdump_args)

        # start receiver
        recv_output = open(f'{EXAMPLE_DIR}/logs/{receiver_log}', "w")
        receiver_cmd = f'python3 {EXAMPLE_DIR}/cli.py answer \
                        --record-to {EXAMPLE_DIR}/videos/noloss_{fps}fps.mp4 \
                        --signaling-path /tmp/test.sock \
                        --signaling unix-socket \
                        --fps {fps} \
                        --verbose'
        receiver_args = shlex.split(receiver_cmd)
        recv_proc = sh.Popen(receiver_args, stderr = recv_output) 

        # wait for experiment and kill processes
        print("PIDS", recv_proc.pid, tcp_proc.pid, mm_proc.pid)
        time.sleep(args.duration)
        os.kill(recv_proc.pid, signal.SIGINT)
        time.sleep(5)
        
        os.kill(mm_proc.pid, signal.SIGTERM)
        os.system("sudo pkill -9 tcpdump")
        os.system("sudo pkill -9 python3")
        recv_output.close()


""" get fps from ffprobe 
"""
def get_fps_from_video(video_name):
    ffprobe_cmd = f'ffprobe -v error -select_streams v \
            -of default=noprint_wrappers=1:nokey=1 \
            -show_entries stream=avg_frame_rate {video_name}' 
    fps_string = sh.check_output(ffprobe_cmd, shell=True)
    print(fps_string)
    fps_string = fps_string.decode("utf-8")[:-1]
    print(fps_string)
    if "/" in fps_string:
        parts = fps_string.split("/")
        fps = round(int(parts[0]) / int(parts[1]), 2)
    else:
        fps = int(fps_string)
    print(fps_string, fps)
    return fps



""" gets bitrate info from pcap file 
    and puts it into csv for R
"""
def aggregate_data():
    first = True
    for fps in args.fps_list:
        dump_file = f'{EXAMPLE_DIR}/tcpdumps/noloss_{fps}fps_dump.pcap'
        saved_video_file = f'{EXAMPLE_DIR}/videos/noloss_{fps}fps.mp4'

        stats = packet_parser.gather_trace_statistics(dump_file, args.window)
        num_windows = len(stats['bitrates']['video'])
        streams = list(stats['bitrates'].keys())
        stats['bitrates']['time'] = np.arange(1, num_windows + 1)
        
        df = pd.DataFrame.from_dict(stats['bitrates'])
        for s in streams:
            df[s] = (df[s] / 1000.0 / args.window).round(2)
        df['fps'] = get_fps_from_video(saved_video_file)

        if first:
            df.to_csv(args.csv_name, header=True, index=False, mode="w")
            first = False
        else:
            df.to_csv(args.csv_name, header=False, index=False, mode="a+")

run_experiments()
aggregate_data()
