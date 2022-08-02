import argparse
import numpy as np
from process_utils import *

parser = argparse.ArgumentParser(description='Collect bw logs info.')
parser.add_argument('--window', type=int,
                    help='duration to aggregate data (assumes ms)',
                    default=200)
parser.add_argument('--save-dir', type=str,
                    help='directory to save graph in', default='./bw_graphs')
parser.add_argument('--output-name', type=str,
                    help='file to save final graph in', default="bw")
parser.add_argument('--max-time', type=int,
                    help='maximum time to plot the trace in second', required=True)
parser.add_argument('--trace-path', type=str,
                    help='path to the trace file', required=True)
args = parser.parse_args()

if __name__ == "__main__":
    save_suffix = f'{args.output_name}_w{args.window}_ms'
    full_trace = get_full_trace(args.trace_path, int(1000 * args.max_time + 1))
    windowed_trace_bw = get_average_bw_over_window(full_trace, window=args.window)
    plot_graph(np.linspace(0, args.window * len(windowed_trace_bw)/1000, len(windowed_trace_bw)),\
          [windowed_trace_bw],\
          ['link'], \
          ['r'], 'time (s)', 'bitrate (kbps)', \
          f'Link\'s Bitrate', \
          args.save_dir, f'link_bitrate_{save_suffix}')
