#!/bin/sh
# compares VPX at a series of resolutions and different quantizer and bitrates values
export CONFIG_PATH='/data4/pantea/nets_scripts/paper_configs/resolution1024_vpx.yaml'
cd ../../end2end_experiments
python vpx_baseline_vary_resolution.py \
--resolutions 64x64 128x128 256x256 512x512 \
--duration 400 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people needle_drop \
--save-prefix /data3/pantea/quantization_scheme_full_range \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv data/needle_drop_quantization_scheme_full_range_video_dur \
--quantizer-list -1 --default-bitrate-list 5000 50000 100000 200000 500000 800000 1000000 3000000 7000000 \
--video-num-range 0 0 --disable-mahimah  --just-aggregate \


python vpx_baseline_vary_resolution.py \
--resolutions 64x64 128x128 256x256 512x512 \
--duration 400 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people needle_drop \
--save-prefix /data3/pantea/quantization_scheme_fixed \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv data/needle_drop_quantization_scheme_fixed_range_video_dur \
--quantizer-list 63 55 50 48 32 16 8 2 --default-bitrate-list 100000 500000 \
--video-num-range 0 0 --disable-mahimah --just-aggregate \

# plot data
#cd ../plot_scripts
#./vpx_baseline_vary_resolution_quantizer.R
