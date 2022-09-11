#!/bin/sh

# main experiment for VPX 1024x1024
cd ../../../end2end_experiments

export CONFIG_PATH='/data4/pantea/nets_scripts/paper_configs/resolution1024_vpx.yaml'
# full-range quantizer
python vpx_baseline_vary_resolution.py \
--resolutions 1024x1024 \
--duration 600 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people xiran \
--save-prefix /data4/pantea/nsdi_fall_2022/main_comparison/vpx_full_quantizer_jitterbuffer_2048 \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv /data4/pantea/nsdi_fall_2022/main_comparison/data/vpx_full_quantizer_jitterbuffer_2048 \
--quantizer-list -1 \
--vpx-default-bitrate-list 50000 100000 200000 300000 500000 1000000 \
--video-num-range 0 4 --disable-mahimah --just-aggregate \
