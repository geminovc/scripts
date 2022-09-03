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
from first_order_model.modules.model import Vgg19, VggFace16
from first_order_model.logger import Logger
from first_order_model.reconstruction import frame_to_tensor, get_video_duration
from first_order_model.frames_dataset import get_num_frames
import lpips
import log_parser
import pandas as pd
import subprocess

checkpoint_dict = {
        '512': {
        'generic': '/video-conf/scratch/pantea_experiments_tardy/generic_512_kp_at_256_with_hr_skip_connections 29_03_22_17.17.57/00000059-checkpoint.pth.tar',
        'jen_psaki': '/video-conf/scratch/pantea_experiments_tardy/resolution512_with_hr_skip_connections/jen_psaki_resolution512_with_hr_skip_connections 08_04_22_20.34.56/00000069-checkpoint.pth.tar',
        'seth_meyer': '/video-conf/scratch/vibhaa_mm_log_directory/seth_meyers_512 05_04_22_19.07.24/00000069-checkpoint.pth.tar',
        'trever_noah': '/video-conf/scratch/pantea_experiments_tardy/resolution512_with_hr_skip_connections/trever_noah_resolution512_with_hr_skip_connections 08_04_22_16.14.52/00000069-checkpoint.pth.tar',
        'tucker': '/video-conf/scratch/pantea_experiments_tardy/resolution512_with_hr_skip_connections/tucker_resolution512_with_hr_skip_connections 08_04_22_18.02.06/00000069-checkpoint.pth.tar',
        'kayleigh': '/video-conf/scratch/pantea_experiments_tardy/resolution512_with_hr_skip_connections/kayleigh_resolution512_with_hr_skip_connections 05_04_22_18.23.53/00000069-checkpoint.pth.tar'},
        
        '1024': {
            'needle_drop': '/video-conf/scratch/vibhaa_mm_arjun_directory/needle_drop_with_hr_skip_connections 11_04_22_16.54.29/00000069-checkpoint.pth.tar',
            'fancy_fueko': '/video-conf/scratch/pantea_experiments_tardy/resolution1024_with_hr_skip_connections/fancy_fueko_resolution1024_with_hr_skip_connections 10_04_22_01.06.51/00000069-cyheckpoint.pth.tar',
            'xiran': '/video-conf/scratch/pantea_experiments_tardy/resolution1024_with_hr_skip_connections/xiran_resolution1024_with_hr_skip_connections 08_04_22_13.43.30/00000069-checkpoint.pth.tar',
            'kayleigh': '/video-conf/scratch/vibhaa_mm_log_directory/kayleigh_resolution1024_with_hr_skip_connections 14_04_22_05.24.11/00000069-checkpoint.pth.tar', 
            }
}

vgg_model = Vgg19()
original_lpips = lpips.LPIPS(net='vgg')
vgg_face_model = VggFace16()

if torch.cuda.is_available():
    vgg_model = vgg_model.cuda()
    original_lpips = original_lpips.cuda()
    vgg_face_model = vgg_face_model.cuda()

loss_fn_vgg = vgg_model.compute_loss
face_lpips = vgg_face_model.compute_loss

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

""" get per frame visual metrics based on predicted and original frame
"""
def get_quality(prediction, original):
    tensor1 = frame_to_tensor(img_as_float32(prediction), device)
    tensor2 = frame_to_tensor(img_as_float32(original), device)
    return Logger.get_visual_metrics(tensor1, tensor2, loss_fn_vgg, original_lpips, face_lpips)


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

    if 'orig_lpips' in metrics_dict[0]:
        orig_lpips = [m['orig_lpips'] for m in metrics_dict]
        orig_lpip = np.average(orig_lpips)
    else:
        orig_lpip = 0

    if 'face_lpips' in metrics_dict[0]:
        face_lpips = [m['face_lpips'] for m in metrics_dict]
        face_lpip = np.average(face_lpips)
    else:
        face_lpip = 0

    if 'latency' in metrics_dict[0]:
        latencies = [m['latency'] for m in metrics_dict]
        latency = np.average(latencies)
    else:
        latency = 0

    return psnr, ssim, lpip, latency, orig_lpip, face_lpip


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
    averaged_metrics = {'psnr': [], 'ssim': [], 'lpips': [], 'old_lpips': [], 'latency': []}
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
    if len(window_metrics) > 0:
        averages = get_average_metrics(window_metrics)
        for i, k in enumerate(window_metrics[0].keys()):
            averaged_metrics[k].append(averages[i])
    return averaged_metrics   


