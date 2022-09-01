import argparse
import pandas as pd

parser = argparse.ArgumentParser(description='Aggregate data of different settings for comparison graph.')
parser.add_argument('--data-paths', type=str, nargs='+',
                    help='paths to the experiment results',
                    default=['data/vpx_baseline', 'data/bicubic_baseline',
                            'data/swinir_lte_baseline', 'data/Ours', 'data/FOM'])
parser.add_argument('--settings', type=str, nargs='+',
                    help='name of the experiment to be displayed',
                    default=['vpx', 'bicubic','SwinIR-LTE', 'Ours', 'FOM'])
parser.add_argument('--columns-names', type=str, nargs='+',
                    help='name of the columns to be gathered',
                    default=['psnr', 'ssim', 'ssim_db', 'lpips', 'kbps', 'latency', 'quantizer', 'setting'])
parser.add_argument('--csv-name', type=str,
                    help='file to save final data in',
                    default="data/aggregate_1024_comparison_data")

args = parser.parse_args()

columns_names = args.columns_names
combined_df = pd.DataFrame(columns=columns_names)
for setting, data_path in zip(args.settings, args.data_paths):
    df = pd.read_csv(data_path)
    df['setting'] = setting
    combined_df = pd.concat([df[columns_names], combined_df], ignore_index=True)

combined_df.to_csv(args.csv_name, header=True, index=False, mode="w")
