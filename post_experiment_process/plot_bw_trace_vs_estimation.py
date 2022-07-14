import argparse
import sys
sys.path.append('../')
import log_parser
import numpy as np
from utils import *
from estimate_bw_at_sender import get_average_bw_over_window, get_kbits_per_ms, get_full_trace, get_bw_logs
from process_utils import plot_graph

parser = argparse.ArgumentParser(description='Collect bw logs info.')
parser.add_argument('--window', type=int,
                    help='duration to aggregate data (assumes ms)',
                    default=200)
parser.add_argument('--save-dir', type=str,
                    help='directory to save graph in', default='./bw_graphs')
parser.add_argument('--output-name', type=str,
                    help='file to save final graph in', default="bw")
parser.add_argument('--log-path', type=str,
                    help='path to the log file', required=True)
parser.add_argument('--trace-path', type=str,
                    help='path to the trace file', required=True)
args = parser.parse_args()


def get_common_intervals(windowed_trace_bw, sent_video_bitrates, windowed_estimated_bw):
    min_len = min(len(windowed_trace_bw), len(sent_video_bitrates), len(windowed_estimated_bw))
    return np.clip(windowed_trace_bw[0:min_len], 0, 12000), np.clip(sent_video_bitrates[0:min_len], 0, 12000),\
            np.clip(windowed_estimated_bw[0:min_len], 0, 12000)


if __name__ == "__main__":
    stats = log_parser.gather_trace_statistics(args.log_path, args.window/1000)
    sent_video_bitrates = [i/(args.window) for i in stats['bitrates']['video']]
    save_suffix = f'{args.output_name}_w{args.window}_ms'
    plot_graph(np.linspace(0, args.window * len(sent_video_bitrates)/1000, len(sent_video_bitrates)),\
          [sent_video_bitrates],\
          ['sent video bitrates'], \
          ['r'], 'time (s)', 'bitrate (kbps)', 'sent bitrate',\
          args.save_dir, f'sent_rtp_{save_suffix}')
    try:
        estimated_max_bws, received_estimated_time = get_bw_logs(args.log_path)
        compression_size, compression_time = log_parser.gather_encoder_statistics(args.log_path)

        if len(estimated_max_bws) > 0:
            estimated_max_kbpms = get_kbits_per_ms(estimated_max_bws, received_estimated_time, \
                                                    is_ms=False, is_kbits=True)
            windowed_estimated_bw = get_average_bw_over_window(estimated_max_kbpms, window=args.window)
            # replace 0s with previous estimation
            for i in range(1, len(windowed_estimated_bw)):
                if windowed_estimated_bw[i] == 0:
                    windowed_estimated_bw[i] = windowed_estimated_bw[i - 1]

            full_trace = get_full_trace(args.trace_path, int(1000 * max(received_estimated_time) + 1))
            windowed_trace_bw = get_average_bw_over_window(full_trace, window=args.window)
            windowed_trace_bw, sent_video_bitrates, windowed_estimated_bw = get_common_intervals(windowed_trace_bw,\
                                                                sent_video_bitrates, windowed_estimated_bw)

            plot_graph(np.linspace(0, args.window * len(windowed_trace_bw)/1000, len(windowed_trace_bw)),\
                      [windowed_trace_bw, windowed_estimated_bw, sent_video_bitrates],\
                      ['link', 'estimated bw from receiver', 'sent video bitrates'], \
                      ['r', 'g', 'b'], 'time (s)', 'bitrate (kbps)', 'sent vs link vs estimated bitrate',\
                      args.save_dir, f'link_vs_sent_vs_estimation_{save_suffix}')

            plot_graph(compression_time, [compression_size],\
                      ['payload size'], \
                      ['m'], 'time (s)', 'payload size (bytes)', 'Encoder output',\
                      args.save_dir, f'encoder_output_vs_time_{save_suffix}')

            plot_graph([i for i in range(len(compression_size))], [compression_size],\
                      ['payload size'], \
                      ['m'], 'frame index', 'payload size (bytes)', 'Encoder output',\
                      args.save_dir, f'encoder_output_vs_frame_index_{save_suffix}')

            print("Avergae sent video bitrate", np.mean(sent_video_bitrates))
            print("Avergae encoder payload size per frame", np.mean(compression_size))
    except Exception as e:
        print(e)
        pass
