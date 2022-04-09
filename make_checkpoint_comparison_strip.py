from first_order_model.fom_wrapper import FirstOrderModel
import imageio 
import numpy as np
import time
from argparse import ArgumentParser
from first_order_model.frames_dataset import get_num_frames, get_frame

parser = ArgumentParser()
parser.add_argument("--video_path",
                    default="/data4/pantea/nets_implementation/first_order_model/512_kayleigh_10_second_0_1.mp4",
                    help="path to the test video")
parser.add_argument("--generate_video",
                    action='store_true',
                    help="generate a video strip instead of an image strip")
parser.add_argument("--source_frame_num",
                    default=0,
                    type=int,
                    help="index of the source frame")
parser.add_argument("--target_frame_num",
                    default=1,
                    type=int,
                    help="index of the target frame")
parser.add_argument("--output_name",
                    default="comparison",
                    help="name of the output file to be saved")
parser.add_argument("--output_fps",
                    default=30,
                    help="fps of the final video if generate_video is set")
parser.add_argument("--source_update_frequency",
                    default=1800,
                    help="source update frequency if generate_video is set")
parser.add_argument("--config_list",
                    type=str,
                    nargs='+',
                    default=[ "/data4/pantea/nets_implementation/first_order_model/config/paper_configs/resolution512_with_hr_skip_connections.yaml"],
                    help="path to configs")
parser.add_argument('--checkpoint_list',
                    type=str,
                    nargs='+',
                    help='list of checkpoints',
                    default=['/video-conf/scratch/pantea_experiments_tardy/resolution512_with_hr_skip_connections/kayleigh_resolution512_with_hr_skip_connections 05_04_22_18.23.53/00000069-checkpoint.pth.tar'])

parser.set_defaults(verbose=False)
opt = parser.parse_args()
checkpoint_list = opt.checkpoint_list
config_list = opt.config_list

video_name = opt.video_path
num_frames = get_num_frames(video_name)
print("Number of frames in the video", num_frames)
source = get_frame(video_name, opt.source_frame_num, ifnormalize=False)
predictions = []

for config, checkpoint in zip(config_list, checkpoint_list):
    model = FirstOrderModel(config, checkpoint)

    source_kp, _= model.extract_keypoints(source)
    model.update_source(0, source, source_kp)
    old_source_index = 0
    times = []
    prediction = []

    if opt.generate_video:
        for i in range(0, num_frames):
            if i % opt.source_update_frequency == 0:
                source = get_frame(video_name, i, ifnormalize=False)
                source_kp, _= model.extract_keypoints(source)
                model.update_source(len(model.source_frames), source, source_kp) 
            
            driving = get_frame(video_name, i, ifnormalize=False)
            target_kp, source_index = model.extract_keypoints(driving)
            target_kp['source_index'] = source_index
            if source_index == old_source_index:
                update_source = False
            else:
                update_source = True
                old_source_index = source_index
            start = time.perf_counter()
            prediction.append(model.predict(target_kp, update_source))
            times.append(time.perf_counter() - start)
    else:
        driving = get_frame(video_name, opt.target_frame_num, ifnormalize=False)
        target_kp, source_index = model.extract_keypoints(driving)
        target_kp['source_index'] = source_index
        start = time.perf_counter()
        prediction.append(model.predict(target_kp, True))
        times.append(time.perf_counter() - start)
    
    predictions.append(prediction)
    print(f"Average prediction time per frame for {config} is {sum(times)/len(times)}s.")

if opt.generate_video:
    imageio.mimsave(f'{opt.output_name}_freq{opt.source_update_frequency}.mp4', np.concatenate(predictions, axis=2), fps = int(opt.output_fps))
else:
    imageio.imsave(f'{opt.output_name}.png', np.hstack([image[0] for image in predictions]))
