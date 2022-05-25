"""
Generates visual compariosn for a frame
across all methods at different reference frame 
frequencies and VPX compression levels
"""
import argparse
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Collect per frame stats.')
parser.add_argument('--person', type=str,
                    help='person who will be resized', default='xiran')
parser.add_argument('--save-prefix', type=str,
                    help='prefix to save logs and files in', 
                    required=True)
parser.add_argument('--destination-file', type=str,
                    help='file to save final strip in', 
                    default="data/strip.pdf")
parser.add_argument('--video-name', type=str,
                    help='video name', default="0_1.mp4")
parser.add_argument('--frame-num', type=int,
                    help='frame number', default=100)
parser.add_argument('--reference-frame-frequency-list', type=int, nargs='+',
                    help='interval between reference frame in frames',
                    default=[10, 60, 300, 900, 30000])
parser.add_argument('--vpx-quantizer-list', type=int, nargs='+',
                    help='set of quantizers to quantize at',
                    default=[2, 16, 32, 48, 63])
parser.add_argument('--setting-list', type=str, nargs='+',
                    help='personalized vs. generic', 
                    default=["personalized"])
parser.add_argument('--resolution', type=str,
                    help='resolution of the image',
                    default='512x512')

args = parser.parse_args()


def get_single_experiment_sample(save_dir, frame_num, frame_type='receiver'):
    """ aggregate single experiment data by reformating per frame metrics
        dict and dumping individual frames' qualities
    """
    frame = np.load(f'{save_dir}/{frame_type}_frame_{frame_num:05d}.npy', allow_pickle='TRUE')
    return frame


""" gets metrics from npy file 
    and puts it into csv for R
"""
def aggregate_data():
    first = True
    save_prefix = args.save_prefix
    setting_list = args.setting_list
    video_name = args.video_name
    person = args.person
    resolution = args.resolution
    frames = []
    first = True
    
    for setting in setting_list:
        if setting in ['personalized', 'generic']:
            for freq in args.reference_frame_frequency_list:
                print(f'Run {video_name} for person {person} reference frame freq {freq} setting {setting}')
                save_dir = f'{save_prefix}_{setting}/resolution{resolution}/' + \
                        f'{person}/reference_freq{freq}/' + \
                        f'{os.path.basename(video_name)}/run0'

                if first:
                    frame = get_single_experiment_sample(save_dir, args.frame_num, 'sender')
                    frames.append(frame)
                    first = False

                frame = get_single_experiment_sample(save_dir, args.frame_num)
                frames.append(frame)

        if setting == "vpx":
            for quantizer in args.vpx_quantizer_list:
                print(f'Run {video_name} for person {person} reference frame freq {freq} setting {setting}')
                save_dir = f'{save_prefix}_{width}_comparison_{setting}/{person}/' + \
                            f'resolution{resolution}/quantizer{quantizer}/' + \
                        f'{os.path.basename(video_name)}/run0'
                if first:
                    frame = get_single_experiment_sample(save_dir, args.frame_num, 'sender')
                    frames.append(frame)
                    first = False

                frame = get_single_experiment_sample(save_dir, args.frame_num)
                frames.append(frame)

    # put frames into numpy grid
    # save it
    combined_image = np.concatenate(frames, axis=1)
    plt.imshow(combined_image)
    plt.grid(False)
    plt.axis('off')
    plt.savefig(args.destination_file, bbox_inches='tight', pad_inches=0)

aggregate_data()
