#!/bin/sh

# main experiment for Ours 256x256
cd ../../../end2end_experiments
nets_scripts_dir=/data4/pantea/nets_scripts #change
aiortc_dir=/data4/pantea/aiortc  #change
person=needle_drop
save_prefix=./adaptation/ours_everything_comparison_perfect_estimator_shrinked_trace
window=1000
log_dir=${save_prefix}/${person}/1.mp4/lrquantizer-1/quantizer32/run0

# full-range quantizer
python adaptation.py \
--lr-enable-gcc \
--duration 3600  --window ${window} --runs 1 \
--root-dir /video-conf/scratch/pantea_mapmaker/fom_dataset_adaptation \
--people ${person} \
--save-prefix ${save_prefix} \
--executable-dir ${aiortc_dir}/examples/videostream-cli \
--csv ${save_prefix}/ours_perfect.csv \
--quantizer-list 32 --lr-quantizer-list -1 \
--configs-dir ${nets_scripts_dir}/paper_configs/exps_overview \
--generator-type occlusion_aware --resolution 1024 \
--video-num-range 0 0 --disable-mahimahi  \


cd ${nets_scripts_dir}/post_experiment_process

python plot_bw_trace_vs_estimation.py \
	--log-path ${log_dir}/sender.log \
	--save-dir ${log_dir} \
	--output-name sender \
	--window ${window}


python get_metrics_timeseries.py \
	--template-output ${log_dir}/timeseries_sender_w${window}_ms.csv \
	--save-dir ${log_dir} \
	--video-path-1 /video-conf/scratch/pantea_mapmaker/fom_dataset_adaptation/${person}/test/1.mp4 \
	--video-path-2 ${log_dir}/received.mp4 \
	--window ${window}


python estimate_rtt_at_sender.py \
	--log-path ${log_dir}/sender.log \
	--save-dir ${log_dir} \
	--output-name sender
