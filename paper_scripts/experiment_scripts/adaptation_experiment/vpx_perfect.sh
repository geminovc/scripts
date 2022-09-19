#!/bin/sh

# vpx
cd ../../../end2end_experiments
nets_scripts_dir=/data4/pantea/nets_scripts #change
aiortc_dir=/data4/pantea/aiortc #change
person=needle_drop
save_prefix=./adaptation/vpx_everything_comparison_perfect_estimator_shrinked_trace
window=1000
log_dir=${save_prefix}/resolution1024x1024/${person}/1.mp4/quantizer-1/vpx_min550000_default550000_max550000bitrate/run0

export CONFIG_PATH=${nets_scripts_dir}/paper_configs/resolution1024_vpx.yaml

# full-range quantizer
python vpx_baseline_vary_resolution.py \
--resolutions 1024x1024 \
--duration 1500 --window ${window} --runs 1 \
--root-dir /video-conf/scratch/pantea_mapmaker/fom_dataset_adaptation \
--people ${person} \
--save-prefix ${save_prefix} \
--executable-dir ${aiortc_dir}/examples/videostream-cli \
--csv ${save_prefix}/vpx_perfect.csv \
--quantizer-list -1 --vpx-default-bitrate-list 550000 \
--video-num-range 0 0 --disable-mahimahi \

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

