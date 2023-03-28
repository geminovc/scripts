#!/bin/sh

# main experiment for Ours gcc
cd ../../../end2end_experiments
nets_scripts_dir=/data4/pantea/nets_scripts #change
aiortc_dir=/data4/pantea/aiortc  #change
trace=paper_ours
person=needle_drop
save_prefix=/data4/pantea/adaptation_end2end/ours_gcc #change
window=1000
video_num=1
video_root=/video-conf/scratch/pantea_mapmaker/fom_dataset_adaptation
log_dir=${save_prefix}/${person}/${video_num}.mp4/lrquantizer-1/quantizer32/run0

# full-range quantizer
python adaptation.py \
--lr-enable-gcc \
--uplink-trace /video-conf/scratch/pantea_mapmaker/traces/${trace} \
--downlink-trace /video-conf/scratch/pantea_mapmaker/traces/12mbps_trace \
--duration 600 --window ${window} --runs 1 \
--root-dir ${video_root} \
--people ${person} \
--save-prefix ${save_prefix} \
--executable-dir ${aiortc_dir}/examples/videostream-cli \
--csv ${save_prefix}/ours_gcc_${trace}.csv \
--quantizer-list 32 --lr-quantizer-list -1 \
--configs-dir ${nets_scripts_dir}/paper_configs/exps_overview \
--generator-type occlusion_aware --resolution 1024 \
--video-num-range 0 0 \


cd ${nets_scripts_dir}/post_experiment_process

mm-graph ${log_dir}/mahimahi.log 100 --no-port --no-display --plot-direction \
	egress > ${log_dir}/mahimahi.eps 2> ${log_dir}/mmgraph.log

python plot_bw_trace_vs_estimation.py \
	--log-dir ${log_dir} \
	--end-point sender \
	--trace-path /video-conf/scratch/pantea_mapmaker/traces/${trace} \
	--save-dir ${log_dir} \
	--output-name sender \
	--window ${window}


python get_metrics_timeseries.py \
	--template-output ${log_dir}/timeseries_sender_w${window}_ms.csv \
	--save-dir ${log_dir} \
	--video-path-1 ${video_root}/${person}/test/${video_num}.mp4 \
	--video-path-2 ${log_dir}/received.mp4 \
	--window ${window}
