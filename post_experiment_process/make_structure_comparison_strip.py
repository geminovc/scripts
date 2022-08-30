import sys
sys.path.append('../')
from first_order_model.fom_wrapper import FirstOrderModel
import imageio 
import numpy as np
import time
import os
import pandas as pd
from argparse import ArgumentParser
from checkpoints import *
from nets_utils import *
import imageio

def get_num_frames(filename):
    cmd = f"ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -print_format csv {filename}"
    num_frames = os.popen(cmd).read()
    num_frames = int(num_frames.split(',')[1])
    return num_frames

def get_frame(filename, frame_num, ifnormalize=True):
    reader = imageio.get_reader(filename, "ffmpeg")
    reader.set_image_index(frame_num)
    frame = np.array(reader.get_next_data())
    if ifnormalize:
        frame = img_as_float32(frame)
    reader.close()
    return frame

parser = ArgumentParser()
parser.add_argument("--root_dir",
                    default="/video-conf/scratch/pantea",
                    help="path to the test video")
parser.add_argument("--generate_video",
                    action='store_true',
                    help="generate a video strip instead of an image strip")
parser.add_argument("--compute_metrics",
                    action='store_true',
                    help="compute the per-frame metrics if set")
parser.add_argument("--source_frame_num",
                    default=0,
                    type=int,
                    help="index of the source frame")
parser.add_argument("--target_frame_num",
                    default=10,
                    type=int,
                    help="index of the target frame")
parser.add_argument("--max_frame_num",
                    default=1800,
                    type=int,
                    help="maximum frame number if generating video")
parser.add_argument("--save_prefix",
                    default="model_structure_comparison",
                    help="name of the output file to be saved")
parser.add_argument("--output_fps",
                    default=30,
                    help="fps of the final video if generate_video is set")
parser.add_argument("--source_update_frequency",
                    default=8000,
                    help="source update frequency if generate_video is set")
parser.add_argument('--resolution', type=str,
                    help='video resolution',
                    default="512")
parser.add_argument("--person",
                    default="xiran_close_up",
                    help="name of the person")

parser.set_defaults(verbose=False)
opt = parser.parse_args()
person = opt.person

settings = [f"resolution{opt.resolution}_fom_standard", f"resolution{opt.resolution}_only_upsample_blocks",
            f"resolution{opt.resolution}_without_hr_skip_connections", f"resolution{opt.resolution}_with_hr_skip_connections"]

checkpoint_list = [structure_based_checkpoint_dict[setting][person] for setting in settings]
config_list = [f'paper_configs/{setting}.yaml' for setting in settings]

video_dir = os.path.join(opt.root_dir, f"fom_personalized_{opt.resolution}" ,person, "test")
try:
    num_videos = 0
    for base_video_name in os.listdir(video_dir):
        video_name =  os.path.join(video_dir, base_video_name)
        print("video name ", video_name)
        save_dir = f'{opt.save_prefix}/{opt.resolution}/{person}/{os.path.basename(video_name)}'
        print("save_dir", save_dir)
        
        if_predict = True 
        if opt.generate_video:
            save_suffix = f'max_frame_num{opt.max_frame_num}_freq{opt.source_update_frequency}'
            if os.path.exists(f'{save_dir}/{save_suffix}.mp4'):
                print(f'{save_dir}/{save_suffix}.mp4 exists!')
                if_predict = False
        else:
            save_suffix = f'src{opt.source_frame_num}_target{opt.target_frame_num}'
            if os.path.exists(f'{save_dir}/{save_suffix}.png'):
                print(f'{save_dir}/{save_suffix}.png exists!')
                if_predict = False
        
        if if_predict:
            os.makedirs(save_dir, exist_ok=True)
            source = get_frame(video_name, opt.source_frame_num, ifnormalize=False)
            predictions = []
            video_array = []
            cross_setting_metrics = {}
            
            # Add original video frames/source-target pair to the strip
            if opt.generate_video:
                reader = imageio.get_reader(video_name, "ffmpeg")
                num_frames = 0
                for frame in reader:
                    video_array.append(frame)
                    num_frames += 1
                    print(f'Reading video frame num {num_frames}')
                    if num_frames == opt.max_frame_num:
                        break
                predictions.append(video_array)
            else:
                predictions.append(np.expand_dims(source, axis=0))
                driving = get_frame(video_name, opt.target_frame_num, ifnormalize=False)
                predictions.append(np.expand_dims(driving, axis=0))
            
            for config, checkpoint in zip(config_list, checkpoint_list):
                if checkpoint != '':
                    setting = settings[config_list.index(config)]
                    print(setting)
                    model = FirstOrderModel(config, checkpoint)
               
                    source_kp, _= model.extract_keypoints(source)
                    model.update_source(0, source, source_kp)
                    prediction = []
                    per_frame_metrics = []

                    if opt.generate_video:
                        for i in range(0, min(len(video_array), opt.max_frame_num)):
                            print(i)
                            if i % opt.source_update_frequency == 0:
                                source = video_array[i]
                                source_kp, _= model.extract_keypoints(source)
                                model.update_source(len(model.source_frames), source, source_kp) 
                            
                            driving = video_array[i]
                            target_kp, source_index = model.extract_keypoints(driving)
                            target_kp['source_index'] = source_index
                            start = time.perf_counter()
                            predicted_driving = model.predict(target_kp)
                            prediction_time = 1000 * (time.perf_counter() - start)
                            prediction.append(predicted_driving)
                            metrics = get_quality(predicted_driving, driving)
                            metrics['latency'] = prediction_time
                            metrics['frame_num'] = i
                            per_frame_metrics.append(metrics)
                    else:
                        driving = get_frame(video_name, opt.target_frame_num, ifnormalize=False)
                        target_kp, source_index = model.extract_keypoints(driving)
                        target_kp['source_index'] = source_index
                        start = time.perf_counter()
                        predicted_driving = model.predict(target_kp)
                        prediction_time = 1000 * (time.perf_counter() - start)
                        prediction.append(predicted_driving)
                        metrics = get_quality(predicted_driving, driving)
                        metrics['latency'] = prediction_time
                        metrics['frame_num'] = opt.target_frame_num
                        per_frame_metrics.append(metrics)
                    
                    # saving info per setting    
                    np.save(f'{save_dir}/{setting}_per_frame_metrics_{save_suffix}.npy', per_frame_metrics)
                    #print(per_frame_metrics)
                    predictions.append(prediction)
                    averages = get_average_metrics(per_frame_metrics)
                    cross_setting_metrics[setting] = {}
                    for index, name in enumerate(['psnr', 'ssim', 'lpip', 'latency']):
                        cross_setting_metrics[setting][name] = averages[index]

            # saving info per video for all settings
            df = pd.DataFrame.from_dict(cross_setting_metrics)
            df.to_csv(f'{save_dir}/{save_suffix}.csv', header=True, index=False, mode="w")
            start_imageio = time.perf_counter()
            if opt.generate_video:
                imageio.mimsave(f'{save_dir}/{save_suffix}.mp4',
                        np.concatenate(predictions, axis=2), fps = int(opt.output_fps))
            else:
                imageio.imsave(f'{save_dir}/{save_suffix}.png',
                        np.hstack([image[0] for image in predictions]))
            print("Saving the final output", time.perf_counter() - start_imageio)
            num_videos += 1
            #if num_videos == 3:
            #    break

except Exception as e:
    print(e)
