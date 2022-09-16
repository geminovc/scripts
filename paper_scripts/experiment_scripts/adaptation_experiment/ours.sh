#!/bin/sh

# main experiment for Ours 256x256
cd ../../../end2end_experiments

trace=test_with_frame_save
person=needle_drop
save_prefix=/data4/pantea/ours_${trace}_q250_enable_lr_gcc


# full-range quantizer
python adaptation.py \
--lr-enable-gcc \
--uplink-trace /data4/pantea/nets_scripts/traces/${trace} \
--downlink-trace /data4/pantea/nets_scripts/traces/12mbps_trace \
--duration 500  --window 1000 --runs 1 \
--root-dir /data4/pantea/fom_dataset_9min \
--people ${person} \
--save-prefix ${save_prefix} \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--csv ${save_prefix}/ours_${trace}.csv \
--quantizer-list 32 --lr-quantizer-list -1 \
--configs-dir /data4/pantea/nets_scripts/paper_configs/exps_overview \
--generator-type occlusion_aware --resolution 1024 \
--video-num-range 0 0 --disable-mahimahi \

cd /data4/pantea/nets_scripts/post_experiment_process

python plot_bw_trace_vs_estimation.py \
	--log-path ${save_prefix}/${person}/1.mp4/lrquantizer-1/quantizer32/run0/sender.log \
	--trace-path /data4/pantea/nets_scripts/traces/${trace} \
	--save-dir ${save_prefix}/${person}/1.mp4/lrquantizer-1/quantizer32/run0 \
	--output-name sender \
	--window 1000

python estimate_rtt_at_sender.py \
	--log-path ${save_prefix}/${person}/1.mp4/lrquantizer-1/quantizer32/run0/sender.log \
	--save-dir ${save_prefix}/${person}/1.mp4/lrquantizer-1/quantizer32/run0 \
	--output-name sender
