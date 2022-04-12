from skimage.metrics import peak_signal_noise_ratio
from skimage.metrics import structural_similarity
import numpy as np
import subprocess as sh
import shlex
import time
import os
import signal
import datetime as dt
import torch
import getpass
import json
import piq
import glob
from skimage import img_as_float32
from first_order_model.modules.model import Vgg19

checkpoint_dict = {
        'generic': '/video-conf/scratch/pantea_experiments_tardy/generic_512_kp_at_256_with_hr_skip_connections\ 29_03_22_17.17.57/',
        'jen_psaki': '/video-conf/scratch/pantea_experiments_tardy/resolution512_with_hr_skip_connections/jen_psaki_resolution512_with_hr_skip_connections 08_04_22_20.34.56/00000069-checkpoint.pth.tar',
        'seth_meyer': '/video-conf/scratch/vibhaa_mm_log_directory/seth_meyers_512 05_04_22_19.07.24/00000069-checkpoint.pth.tar',
        'trever_noah': '/video-conf/scratch/pantea_experiments_tardy/resolution512_with_hr_skip_connections/trever_noah_resolution512_with_hr_skip_connections 08_04_22_16.14.52/00000069-checkpoint.pth.tar',
        'tucker': '/video-conf/scratch/pantea_experiments_tardy/resolution512_with_hr_skip_connections/tucker_resolution512_with_hr_skip_connections 08_04_22_18.02.06/00000069-checkpoint.pth.tar',
        'kayleigh': '/video-conf/scratch/pantea_experiments_tardy/resolution512_with_hr_skip_connections/kayleigh_resolution512_with_hr_skip_connections 05_04_22_18.23.53/00000069-checkpoint.pth.tar'
}

vgg_model = Vgg19()
if torch.cuda.is_available():
    vgg_model = vgg_model.cuda()

""" get per frame visual metrics based on predicted and original frame
"""
def get_quality(prediction, original):
    original = np.expand_dims(img_as_float32(original), 0)
    prediction = np.expand_dims(img_as_float32(prediction), 0)
    
    original = np.transpose(original, [0, 3, 1, 2])
    prediction = np.transpose(prediction, [0, 3, 1, 2])
    
    original_tensor = torch.from_numpy(original)
    prediction_tensor = torch.from_numpy(prediction)
    if torch.cuda.is_available():
        original_tensor = original_tensor.cuda()
        prediction_tensor = prediction_tensor.cuda()

    lpips_val = vgg_model.compute_loss(original_tensor, prediction_tensor).data.cpu().numpy().flatten()[0]
    ssim = piq.ssim(original_tensor, prediction_tensor, data_range=1.).data.cpu().numpy().flatten()[0]
    psnr = piq.psnr(original_tensor, prediction_tensor, data_range=1., \
            reduction='none').data.cpu().numpy().flatten()[0]

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
            if len(words) > 5: 
                continue
            frame_num = int(words[1])
            relevant_time = f'{words[3]} {words[4][:-1]}'
            relevant_time = relevant_time + '.0' if '.' not in relevant_time else relevant_time
            relevant_time = dt.datetime.strptime(relevant_time, "%Y-%m-%d %H:%M:%S.%f")
            sent_times[frame_num] = relevant_time


    # get receive time, latency, metrics
    recv_times_file = open(f'{save_dir}/recv_times.txt', 'r')
    for line in recv_times_file: 
        words = line.split(' ')
        frame_num = int(words[1])
        relevant_time = f'{words[3]} {words[4][:-1]}'
        relevant_time = relevant_time + '.0' if '.' not in relevant_time else relevant_time
        relevant_time = dt.datetime.strptime(relevant_time, "%Y-%m-%d %H:%M:%S.%f")
        
        sent_frame_file = f'{save_dir}/sender_frame_{frame_num:05d}.npy'
        recv_frame_file = f'{save_dir}/receiver_frame_{frame_num:05d}.npy'

        if not os.path.exists(sent_frame_file):
            print("Skipping frame", frame_num)
            continue
       
        try:
            sent_frame = np.load(sent_frame_file, allow_pickle=True)
            recvd_frame = np.load(recv_frame_file, allow_pickle=True)
        except IOError:
            print("Skipping frame", frame_num, "due to IO error")
            continue

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


