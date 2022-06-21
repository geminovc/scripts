#!/bin/bash
video_file=$1
fps=$2
sender_log_file=$3
img_save_dir=$4
exec_dir=$5
enable_prediction=$6
reference_frame_update_freq=$7
quantizer=$8
socket_path=$9

args1="offer --play-from ${video_file} --signaling-path ${socket_path}"
args2=" --signaling unix-socket --reference-update-freq ${reference_frame_update_freq}"
args3=" --fps $fps --save-dir ${img_save_dir} --quantizer ${quantizer} --verbose"

if [[ "${enable_prediction}" == "True" ]]; then
    args2="${args2} --enable-prediction"
fi

python3 ${exec_dir}/cli.py ${args1}${args2}${args3} 2>${sender_log_file}
