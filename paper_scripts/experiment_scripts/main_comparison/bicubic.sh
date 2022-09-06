#!/bin/sh

# main experiment for Bicubic 256x256
cd ../../../end2end_experiments

export CONFIG_PATH='/data4/pantea/nets_scripts/paper_configs/resolution1024_bicubic.yaml'
# full-range quantizer
python lr_video_experiments.py \
--lr-resolutions 256x256 \
--duration 2000  --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people xiran \
--save-prefix /data4/pantea/nsdi_fall_2022/main_comparison/bicubic_full_quantizer \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv /data4/pantea/nsdi_fall_2022/main_comparison/data/bicubic_full_quantizer \
--quantizer-list 32 --lr-quantizer-list -1 \
--lr-target-bitrate-list 45 75 105 \
--configs-dir /data4/pantea/nets_scripts/paper_configs \
--generator-type bicubic --resolution 1024 \
--video-num-range 0 4 --disable-mahimah \
