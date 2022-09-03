#!/bin/sh
# compares Bicubic at a series of low resolutions and different quantizer and bitrates values
export CONFIG_PATH='/data1/pantea/nets_scripts/paper_configs/resolution1024_bicubic.yaml'
cd ../../end2end_experiments
python lr_video_experiments.py \
--lr-resolutions 64x64 128x128 256x256 512x512 \
--duration 1000 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people needle_drop kayleigh xiran fancy_fueko adam_neely \
--save-prefix /data1/pantea/nsdi_fall_2022/bicubic_fixed_quantizer_logs \
--executable-dir /data1/pantea/aiortc/examples/videostream-cli \
--csv data/nsdi_fall_2022_bicubic_fixed_quantizer_all_ppl_3_videos \
--quantizer-list 32 --lr-quantizer-list 63 55 48 40 32 16 8 2 \
--default-bitrate-list 500000 \
--reference-update-freq 5000 \
--video-num-range 0 2 --disable-mahimah --use_bicubic \

python lr_video_experiments.py \
--lr-resolutions 256x256 512x512 \
--duration 1000 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people needle_drop kayleigh xiran fancy_fueko adam_neely \
--save-prefix /data1/pantea/nsdi_fall_2022/bicubic_full_range_quantizer_logs \
--executable-dir /data1/pantea/aiortc/examples/videostream-cli \
--csv data/nsdi_fall_2022_bicubic_full_range_quantizer_all_ppl_3_videos \
--quantizer-list 32 --lr-quantizer-list -1 \
--default-bitrate-list 100000 200000 400000 500000 1000000 1500000 3000000 \
--reference-update-freq 5000 \
--video-num-range 0 2 --disable-mahimah --use_bicubic \

python lr_video_experiments.py \
--lr-resolutions 64x64 128x128 \
--duration 1000 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people needle_drop kayleigh xiran fancy_fueko adam_neely \
--save-prefix /data1/pantea/nsdi_fall_2022/bicubic_full_range_quantizer_logs \
--executable-dir /data1/pantea/aiortc/examples/videostream-cli \
--csv data/nsdi_fall_2022_bicubic_full_range_quantizer_all_ppl_3_videos \
--quantizer-list 32 --lr-quantizer-list -1 \
--default-bitrate-list 1000000  \
--reference-update-freq 5000 \
--video-num-range 0 2 --disable-mahimah --use_bicubic \

# plot data
#cd ../plot_scripts
#./vpx_baseline_vary_resolution_quantizer.R
