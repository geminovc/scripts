#!/bin/sh

# main experiment for SwinIR 256x256
cd ../../../end2end_experiments

export CONFIG_PATH='/data4/pantea/nets_scripts/paper_configs/resolution1024_swinir_lte.yaml'
# full-range quantizer
python lr_video_experiments.py \
--lr-resolutions 256x256 \
--duration 21600 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people xiran \
--save-prefix /data4/pantea/nsdi_fall_2022/main_comparison/swinir_lte_full_quantizer \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv /data4/pantea/nsdi_fall_2022/main_comparison/data/swinir_lte_full_quantizer \
--quantizer-list 32 --lr-quantizer-list -1 \
--lr-target-bitrate-list 45 75 105 \
--configs-dir /data4/pantea/nets_scripts/paper_configs \
--generator-type swinir_lte --resolution 1024 \
--video-num-range 0 4 --disable-mahimah \
