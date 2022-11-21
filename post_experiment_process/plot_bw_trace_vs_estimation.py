import argparse
import sys
sys.path.append('../')
import log_parser
import numpy as np
from nets_utils import *
from process_utils import *
import csv

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


def get_common_intervals(windowed_trace_bw, ref_video_bitrates, windowed_estimated_bw):
    min_len = min(len(windowed_trace_bw), len(ref_video_bitrates), len(windowed_estimated_bw))
    return np.clip(windowed_trace_bw[0:min_len], 0, 12000), np.clip(ref_video_bitrates[0:min_len], 0, 12000),\
            np.clip(windowed_estimated_bw[0:min_len], 0, 12000)


def get_bitrate_using_compression(compressed):
    # TODO: change the function below based on what's logged  in the aiortc code
    bitrates = []
    estimated_bitrates = []
    while len(compressed) % 30 != 0:
        compressed.append(0)

    frame_indexs = range(0, len(compressed))
    hardcoded_bitrates = [min(max(750000 - 55 * 2 * x, 20000) + max(0, -942500 + 55 * 2 * x),
                            650000) for x in frame_indexs]
    # TODO for Vibha: This below for example starts at 1Mbps and goes down to 20kbps
    #and then goes up again
    #hardcoded_bitrates = [min(max(1200000 - 110 * x, 20000) + max(0, -942500 + 110  *x),
    #                       1000000) for x in frame_indexs]

    for i in range(0, int(len(compressed)/30) - 1):
            bitrates.append(8 * sum(compressed[i * 30: (i + 1)*30]) / 1000)
            estimated_bitrates.append(np.average(hardcoded_bitrates[i * 30: (i + 1)*30]) / 1000)
    return bitrates, estimated_bitrates


