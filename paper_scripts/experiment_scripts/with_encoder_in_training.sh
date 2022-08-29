#!/bin/sh
# compares with_encoder_in_training with 256x256lr model at a series of different quantizer and bitrates values
export CHECKPOINT_PATH='/video-conf/scratch/vibhaa_tardy/with_encoder_in_training/xiran1024_with_256x256lr_quant55_7x7LRkernel 22_08_22_15.18.42/00000099-checkpoint.pth.tar'
export CONFIG_PATH='/video-conf/scratch/vibhaa_tardy/with_encoder_in_training/xiran1024_with_256x256lr_quant55_7x7LRkernel 22_08_22_15.18.42/resolution1024_with_sr.yaml'

cd ../../end2end_experiments
python lr_video_experiments.py \
--duration 70 --window 1000 --runs 3 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people xiran \
--save-prefix /data3/pantea/xiran_256x256lr_with_encoder_in_training_lrquant55_7x7LRkernel_logs \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv data/xiran_256x256lr_with_encoder_in_training_lrquant55_7x7LRkernel \
--quantizer-list 32 48 55 --lr-quantizer-list 40 45 50 55 63 \
--reference-update-freq 5000 \
--video-num-range 0 4 --disable-mahimah \

# plot data
#cd ../plot_scripts
#./vpx_baseline_vary_resolution_quantizer.R
