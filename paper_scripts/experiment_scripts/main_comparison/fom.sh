#!/bin/sh
# compares original paper's FOMM
export CONFIG_PATH='/data4/pantea/nets_scripts/paper_configs/resolution1024_fom_standard.yaml'
cd ../../end2end_experiments
python structure_comparison_experiments.py \
--resolution 1024 \
--duration 1000 --window 1000 --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people xiran needle_drop kayleigh fancy_fueko adam_neely \
--save-prefix /data3/pantea/nsdi_fall_2022/keypoint_based_models_logs \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv data/nsdi_fall_2022_fom_original_paper \
--setting-list fom_original_paper \
--quantizer-list 32 \
--reference-update-freq-list 18000 \
--video-num-range 0 2 --disable-mahimah  \

# plot data
#cd ../plot_scripts
#./vpx_baseline_vary_resolution_quantizer.R