if __name__ == "__main__":
    bitrate_stats = get_log_statistics(args.log_path, args.window/1000)
    window = bitrate_stats['window']
    elapsed_time = bitrate_stats['elapsed_time']
    ref_video_bitrates = [i/window/1000 for i in bitrate_stats['bitrates']['video']]
    lr_video_bitrates = [i/window/1000 for i in bitrate_stats['bitrates']['lr_video']]
    total_video_bitrates = [sum(value) for value in zip(ref_video_bitrates, lr_video_bitrates)]
    ref_estimated_max_bws = [i/1000 for i in bitrate_stats['bitrates']['estimated_max_bw_video']]
    lr_estimated_max_bws = [i/1000 for i in bitrate_stats['bitrates']['estimated_max_bw_lr_video']]
    compression_stats  = log_parser.gather_encoder_statistics(args.log_path)
    save_suffix = f'{args.output_name}_w{args.window}_ms'
    try:
        if len(total_video_bitrates) > 0:
            # replace 0s with previous estimation
            for i in range(1, len(lr_estimated_max_bws)):
                if ref_estimated_max_bws[i] == 0:
                    ref_estimated_max_bws[i] = ref_estimated_max_bws[i - 1]
                if lr_estimated_max_bws[i] == 0:
                    lr_estimated_max_bws[i] = lr_estimated_max_bws[i - 1]
 
            time_axis = np.linspace(0, args.window * len(total_video_bitrates)/1000,
                                    len(total_video_bitrates))
            cc_bitrate_estimation = lr_estimated_max_bws if np.average(lr_estimated_max_bws) > 0 \
                                        else ref_estimated_max_bws

            #TODO: fix trace problem
            if os.path.exists(args.trace_path):
                """use the real trace if experiment was with mahimahi"""
                full_trace = get_full_trace(args.trace_path,
                                        args.window * (int(elapsed_time) + 100))
                windowed_trace = get_average_bw_over_window(full_trace, window=args.window)
                if np.average(lr_estimated_max_bws) > 0:
                    #crop the model warmup part
                    windowed_trace = windowed_trace[20:len(cc_bitrate_estimation) + 20]
                else:
                    windowed_trace = windowed_trace[:len(cc_bitrate_estimation)]
            else:
                windowed_trace = lr_estimated_max_bws if np.average(lr_estimated_max_bws) > 0 \
                                    else ref_estimated_max_bws

            #windowed_trace = get_common_intervals(windowed_trace,
            #bitrate_stats['elapsed_time'], bitrate_stats['first_packet_time'])

            plot_graph(time_axis,\
                      [windowed_trace, cc_bitrate_estimation, total_video_bitrates],\
                      ['link', 'estimated bw from receiver', 'sent video bitrates'], \
                      ['r', 'g', 'b'], 'time (s)', 'bitrate (kbps)', \
                      f'sent vs link vs estimated bitrate for {args.output_name}', \
                      args.save_dir, f'link_vs_sent_vs_estimation_{save_suffix}')

            plot_graph(time_axis,\
                      [ref_estimated_max_bws, ref_video_bitrates],\
                      ['estimated bw', 'sent video bitrates'], \
                      ['g', 'b'], 'time (s)', 'bitrate (kbps)', \
                      f'reference stream sent vs estimated bitrate for {args.output_name}', \
                      args.save_dir, f'ref_sent_vs_estimation_{save_suffix}')

            plot_graph(time_axis,\
                      [lr_estimated_max_bws, lr_video_bitrates],\
                      ['estimated bw', 'sent video bitrates'], \
                      ['g', 'b'], 'time (s)', 'bitrate (kbps)', \
                      f'low-res stream sent vs estimated bitrate for {args.output_name}', \
                      args.save_dir, f'lr_video_sent_vs_estimation_{save_suffix}')

            plot_graph(time_axis,\
                  [ref_video_bitrates, [np.mean(ref_video_bitrates) for x in ref_video_bitrates]],\
                  ['ref video bitrates', 'average'], \
                  ['r', 'b'], 'time (s)', 'bitrate (kbps)', \
                  f'sent reference video bitrate for {args.output_name}',\
                  args.save_dir, f'sent_ref_video_rtp_{save_suffix}')

            plot_graph(time_axis,\
                  [lr_video_bitrates, [np.mean(lr_video_bitrates) for x in lr_video_bitrates]],\
                  ['lr video bitrates', 'average'], \
                  ['r', 'b'], 'time (s)', 'bitrate (kbps)', \
                  f'sent low-res  video bitrate for {args.output_name}',\
                  args.save_dir, f'sent_lr_video_rtp_{save_suffix}')

            plot_graph(time_axis,\
                  [total_video_bitrates, [np.mean(total_video_bitrates) for x in total_video_bitrates]],\
                  ['total video bitrates', 'average'], \
                  ['r', 'b'], 'time (s)', 'bitrate (kbps)', \
                  f'total sent video bitrate for {args.output_name}',\
                  args.save_dir, f'sent_total_video_rtp_{save_suffix}')
            

            for video_type in ['video', 'lr_video']:
                if len(compression_stats[video_type]) > 30:
                    plot_graph(compression_stats[f'{video_type}_time'], [compression_stats[video_type]],\
                              ['encoder payload size'], \
                              ['m'], 'time (s)', f'payload size (bytes)',\
                              f'{video_type} encoder output for {args.output_name}',\
                              args.save_dir, f'{video_type}_encoder_output_vs_time_{save_suffix}',\
                              is_scatter=(video_type=='video'))

                    compression_bitrates, hardcoded_bitrates = get_bitrate_using_compression(compression_stats[video_type])
                    plot_graph(range(0, len(compression_bitrates)), [compression_bitrates, hardcoded_bitrates],\
                              ['bitrates from encoder', 'hardcoded link'], \
                              ['b', 'r'], 'time (s)', f'kbps',\
                              f'{video_type} encoder output for {args.output_name}',\
                              args.save_dir, f'bitrates_using_encoder_{video_type}_{save_suffix}')

                    # dump compression timeseries
                    timeseries_file = open(os.path.join(args.save_dir, f'compression_timeseries_{save_suffix}.csv'), 'wt')
                    writer = csv.writer(timeseries_file)
                    writer.writerow(['actual_bitrate', 'estimated_bitrate', 'total_video_bitrates'])
                    for i in range(len(hardcoded_bitrates)):
                        writer.writerow([hardcoded_bitrates[i], hardcoded_bitrates[i], compression_bitrates[i]])
                    timeseries_file.close()

            measurement_file = open(os.path.join(args.save_dir, f'bitrate_average_{save_suffix}.csv'), 'wt')
            measurement_string = f'Average sent reference video bitrate {np.mean(ref_video_bitrates)} kbps \n'
            measurement_string += f'Average sent low-res video bitrate {np.mean(lr_video_bitrates)} kbps \n'
            measurement_string += f'Average sent total video bitrate {np.mean(total_video_bitrates)} kbps \n'
            print(measurement_string)
            writer = csv.writer(measurement_file)
            writer.writerow(['Average reference bitrate', 'Average low-res bitrate', 'Average total bitrate'])
            writer.writerow([np.mean(ref_video_bitrates), np.mean(lr_video_bitrates), np.mean(total_video_bitrates)])
            measurement_file.close()

            # dump timeseries
            timeseries_file = open(os.path.join(args.save_dir, f'timeseries_{save_suffix}.csv'), 'wt')
            writer = csv.writer(timeseries_file)
            writer.writerow(['actual_bitrate', 'estimated_bitrate', 'total_video_bitrates'])
            for i in range(len(total_video_bitrates)):
                writer.writerow([windowed_trace[i], cc_bitrate_estimation[i], total_video_bitrates[i]])

            timeseries_file.close()

    except Exception as e:
        print(e)