""" pickle dump visual metrics and latency for all frames from the experiment
    and delete them
"""
def dump_per_frame_video_quality_latency(save_dir):
    metrics = {}
    lr_metrics = {}
    sent_times = {}
    special_frames_list = [1322, 574, 140, 1786, 1048, 839, 761, 2253, 637, 375, \
            1155, 2309, 1524, 1486, 1207, 315, 1952, 2111, 2148, 1530, \
            112, 939, 1211, 403, 2225, 1900, 207, 1634, 2006, 28]  

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
    highest_frame_so_far = -1
    for line in recv_times_file: 
        words = line.split(' ')
        frame_num = int(words[1])
        relevant_time = f'{words[3]} {words[4][:-1]}'
        relevant_time = relevant_time + '.0' if '.' not in relevant_time else relevant_time
        relevant_time = dt.datetime.strptime(relevant_time, "%Y-%m-%d %H:%M:%S.%f")
        
        sent_frame_file = f'{save_dir}/sender_frame_{frame_num:05d}.npy'
        recv_frame_file = f'{save_dir}/receiver_frame_{frame_num:05d}.npy'
        sent_lr_frame_file = f'{save_dir}/sender_lr_frame_{frame_num:05d}.npy'
        recv_lr_frame_file = f'{save_dir}/receiver_lr_frame_{frame_num:05d}.npy'

        if frame_num <= highest_frame_so_far:
            continue
        
        if frame_num > highest_frame_so_far + 100:
            continue
        #compute metrics for high-resolution sent and received frames
        if not os.path.exists(recv_frame_file) or not os.path.exists(sent_frame_file):
            print("Skipping frame", frame_num)
            if os.path.exists(recv_frame_file):
                os.remove(recv_frame_file)
            continue

        highest_frame_so_far = frame_num
        try:
            sent_frame = np.load(sent_frame_file)
        except:
            try:
                sent_frame = np.load(sent_frame_file, allow_pickle=True)
            except:
                continue
        try:
            recvd_frame = np.load(recv_frame_file)
        except:
            try:
                recvd_frame = np.load(recv_frame_file, allow_pickle=True)
            except:
                continue

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
            try:
                os.remove(sent_frame_file)
                os.remove(recv_frame_file)
            except:
                pass
     
        #compute metrics for low-resolution sent and received frames
        if not os.path.exists(recv_lr_frame_file) or not os.path.exists(sent_lr_frame_file):
            print("Skipping low-res frame", frame_num)
            if os.path.exists(recv_lr_frame_file):
                os.remove(recv_lr_frame_file)
            continue

        try:
            sent_lr_frame = np.load(sent_lr_frame_file)
        except:
            try:
                sent_lr_frame = np.load(sent_lr_frame_file, allow_pickle=True)
            except:
                continue
        try:
            recvd_lr_frame = np.load(recv_lr_frame_file)
        except:
            try:
                recvd_lr_frame = np.load(recv_lr_frame_file, allow_pickle=True)
            except:
                continue

        if frame_num % 100 == 0:
            np.save(f'{save_dir}/lr_metrics.npy', lr_metrics)

        if frame_num % 500 == 0:
            print(f'dumped metrics for {frame_num} low-res frames')

        lr_qualities = get_quality(recvd_lr_frame, sent_lr_frame)
        lr_frame_metrics  = lr_qualities.copy()
        lr_metrics[frame_num] = lr_frame_metrics

        if frame_num not in special_frames_list:
            try:
                os.remove(sent_lr_frame_file)
                os.remove(recv_lr_frame_file)
            except:
                pass

    recv_times_file.close()
    
    # clean up any unremoved sent frames

    for frame_num in sent_times.keys():
        try:
            sent_frame_file = f'{save_dir}/sender_frame_{frame_num:05d}.npy'
            os.remove(sent_frame_file)
        except:
            pass

        try:
            sent_lr_frame_file = f'{save_dir}/sender_lr_frame_{frame_num:05d}.npy'
            os.remove(sent_lr_frame_file)
        except:
            pass

    try:
        os.system(f'rm {save_dir}/reference_frame*')
    except:
        pass

    try:
        os.system(f'rm {save_dir}/predicted_frame*')
    except:
        pass

    try:
        for s in glob.glob(f'{save_dir}/sender_frame*.npy'):
            frame_num = int(s.split("_")[-1].split(".")[0])
            if frame_num not in special_frames_list:
                try:
                    sent_frame_file = f'{save_dir}/sender_frame_{frame_num:05d}.npy'
                    os.remove(sent_frame_file)
                except:
                    pass

                try:
                    sent_lr_frame_file = f'{save_dir}/sender_lr_frame_{frame_num:05d}.npy'
                    os.remove(sent_lr_frame_file)
                except:
                    pass
    except:
        pass

    try:
        for s in glob.glob(f'{save_dir}/receiver_frame*.npy'):
            frame_num = int(s.split("_")[-1].split(".")[0])
            if frame_num not in special_frames_list:
                try:
                    recv_frame_file = f'{save_dir}/receiver_frame_{frame_num:05d}.npy'
                    os.remove(recv_frame_file)
                except:
                    pass
                try:
                    recv_lr_frame_file = f'{save_dir}/receiver_lr_frame_{frame_num:05d}.npy'
                    os.remove(recv_lr_frame_file)
                except:
                    pass
    except:
        pass

    np.save(f'{save_dir}/metrics.npy', metrics)
    if len(lr_metrics.keys()) > 0:
        np.save(f'{save_dir}/lr_metrics.npy', lr_metrics)


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
            if "Prediction time for received" in words:
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


