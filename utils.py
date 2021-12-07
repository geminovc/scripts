from skimage.metrics import peak_signal_noise_ratio
from skimage.metrics import structural_similarity
import lpips
import numpy as np
import subprocess as sh
import shlex
import time
import os
import signal
import datetime as dt
import torch

loss_fn_vgg = lpips.LPIPS(net='vgg')
if torch.cuda.is_available():
    loss_fn_vgg = loss_fn_vgg.cuda()

""" get per frame visual metrics based on predicted and original frame 
"""
def get_quality(prediction, original):
    psnr = peak_signal_noise_ratio(original, prediction)
    ssim = structural_similarity(original, prediction, multichannel=True)

    if np.max(original) > 1 or np.max(prediction) > 1:
        original = original.astype(np.float32)
        prediction = prediction.astype(np.float32)
        original /= 255.0
        prediction /= 255.0

    original = np.transpose(original, [2, 0, 1])
    original_tensor = torch.unsqueeze(torch.from_numpy(original), 0)

    prediction = np.transpose(prediction, [2, 0, 1])
    prediction_tensor = torch.unsqueeze(torch.from_numpy(prediction), 0)

    if torch.cuda.is_available():
        original_tensor = original_tensor.cuda()
        prediction_tensor = prediction_tensor.cuda()
    lpips_val = loss_fn_vgg(original_tensor, prediction_tensor).data.cpu().numpy().flatten()[0]

    return {'psnr': psnr, 'ssim': ssim, 'lpips': lpips_val}


""" average out metrics across all frames as aggregated in
    the metrics_dict dictionary element
"""
def get_average_metrics(metrics_dict):
    psnrs = [m['psnr'] for m in metrics_dict]
    psnr = np.average(psnrs)

    ssims = [m['ssim'] for m in metrics_dict]
    ssim = np.average(ssims)

    lpips = [m['lpips'] for m in metrics_dict]
    lpip = np.average(lpips)

    if 'latency' in metrics_dict[0]:
        latencies = [m['latency'] for m in metrics_dict]
        latency = np.average(latencies)
    else:
        latency = 0

    return psnr, ssim, lpip, latency


""" get the fps of a video by running ffprobe
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


""" get video quality and latency metrics aggregated over
    windows of the experiment
"""
def get_video_quality_latency_over_windows(save_dir, window):
    window_metrics = [] 
    averaged_metrics = {'psnr': [], 'ssim': [], 'lpips': [], 'latency': []}
    sent_times = {}
    last_window_start = -1

    # parse send times
    with open(f'{save_dir}/send_times.txt', 'r') as send_times_file:
        for line in send_times_file:
            words = line.split(' ')
            frame_num = int(words[1])
            relevant_time = f'{words[3]} {words[4][:-1]}'
            relevant_time = dt.datetime.strptime(relevant_time, "%Y-%m-%d %H:%M:%S.%f")
            sent_times[frame_num] = relevant_time


    # get receive time, latency, metrics
    recv_times_file = open(f'{save_dir}/recv_times.txt', 'r')
    for line in recv_times_file: 
        words = line.split(' ')
        frame_num = int(words[1])
        relevant_time = f'{words[3]} {words[4][:-1]}'
        relevant_time = dt.datetime.strptime(relevant_time, "%Y-%m-%d %H:%M:%S.%f")
        
        sent_frame_file = f'{save_dir}/sender_frame_{frame_num:05d}.npy'
        recv_frame_file = f'{save_dir}/receiver_frame_{frame_num:05d}.npy'

        sent_frame = np.load(sent_frame_file)
        recvd_frame = np.load(recv_frame_file)

        qualities = get_quality(recvd_frame, sent_frame)
        latency = (relevant_time - sent_times[frame_num]).total_seconds() * 1000
        frame_metrics  = qualities.copy()
        frame_metrics.update({'latency': latency})
        window_metrics.append(frame_metrics)
        
        if last_window_start == -1:
            last_window_start = relevant_time

        if ((relevant_time - last_window_start).seconds > window):
            averages = get_average_metrics(window_metrics)
            for i, k in enumerate(window_metrics[0].keys()):
                averaged_metrics[k].append(averages[i])
            window_metrics = []
            last_window_start += dt.timedelta(0, window)

    recv_times_file.close()
    averages = get_average_metrics(window_metrics)
    for i, k in enumerate(window_metrics[0].keys()):
        averaged_metrics[k].append(averages[i])
    return averaged_metrics


""" run a single experiment inside a mahimahi shell, 
    capturing logs using parameters passed in
"""
def run_single_experiment(params):
    log_dir = params['save_dir']
    duration = params['duration']
    fps = params['fps']
    uplink_trace = params['uplink_trace']
    downlink_trace = params['downlink_trace']
    video_file = params['video_file']
    exec_dir = params['executable_dir']
    dump_file = 'tcpdump.pcap'
    
    # run sender inside mm-shell
    mm_setup = 'sudo sysctl -w net.ipv4.ip_forward=1'
    sh.run(mm_setup, shell=True)

    mm_cmd = f'mm-link {uplink_trace} {downlink_trace} \
            ./offer.sh {video_file} {fps} \
            {log_dir}/sender.log {log_dir} {exec_dir}'
    mm_args = shlex.split(mm_cmd)
    mm_proc = sh.Popen(mm_args)

    # get tcpdump
    time.sleep(5)
    ifconfig_cmd = 'ifconfig | grep -oh "link-[0-9]*"'
    link_name = sh.check_output(ifconfig_cmd, shell=True)
    link_name = link_name.decode("utf-8")[:-1]
    print("Link Name:", link_name)

    rm_cmd = f'sudo rm {log_dir}/{dump_file}'
    sh.run(rm_cmd, shell=True)

    tcpdump_cmd = f'sudo tcpdump -i {link_name} \
            -w {log_dir}/{dump_file}'
    print(tcpdump_cmd)
    tcpdump_args = shlex.split(tcpdump_cmd)
    tcp_proc = sh.Popen(tcpdump_args)

    # start receiver
    recv_output = open(f'{log_dir}/receiver.log', "w")
    receiver_cmd = f'python3 {exec_dir}/cli.py answer \
                    --record-to {log_dir}/received.mp4 \
                    --signaling-path /tmp/test.sock \
                    --signaling unix-socket \
                    --fps {fps} \
                    --save-dir {log_dir} \
                    --verbose'
    receiver_args = shlex.split(receiver_cmd)
    recv_proc = sh.Popen(receiver_args, stderr = recv_output) 

    # wait for experiment and kill processes
    print("PIDS", recv_proc.pid, tcp_proc.pid, mm_proc.pid)
    time.sleep(duration)
    os.kill(recv_proc.pid, signal.SIGINT)
    time.sleep(5)
    
    os.kill(mm_proc.pid, signal.SIGTERM)
    os.system("sudo pkill -9 tcpdump")
    os.system("sudo pkill -9 python3")
    recv_output.close()

