#!/bin/sh
# compares FOM different quantizer and reference-frequency  values
export CONFIG_PATH='/data1/pantea/nets_scripts/paper_configs/resolution1024_fom_standard.yaml'
cd ../../end2end_experiments
python structure_comparison_experiments.py \
--resolution 1024 \
--duration 1000 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people xiran needle_drop kayleigh fancy_fueko adam_neely \
--save-prefix /data1/pantea/nsdi_fall_2022/keypoint_based_models_logs \
--executable-dir /data1/pantea/aiortc/examples/videostream-cli \
--csv data/nsdi_fall_2022_keypoint_based_models \
--setting-list fom_original_paper \
--quantizer-list 32 \
--reference-update-freq-list 10 100 450 900 1800 3600 \
--video-num-range 0 2 --disable-mahimah  \

# plot data
#cd ../plot_scripts
#./vpx_baseline_vary_resolution_quantizer.R
