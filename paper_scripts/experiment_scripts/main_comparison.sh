#!/bin/sh

# main comparison between personalized, generic, VPX by varying different parameters at 512x512
cd ../../end2end_experiments
python vary_reference_frame_frequency.py \
--duration 350 --window 350 --num-runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_512 \
--people kayleigh seth_meyer trever_noah jen_psaki tucker \
--save-prefix logs --executable-dir /data1/vibhaa/aiortc/examples/videostream-cli \
--csv data/personalized_512_diff_ref_frames --quantizer 32 \
--reference-frame-frequency-list 10 60 300 900 30000 --video-num-range 0 2 --seting personalized

python vary_reference_frame_frequency.py \
--duration 350 --window 350 --num-runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_512 \
--people kayleigh seth_meyer trever_noah jen_psaki tucker \
--save-prefix logs --executable-dir /data1/vibhaa/aiortc/examples/videostream-cli \
--csv data/generic_512_diff_ref_frames --quantizer 32 \
--reference-frame-frequency-list 10 60 300 900 30000 --video-num-range 0 2 --seting generic

python vpx_baseline_vary_resolution.py --resolutions 512x512 \
--duration 230 --window 230 --num-runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_512 \
--people kayleigh seth_meyer trever_noah jen_psaki tucker \
--save-prefix logs_512_comparison --executable-dir /data1/vibhaa/aiortc/examples/videostream-cli \
--csv data/vpx_512_diff_quantizers --quantizer-list 2 16 32 48 63 --video-num-range 0 2

# needs some careful aggregation of data from the top three manually into a single file
cd ../plot_scripts
./main_comparison.R
