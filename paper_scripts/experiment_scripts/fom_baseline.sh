#!/bin/sh
# compares FOM different quantizer and bitrates values
export CONFIG_PATH='/data4/pantea/nets_scripts/paper_configs/resolution1024_fom_standard.yaml'
cd ../../end2end_experiments
python structure_comparison_experiments.py \
--resolution 1024 \
--duration 70 --window 70000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people xiran \
--save-prefix /data3/pantea/keypoint_based_models \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv data/xiran_keypoint_based_models \
--setting-list fom_standard \
--quantizer-list 32 \
--reference-update-freq 5000 \
--video-num-range 0 0 --disable-mahimah \

# plot data
#cd ../plot_scripts
#./vpx_baseline_vary_resolution_quantizer.R
