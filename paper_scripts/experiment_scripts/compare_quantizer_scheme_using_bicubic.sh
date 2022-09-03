#!/bin/sh
# compares Bicubic at a series of low resolutions and different quantizer and bitrates values
export CONFIG_PATH='/data4/pantea/nets_scripts/paper_configs/resolution1024_bicubic.yaml'
cd ../../end2end_experiments


python lr_video_experiments.py \
--lr-resolutions 256x256 512x512 \
--duration 1000 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people kayleigh  \
--save-prefix /data3/pantea/kayleigh_quantizer_scheme_full_range_using_bicubic \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv data/kayleigh_quantizer_scheme_full_range_using_bicubic \
--quantizer-list 32 --lr-quantizer-list -1 \
--default-bitrate-list 5000 50000 100000 200000 500000 800000 1000000 3000000 7000000 \
--reference-update-freq 5000 \
--video-num-range 0 0 --disable-mahimah --use_bicubic \


python lr_video_experiments.py \
--lr-resolutions 256x256 512x512 \
--duration 1000 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people kayleigh  \
--save-prefix /data3/pantea/kayleigh_quantizer_scheme_fixed_range_using_bicubic \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv data/kayleigh_quantizer_scheme_fixed_range_using_bicubic \
--quantizer-list 32 --lr-quantizer-list 63 56 48 40 32 24 16 8 \
--default-bitrate-list 500000 \
--reference-update-freq 5000 \
--video-num-range 0 0 --disable-mahimah --use_bicubic \

# plot data
#cd ../plot_scripts
#./vpx_baseline_vary_resolution_quantizer.R
