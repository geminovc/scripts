# vpx
cd ../../../end2end_experiments
export CONFIG_PATH='/data1/pantea/nets_scripts/paper_configs/resolution1024_vpx.yaml'

trace=paper_vpx_shrink
person=xiran
save_prefix=/data1/pantea/nsdi_fall_2022/latency/vpx_main_100s
window=1000
log_dir=${save_prefix}/resolution1024x1024/${person}/1.mp4/quantizer-1/vpx_min550000_default550000_max550000bitrate/run0

# full-range quantizer
python vpx_baseline_vary_resolution.py \
--resolutions 1024x1024 \
--uplink-trace /data1/pantea/nets_scripts/traces/${trace} \
--downlink-trace /data1/pantea/nets_scripts/traces/12mbps_trace \
--duration 100 --window ${window} --runs 1 \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024 \
--people ${person} \
--save-prefix ${save_prefix} \
--executable-dir /data1/pantea/aiortc/examples/videostream-cli \
--csv ${save_prefix}/vpx_${trace}.csv \
--quantizer-list -1 --vpx-default-bitrate-list 550000 \
--video-num-range 0 0 --disable-mahimahi  \
