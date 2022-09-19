import subprocess
import av
import torch
import torch.nn.functional as F
import argparse
from skimage import img_as_float32
import numpy as np

from aiortc.codecs.vpx import Vp8Encoder, Vp8Decoder, vp8_depayload
from aiortc.jitterbuffer import JitterFrame

parser = argparse.ArgumentParser(description='Profile VP8.')
parser.add_argument('--video-path', type=str, required=True,
                    help='path to original video file')
parser.add_argument('--target-resolution', type=int,
                    help='resolution to reconstruct to', default=126)
parser.add_argument('--target-bitrate', type=int, required=True,
                    help='target bitrate (in bits per second) to supply to VP8') 
args = parser.parse_args()


def get_frame_from_video_codec(av_frame, av_frame_index, encoder, decoder, quantizer=-1, bitrate=None):
    """ go through the encoder/decoder pipeline to get a 
        representative decoded frame
    """
    if bitrate == None:
        payloads, timestamp = encoder.encode(av_frame, quantizer=quantizer, enable_gcc=False)
    else:
        payloads, timestamp = encoder.encode(av_frame, quantizer=-1, \
                target_bitrate=bitrate, enable_gcc=False)
    payload_data = [vp8_depayload(p) for p in payloads]
    jitter_frame = JitterFrame(data=b"".join(payload_data), timestamp=timestamp)
    decoded_frames = decoder.decode(jitter_frame)
    decoded_frame_av = decoded_frames[0]
    decoded_frame = decoded_frame_av.to_rgb().to_ndarray()
    return decoded_frame_av, decoded_frame, sum([len(p) for p in payloads])


def get_bitrate(stream, video_duration):
    """ get bitrate (in kbps) from a sequence of frame sizes and video
        duration in seconds
    """
    total_bytes = np.sum(stream)
    return total_bytes * 8 / video_duration / 1000.0


def get_video_duration(filename):
    """ get duration of video in seconds 
    """
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)


def frame_to_tensor(frame, device):
    """ convert numpy arrays to tensors for reconstruction pipeline """
    array = np.expand_dims(frame, 0).transpose(0, 3, 1, 2)
    tensor = torch.from_numpy(array)
    return tensor.float().to(device)


def resize_tensor_to_array(input_tensor, output_size, device, mode='nearest'):
    """ resizes a float tensor of range 0.0-1.0 to an int numpy array
        of output_size
    """
    output_array = F.interpolate(input_tensor, output_size, mode=mode).data.cpu().numpy()
    output_array = np.transpose(output_array, [0, 2, 3, 1])[0]
    output_array *= 255
    output_array = output_array.astype(np.uint8)
    return output_array

video_name = args.video_path
lr_size = args.target_resolution
target_bitrate = args.target_bitrate
video_duration = get_video_duration(video_name)

container = av.open(file=video_name, format=None, mode='r')
stream = container.streams.video[0]
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

lr_encoder = Vp8Encoder()
lr_decoder = Vp8Decoder()

frame_idx = 0
lr_stream = []
for av_frame in container.decode(stream):
    if lr_size == 1024:
        driving_lr_av = av_frame
    else:
        frame = av_frame.to_rgb().to_ndarray()
        driving = frame_to_tensor(img_as_float32(frame), device)
        driving_lr = resize_tensor_to_array(driving, lr_size, device)

        driving_lr_av = av.VideoFrame.from_ndarray(driving_lr)
        driving_lr_av.pts = av_frame.pts
        driving_lr_av.time_base = av_frame.time_base

    quantizer_level = -1
            
    driving_lr_av, driving_lr, compressed_tgt = get_frame_from_video_codec(driving_lr_av,
            av_frame.index, lr_encoder, lr_decoder, quantizer_level, target_bitrate)

    frame_idx += 1 
    if frame_idx % 1000 == 0:
        print(f'finished {frame_idx} frames')
    
    lr_stream.append(compressed_tgt)
lr_br = get_bitrate(lr_stream, video_duration)
print(f'Video: {video_name}, Resolution: {lr_size}, Achieved Bitrate: {lr_br}')
