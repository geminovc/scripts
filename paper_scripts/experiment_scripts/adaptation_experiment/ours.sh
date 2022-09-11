#!/bin/sh

# main experiment for Ours 256x256
cd ../../../end2end_experiments

# full-range quantizer
python lr_video_experiments.py \
--uplink-trace /data4/pantea/nets_scripts/traces/cellular/Verizon-LTE-driving.down \
--downlink-trace /data4/pantea/nets_scripts/traces/12mbps_trace \
--lr-resolutions 256x256 \
--duration 2000 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people kayleigh \
--save-prefix /data4/pantea/test_with_mahimahi \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv /data4/pantea/test_with_mahimahi.csv \
--quantizer-list 32 --lr-quantizer-list -1 \
--lr-target-bitrate-list 75 \
--configs-dir /data4/pantea/nets_scripts/paper_configs/exps_overview \
--generator-type occlusion_aware --resolution 1024 \
--video-num-range 0 0  \

