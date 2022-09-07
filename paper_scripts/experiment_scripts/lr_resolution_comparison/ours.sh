#!/bin/sh

# main experiment for Ours for a fixed bitrate in different resolutions
cd ../../../end2end_experiments

# full-range quantizer
python lr_video_experiments.py \
--lr-resolutions 64x64 128x128 \
--duration 2400 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people xiran \
--save-prefix /data4/pantea/nsdi_fall_2022/lr_resolution_comparison/ours_full_quantizer \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv /data4/pantea/nsdi_fall_2022/lr_resolution_comparison/data/ours_full_quantizer \
--quantizer-list 32 --lr-quantizer-list -1 \
--lr-target-bitrate-list 45 \
--configs-dir /data4/pantea/nets_scripts/paper_configs/exps_overview \
--generator-type occlusion_aware --resolution 1024 \
--video-num-range 0 4 --disable-mahimah \

python aggregate_approach_comparison_data.py \
--data-paths /data4/pantea/nsdi_fall_2022/main_comparison/data/ours_full_quantizer /data4/pantea/nsdi_fall_2022/lr_resolution_comparison/data/ours_full_quantizer \
--settings Selected-lr Other-lr \
--csv-name /data4/pantea/nsdi_fall_2022/lr_resolution_comparison/data/aggregated_full_quantizer \
--columns-names setting kbps psnr ssim ssim_db orig_lpips lr_resolution lr_quantizer lr_target_bitrate \
