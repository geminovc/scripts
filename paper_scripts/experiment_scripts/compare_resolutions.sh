#!/bin/sh
# compares VPX at a series of resolutions and different quantizer values
cd ../../end2end_experiments
python vpx_baseline_vary_resolution.py \
--resolutions 256x256 512x512 1024x1024 \
--duration 230 --window 230 --num-runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people xiran needle_drop kayleigh fancy_fueko \
--save-prefix logs --executable-dir /data1/vibhaa/aiortc/examples/videostream-cli \
--csv data/baseline_diff_resolutions --quantizer-list 2 16 32 48 63 --video-num-range 0 2

# plot data
cd ../plot_scripts
./vpx_baseline_vary_resolution_quantizer.R
