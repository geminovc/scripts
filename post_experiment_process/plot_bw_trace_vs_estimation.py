import argparse
import sys
sys.path.append('../')
import argparse
import log_parser
import numpy as np
from utils import *
from estimate_bw_at_sender import get_average_bw_over_window, get_kbits_per_ms, get_full_trace, get_bw_logs
from process_utils import plot_graph

parser = argparse.ArgumentParser(description='Collect bw logs info.')
parser.add_argument('--save-dir', type=str,
                    help='directory to save graph in', default='./bw_graphs')
parser.add_argument('--output-name', type=str,
                    help='file to save final graph in', default="bw")
parser.add_argument('--log-path', type=str,
                    help='path to the log file', required=True)
parser.add_argument('--trace-path', type=str,
                    help='path to the trace file', required=True)
parser.add_argument('--window', type=int,
                    help='duration to aggregate bitrate over (in ms)',
                    default=200)
args = parser.parse_args()


def get_common_intervals(windowed_trace_bw, sent_video_bitrates, windowed_estimated_bw):
    min_len = min(len(windowed_trace_bw), len(sent_video_bitrates), len(windowed_estimated_bw))
    return windowed_trace_bw[1:min_len], sent_video_bitrates[1:min_len], windowed_estimated_bw[1:min_len]


if __name__ == "__main__":
    stats = log_parser.gather_trace_statistics(args.log_path, int(args.window/1000))
    sent_video_bitrates = stats['bitrates']['video']

    try:
        estimated_max_bws, received_estimated_time = get_bw_logs(args.log_path)
        if len(estimated_max_bws) > 0:
            estimated_max_kbpms = get_kbits_per_ms(estimated_max_bws, received_estimated_time, \
                                                    is_ms=False, is_kbits=True)
            windowed_estimated_bw = get_average_bw_over_window(estimated_max_kbpms, window=args.window)
            full_trace = get_full_trace(args.trace_path, int(1000 * max(received_estimated_time) + 1))
            windowed_trace_bw = get_average_bw_over_window(full_trace, window=args.window)
            windowed_trace_bw, sent_video_bitrates, windowed_estimated_bw = get_common_intervals(windowed_trace_bw,\
                                                                sent_video_bitrates, windowed_estimated_bw)
            plot_graph(np.linspace(0, args.window * len(windowed_trace_bw)/1000, len(windowed_trace_bw)),\
                      [windowed_trace_bw, sent_video_bitrates, windowed_estimated_bw],\
                      ['link', 'sent video bitrates', 'estimated bw from receiver'], \
                      ['r', 'b', 'g'], 'time (s)', 'bitrate (kbps)', 'sent vs link vs estimated bitrate',\
                      args.save_dir, f'{args.output_name}_w{args.window}_ms')
    except Exception as e:
        print(e)
        pass