""" check if the video has been fully received
"""
def check_receiving_finished(video_file, receiver_log, max_duration):
    start_time = time.time()
    video_num_frames = get_num_frames(video_file)
    received_at_least_one = False

    while True:
        if time.time() - start_time > 120 and not received_at_least_one:
            print("Killing the experiment: nothing has been received after 2 minutes")
            return
        if time.time() - start_time > max_duration:
            return

        result = subprocess.check_output(f'grep -i "Frame displayed at receiver" {receiver_log} | tail -1 | cut -d" " -f 6 ' , shell=True)
        try:
            if int(result.decode("utf-8").strip()) == video_num_frames - 1:
                return
            received_at_least_one = True
        except Exception as e:
            print(e)
            pass
        time.sleep(10)


""" check the last frame_num in sent/recv times files
"""
def get_frame_num_in_endpoint(endpoint_times):
    result = subprocess.check_output(f'tail -n 1 {endpoint_times} | cut -d" " -f 2 ' , shell=True)
    try:
        frame_num = int(result.decode("utf-8").strip())
        return frame_num
    except Exception as e:
        print(e)
        return None


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
    prediction_type = params.get('prediction_type', 'keypoints')
    quantizer = params.get('quantizer', 32)
    lr_quantizer = params.get('lr_quantizer', 32)
    disable_mahimahi = params.get('disable_mahimahi', True)
    qsize_pkts = params.get('qsize_pkts', 160)
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
        if 'vpx_min_bitrate' in params:
            base_env['VPX_MIN_BITRATE'] = str(params['vpx_min_bitrate'])
        if 'vpx_default_bitrate' in params:
            base_env['VPX_DEFAULT_BITRATE'] = str(params['vpx_default_bitrate'])
        if 'vpx_default_bitrate' in params:
            base_env['VPX_MAX_BITRATE'] = str(params['vpx_max_bitrate'])

        # Start sender
        sender_output = open(f'{log_dir}/sender.log', "w")
        if not disable_mahimahi:
            # run sender inside mm-shell
            print("Using mahimahi shell")
            mm_setup = 'sudo sysctl -w net.ipv4.ip_forward=1'
            sh.run(mm_setup, shell=True)
            sender_cmd = f'mm-delay 25 mm-link {uplink_trace} {downlink_trace} \
                            --uplink-queue=droptail \
                            --downlink-queue=droptail \
                            --uplink-queue-args="packets={qsize_pkts}" \
                            --downlink-queue-args="packets={qsize_pkts}" \
                            --uplink-log="{log_dir}/mahimahi.log" \
                            ./offer.sh {video_file} {fps} {log_dir}/sender.log \
                            {log_dir} {exec_dir} {enable_prediction} {reference_update_freq} \
                            {quantizer} {socket_path} \
                            {lr_quantizer} {prediction_type}'
        else:
            sender_cmd =  f'python {exec_dir}/cli.py offer \
                             --play-from {video_file} \
                             --signaling-path {socket_path} \
                             --signaling unix-socket \
                             --fps {fps} \
                             --quantizer {quantizer} \
                             --lr-quantizer {lr_quantizer} \
                             --reference-update-freq {reference_update_freq} \
                             --save-dir {log_dir}'
            if enable_prediction:
                sender_cmd += ' --enable-prediction'
                sender_cmd += f' --prediction-type {prediction_type}'

            sender_cmd += ' --verbose' 

        sender_args = shlex.split(sender_cmd)
        sender_proc = sh.Popen(sender_args, stderr=sender_output, env=base_env)
 
        if not disable_mahimahi:
            try:
                # get tcpdump
                ifconfig_cmd = 'ifconfig | grep -oh "delay-[0-9]*"'
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
            except Exception as e:
                print("tcpdump error", e)
                pass

        check_sender_ready(f'{log_dir}/sender.log')

        # start receiver
        recv_output = open(f'{log_dir}/receiver.log', "w")
        receiver_cmd = f'python {exec_dir}/cli.py answer \
                        --record-to {log_dir}/received.mp4 \
                        --signaling-path {socket_path} \
                        --signaling unix-socket \
                        --fps {fps} \
                        --quantizer {quantizer} \
                        --lr-quantizer {lr_quantizer} \
                        --reference-update-freq {reference_update_freq} \
                        --save-dir {log_dir}'
        if enable_prediction:
            receiver_cmd += ' --enable-prediction'
            receiver_cmd += f' --prediction-type {prediction_type}'

        receiver_cmd += ' --verbose' 
        receiver_args = shlex.split(receiver_cmd)
        recv_proc = sh.Popen(receiver_args, stderr=recv_output, env=base_env) 

        # wait for experiment and kill processes
        print("PIDS", recv_proc.pid, sender_proc.pid)
        check_receiving_finished(video_file, f'{log_dir}/receiver.log', duration)
        #time.sleep(duration)
        os.kill(recv_proc.pid, signal.SIGINT)
        time.sleep(5)
        
        os.kill(sender_proc.pid, signal.SIGTERM)
        
        time.sleep(5)
        try:
            os.kill(recv_proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            print("couldn't find receive process")

        os.system(f'pkill -9 tcpdump')
        recv_output.close()
        sender_output.close()

        dump_per_frame_video_quality_latency(log_dir)

""" gather data for a single experiment
    over its multiple runs
"""
def gather_data_single_experiment(params):
    total_runs = params['runs']
    save_prefix = params['save_prefix']
    duration = params['duration']
    window = params['window']
    fps = params['fps'] if 'fps' in params else 30

    """ if use_video_length_for_bitrate is True, the experiment
        does not use the windowing and divides the total bits by
        the length of the received.mp4 video.
    """
    use_video_length_for_bitrate = True
    if 'use_video_length_for_bitrate' in params:
        use_video_length_for_bitrate = True

    combined_df = pd.DataFrame()
    for run_num in range(total_runs):
        save_dir = f'{save_prefix}/run{run_num}'
        dump_file = f'{save_dir}/sender.log'
        saved_video_file = f'{save_dir}/received.mp4'
        saved_video_duration = get_video_duration(saved_video_file)
        '''
        send_frame_num = get_frame_num_in_endpoint(f'{save_dir}/send_times.txt')
        recv_frame_num = get_frame_num_in_endpoint(f'{save_dir}/recv_times.txt')
        if recv_frame_num is not None and send_frame_num :
            if recv_frame_num >= send_frame_num - 10:
                use_video_length_for_bitrate = True
            else:
                use_video_length_for_bitrate = False
        '''
        stats = log_parser.gather_trace_statistics(dump_file, window / 1000)
        num_windows = len(stats['bits_sent']['video'])
        streams = list(stats['bits_sent'].keys())

        stats['bits_sent']['time'] = np.arange(1, num_windows + 1)
        window = stats['window']

        df = pd.DataFrame.from_dict(stats['bits_sent'])
        """" convert the bits_sent to bitrate
             if use_video_length_for_bitrate: divide total bits by received video length
             else: divide total bits in each window  by window size
        """
        for s in streams:
            if use_video_length_for_bitrate:
                df[s] = (df[s].sum(axis=0) / saved_video_duration / 1000)
            else:
                df[s] = (df[s] / float(window) / 1000)

        if use_video_length_for_bitrate:
            df['kbps'] = (df['video'] + df['lr_video'] + df['audio'] + df['keypoints'])
        else:
            df['kbps'] = df.iloc[:, 0:4].sum(axis=1)

        if 'resolution' in params:
            resolution = params['resolution']
            width, height = resolution.split("x")
            frame_size = float(width) * float(height)
            df['bpp'] = df['kbps'] * 1000 / fps /frame_size

        per_frame_metrics = np.load(f'{save_dir}/metrics.npy', allow_pickle='TRUE').item()
        if len(per_frame_metrics) == 0:
            print("PROBLEM!!!!")
            continue
        averages = get_average_metrics(list(per_frame_metrics.values()))
        metrics = {'psnr': [], 'ssim': [], 'lpips': [], 'latency': [], 'orig_lpips': [], 'face_lpips': []}
        for i, k in enumerate(metrics.keys()):
                metrics[k].append(averages[i])

        for m in metrics.keys():
            while len(metrics[m]) < df.shape[0]:
                metrics[m].append(metrics[m][0])
            df[m] = metrics[m]

        if os.path.exists(f'{save_dir}/lr_metrics.npy'):
            per_lr_frame_metrics = np.load(f'{save_dir}/lr_metrics.npy', allow_pickle='TRUE').item()
            if len(per_lr_frame_metrics) == 0:
                print("PROBLEM!!!!")
                continue
            averages = get_average_metrics(list(per_lr_frame_metrics.values()))
            metrics = {'lr_psnr': [], 'lr_ssim': [], 'lr_lpips': [], 'lr_orig_lpips': [], 'lr_face_lpips': []}
            for i, k in enumerate(metrics.keys()):
                    metrics[k].append(averages[i])

            for m in metrics.keys():
                while len(metrics[m]) < df.shape[0]:
                    metrics[m].append(metrics[m][0])
                df[m] = metrics[m]

        combined_df = pd.concat([df, combined_df], ignore_index=True)
        if os.path.isfile(f'{save_dir}/mahimahi.log'):
            sh.run(f'mm-graph {save_dir}/mahimahi.log {duration} --no-port \
                    --xrange \"0:{duration}\" --yrange \"0:3\" --y2range \"0:2000\" \
                    > {save_dir}/mahimahi.eps 2> {save_dir}/mmgraph.log', shell=True)

    return pd.DataFrame(combined_df.mean(axis=0).to_dict(), index=[combined_df.index.values[-1]])