""" pickle dump visual metrics and latency for all frames from the experiment
    and delete them
"""
def dump_per_frame_video_quality_latency(save_dir):
    metrics = {} 
    sent_times = {}
    special_frames_list = [1322, 574, 140, 1786, 1048, 839, 761, 2253, 637, 375]  

    # parse send times
    with open(f'{save_dir}/send_times.txt', 'r') as send_times_file:
        for line in send_times_file:
            words = line.split(' ')
            if len(words) > 5: 
                continue
            frame_num = int(words[1])
            relevant_time = f'{words[3]} {words[4][:-1]}'
            relevant_time = dt.datetime.strptime(relevant_time, "%Y-%m-%d %H:%M:%S.%f")
            sent_times[frame_num] = relevant_time


    # get receive time, latency, metrics
    recv_times_file = open(f'{save_dir}/recv_times.txt', 'r')
    highest_frame_so_far = -1
    for line in recv_times_file: 
        words = line.split(' ')
        frame_num = int(words[1])
        relevant_time = f'{words[3]} {words[4][:-1]}'
        relevant_time = dt.datetime.strptime(relevant_time, "%Y-%m-%d %H:%M:%S.%f")
        
        sent_frame_file = f'{save_dir}/sender_frame_{frame_num:05d}.npy'
        recv_frame_file = f'{save_dir}/receiver_frame_{frame_num:05d}.npy'

        if frame_num <= highest_frame_so_far:
            continue
        
        if frame_num > highest_frame_so_far + 100:
            continue

        if not os.path.exists(recv_frame_file) or not os.path.exists(sent_frame_file):
            print("Skipping frame", frame_num)
            if os.path.exists(recv_frame_file):
                os.remove(recv_frame_file)
            continue

        highest_frame_so_far = frame_num
        sent_frame = np.load(sent_frame_file, allow_pickle=True)
        recvd_frame = np.load(recv_frame_file, allow_pickle=True)

        if frame_num % 100 == 0:
            np.save(f'{save_dir}/metrics.npy', metrics)

        if frame_num % 500 == 0:
            print(f'dumped metrics for {frame_num} frames')
        
        qualities = get_quality(recvd_frame, sent_frame)
        latency = (relevant_time - sent_times[frame_num]).total_seconds() * 1000
        frame_metrics  = qualities.copy()
        frame_metrics.update({'latency': latency})
        metrics[frame_num] = frame_metrics
        
        del sent_times[frame_num]
        if frame_num not in special_frames_list:
            os.remove(sent_frame_file)
            os.remove(recv_frame_file)
     
    recv_times_file.close()
    
    # clean up any unremoved sent frames
    for frame_num in sent_times.keys():
        sent_frame_file = f'{save_dir}/sender_frame_{frame_num:05d}.npy'
        os.remove(sent_frame_file)
    os.system(f'rm {save_dir}/reference_frame*')

    for s in glob.glob(f'{save_dir}/sender*.npy'):
        frame_num = int(s.split("_")[-1].split(".")[0])
        if frame_num not in special_frames_list:
            sent_frame_file = f'{save_dir}/sender_frame_{frame_num:05d}.npy'
            os.remove(sent_frame_file)

    for s in glob.glob(f'{save_dir}/receiver*.npy'):
        frame_num = int(s.split("_")[-1].split(".")[0])
        if frame_num not in special_frames_list:
            recv_frame_file = f'{save_dir}/receiver_frame_{frame_num:05d}.npy'
            os.remove(recv_frame_file)

    np.save(f'{save_dir}/metrics.npy', metrics)


""" get throughput aggregated over windows of the experiment
"""
def get_throughput_over_windows(save_dir, window):
    windowed_received = []
    last_window_start = -1
    current_window_len = 0
    total_predicted_frames = 0

    old_end_of_prediction_time = 0
    first_prediction_time = 0
    last_prediction_time = 1

    with open(f'{save_dir}/receiver.log') as receiver_log:
        for line in receiver_log:
            words = line.strip()
            if "Prediction time for received keypoints" in words:
                total_predicted_frames += 1
                words_split = words.split()
                end_of_prediction_time = float(words_split[10])
                if first_prediction_time == 0:
                    first_prediction_time = end_of_prediction_time
                #print("time diff between predictions", (end_of_prediction_time - old_end_of_prediction_time) * 1000)
                old_end_of_prediction_time = end_of_prediction_time
                if end_of_prediction_time - last_window_start > window:
                    if current_window_len > 0:
                        windowed_received.append(current_window_len)
                    current_window_len = 1
                    last_window_start = end_of_prediction_time
                else:
                    current_window_len += 1
    
    last_prediction_time = end_of_prediction_time
    if current_window_len > 0:
        windowed_received.append(current_window_len)
    windowed_throughput = [i/window for i in windowed_received]
    print("total_predicted_frames", total_predicted_frames)
    print("total_throughput over the experiment", total_predicted_frames / (last_prediction_time - first_prediction_time))
    return  windowed_throughput


