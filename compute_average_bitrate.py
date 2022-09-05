from first_order_model.reconstruction import get_video_duration
import log_parser
import pandas as pd

def compute_bitrate(save_prefix):
    total_runs = 1
    window = 1000
    for run_num in range(total_runs):
        save_dir = f'{save_prefix}/run{run_num}'
        dump_file = f'{save_dir}/sender.log'
        saved_video_file = f'{save_dir}/received.mp4'
        saved_video_duration = get_video_duration(saved_video_file)
        stats = log_parser.gather_trace_statistics(dump_file, window / 1000)
        streams = list(stats['bits_sent'].keys())
        df = pd.DataFrame.from_dict(stats['bits_sent'])
        for s in streams:
            df[s] = (df[s].sum(axis=0) / saved_video_duration / 1000)
        print(df['video'] + df['lr_video'] + df['audio'] + df['keypoints'])

save_prefix = '/data4/pantea/nsdi_fall_2022/swinir_lte_full_range_quantizer_logs_high/lrresolution256x256/needle_drop/4.mp4/lrquantizer-1/quantizer32/vpx_min400000_default400000_max400000bitrate'
compute_bitrate(save_prefix)
