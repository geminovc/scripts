#!/bin/sh
# compares SwinIR_LTE at a series of low resolutions and different quantizer and bitrates values
export CONFIG_PATH='/data4/pantea/nets_scripts/paper_configs/resolution1024_swinir_lte.yaml'
cd ../../end2end_experiments

python lr_video_experiments.py \
--lr-resolutions 256x256 512x512 \
--duration 16200 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people needle_drop kayleigh xiran fancy_fueko adam_neely \
--save-prefix /data4/pantea/nsdi_fall_2022/swinir_lte_full_range_quantizer_logs_256_and_512 \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv data/nsdi_fall_2022_swinir_lte_full_range_quantizer_all_ppl_3_videos_256_and_512 \
--quantizer-list 32 --lr-quantizer-list -1 \
--lr-target-bitrate-list 15000 45000 75000 105000 180000 300000 420000 \
--video-num-range 0 2 --disable-mahimah \

python lr_video_experiments.py \
--lr-resolutions 64x64 128x128 \
--duration 16200 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people needle_drop kayleigh xiran fancy_fueko adam_neely \
--save-prefix /data4/pantea/nsdi_fall_2022/swinir_lte_full_range_quantizer_logs_64_and_128 \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv data/nsdi_fall_2022_swinir_lte_full_range_quantizer_all_ppl_3_videos_64_and_128 \
--quantizer-list 32 --lr-quantizer-list -1 \
--lr-target-bitrate-list 15000 45000 \
--video-num-range 0 2 --disable-mahimah \


python aggregate_approach_comparison_data.py \
--data-paths data/nsdi_fall_2022_swinir_lte_full_range_quantizer_all_ppl_3_videos_256_and_512 data/nsdi_fall_2022_swinir_lte_full_range_quantizer_all_ppl_3_videos_64_and_128 \
--settings SwinIR SwinIR \
--columns-names setting lr_resolution lr_quantizer lr_target_bitrate kbps psnr ssim ssim_db orig_lpips lpips face_lpips lr_psnr lr_ssim lr_ssim_db lr_orig_lpips lr_lpips lr_face_lpips latency \
--csv-name /data4/pantea/nsdi_fall_2022/swinir_lte_full_range_quantizer_aggregate.csv \

# plot data
#cd ../plot_scripts
#./vpx_baseline_vary_resolution_quantizer.R
