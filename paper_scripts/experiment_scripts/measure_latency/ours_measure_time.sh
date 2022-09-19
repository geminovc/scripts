#!/bin/sh

# main experiment for Ours 256x256
cd ../../../end2end_experiments

# full-range quantizer
python lr_video_experiments.py \
--lr-resolutions 256x256 \
--duration 600 --window 1000 --runs 1 \
--root-dir /data1/pantea/fom_dataset_1024_20fps \
--people xiran \
--save-prefix /data1/pantea/nsdi_fall_2022/latency/ours_use_av_conversion_received_time_place_display_100s_long_videe_at_30fps \
--executable-dir /data1/pantea/aiortc/examples/videostream-cli \
--csv /data1/pantea/test_new.csv \
--quantizer-list 32 --lr-quantizer-list -1 \
--lr-target-bitrate-list 75 \
--configs-dir /data1/pantea/nets_scripts/paper_configs/exps_overview \
--generator-type occlusion_aware --resolution 1024 \
--video-num-range 0 0 --disable-mahimah  \
