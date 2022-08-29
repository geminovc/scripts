#!/bin/sh
# compares Bicubic at a series of low resolutions and different quantizer and bitrates values
export CONFIG_PATH='/data4/pantea/nets_scripts/paper_configs/resolution1024_bicubic.yaml'
cd ../../end2end_experiments
python lr_video_experiments.py \
--lr-resolutions 64x64 128x128 256x256 \
--duration 70 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people xiran \
--save-prefix /data3/pantea/xiran_bicubic_logs \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv data/xiran_bicubic_logs \
--quantizer-list 32 --lr-quantizer-list 32 40 45 50 55 63 \
--reference-update-freq 5000 \
--video-num-range 0 2 --disable-mahimah --use_bicubic \

# plot data
#cd ../plot_scripts
#./vpx_baseline_vary_resolution_quantizer.R
