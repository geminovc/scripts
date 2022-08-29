#!/bin/sh
# compares SwinIR_LTE at a series of low resolutions and different quantizer and bitrates values
export CONFIG_PATH='/data4/pantea/nets_scripts/paper_configs/resolution1024_swinir_lte.yaml'
cd ../../end2end_experiments
python lr_video_experiments.py \
--duration 70 --window 1000 --runs 3 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people xiran \
--save-prefix /data3/pantea/xiran_256x256lr_swinir_lte_logs \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv data/xiran_256x256lr_swinir_lte_logs \
--quantizer-list 32 --lr-quantizer-list 40 45 50 55 63 \
--reference-update-freq 5000 \
--video-num-range 0 4 --disable-mahimah \

# plot data
#cd ../plot_scripts
#./vpx_baseline_vary_resolution_quantizer.R
