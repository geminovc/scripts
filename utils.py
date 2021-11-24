from skimage.metrics import peak_signal_noise_ratio
from skimage.metrics import structural_similarity
import lpips
import numpy as np
import subprocess as sh
import shlex
import time
import os
import signal

""" get per frame visual metrics based on predicted and original frame 
"""
def get_quality(prediction, original):
    psnr = peak_signal_noise_ratio(original, prediction)
    ssim = structural_similarity(original, prediction, multichannel=True)

    # TODO: tensorify/send to CUDA
    lpips = 0 #loss_fn_vgg(original, prediction)

    return {'psnr': psnr, 'ssim': ssim, 'lpips': lpips}


""" average out visual metrics across all frames as aggregated in
    the metrics_dict dictionary element
"""
def get_average_visual_metrics(metrics_dict):
    psnrs = [m['psnr'] for m in metrics_dict]
    psnr = np.average(psnrs)

    ssims = [m['ssim'] for m in metrics_dict]
    ssim = np.average(ssims)

    lpips = [m['lpips'] for m in metrics_dict]
    lpip = np.average(lpips)

    return psnr, ssim, lpip


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