""" check if sender has gathered ice state 
"""
def check_sender_ready(filename):
    while True:
        result = sh.run(f'grep -i "iceGatheringState gathering -> complete" {filename}', shell=True)
        if result.returncode == 0:
            return
        time.sleep(5)


""" run a single experiment inside a mahimahi shell, 
    capturing logs using parameters passed in
"""
def run_single_experiment(params):
    total_runs = params['runs']
    save_dir = params['save_dir']
    duration = params['duration']
    fps = params['fps'] if 'fps' in params else 30
    uplink_trace = params['uplink_trace']
    downlink_trace = params['downlink_trace']
    video_file = params['video_file']
    exec_dir = params['executable_dir']
    dump_file = 'tcpdump.pcap'
    enable_prediction = params['enable_prediction']
    reference_update_freq = params.get('reference_update_freq', '0')
    quantizer = params.get('quantizer', 32)
    socket_path = params.get('socket_path', 'test.sock')
    user = getpass.getuser()

    for run_num in range(total_runs):
        print(f'Running {run_num}')
        params['run_num'] = run_num
        log_dir = f'{save_dir}/run{run_num}'
        os.makedirs(log_dir)
        
        # dump all parameters
        param_file = open(f'{log_dir}/params.json', "w")
        json.dump(params, param_file)
        param_file.close()

        # environment variable for number of bits if need be
        base_env = os.environ.copy()
        if 'jacobian_bits' in params:
            num_bits = params['jacobian_bits']
            base_env['JACOBIAN_BITS'] = str(num_bits)
        
        if 'checkpoint' in params:
            base_env['CHECKPOINT_PATH'] = params['checkpoint']
        if 'config_path' in params:
            base_env['CONFIG_PATH'] = params['config_path']
        
        # run sender inside mm-shell
        # mm_setup = 'sudo sysctl -w net.ipv4.ip_forward=1'
        # sh.run(mm_setup, shell=True)

        #mm_cmd = f'mm-link {uplink_trace} {downlink_trace}' 
        mm_cmd = f'./offer.sh {video_file} {fps} \
                {log_dir}/sender.log {log_dir} {exec_dir} \
                {enable_prediction} {reference_update_freq} {quantizer} {socket_path}'
        mm_args = shlex.split(mm_cmd)
        mm_proc = sh.Popen(mm_args, env=base_env)

        # get tcpdump
        check_sender_ready(f'{log_dir}/sender.log')
        """
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
        """

        # start receiver
        recv_output = open(f'{log_dir}/receiver.log', "w")
        receiver_cmd = f'python3 {exec_dir}/cli.py answer \
                        --record-to {log_dir}/received.mp4 \
                        --signaling-path {socket_path} \
                        --signaling unix-socket \
                        --fps {fps} \
                        --quantizer {quantizer} \
                        --reference-update-freq {reference_update_freq} \
                        --save-dir {log_dir}'
        if enable_prediction:
            receiver_cmd += ' --enable-prediction'
        receiver_cmd += ' --verbose' 
        receiver_args = shlex.split(receiver_cmd)
        recv_proc = sh.Popen(receiver_args, stderr=recv_output, env=base_env) 

        # wait for experiment and kill processes
        print("PIDS", recv_proc.pid, mm_proc.pid)
        time.sleep(duration)
        os.kill(recv_proc.pid, signal.SIGINT)
        time.sleep(5)
        
        os.kill(mm_proc.pid, signal.SIGTERM)
        os.system(f'pkill -9 tcpdump')
        os.system(f'pkill -U {user} -9 python3')
        recv_output.close()

        dump_per_frame_video_quality_latency(log_dir)
