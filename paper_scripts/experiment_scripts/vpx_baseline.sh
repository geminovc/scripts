#!/bin/sh
# compares VPX at a series of resolutions and different quantizer and bitrates values
export CONFIG_PATH='/data4/pantea/aiortc/nets_implementation/first_order_model/config/resolution1024_vpx.yaml'
cd ../../end2end_experiments
python vpx_baseline_vary_resolution.py \
--resolutions 128x128 256x256 \
--duration 70 --window 1 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people xiran needle_drop \
--save-prefix /video-conf/scratch/pantea_experiments_mapmaker/vary_bitrate_and_quantization_logs \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv data/vary_bitrate_and_quantization_logs \
--quantizer-list -1 32 45 55 63 --default-bitrate-list 100000 500000 1000000 \
--video-num-range 0 2 --disable-mahimah \

# plot data
#cd ../plot_scripts
#./vpx_baseline_vary_resolution_quantizer.R
