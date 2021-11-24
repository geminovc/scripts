#!/bin/bash
video_file=$1
fps=$2
sender_log_file=$3
img_save_dir=$4
exec_dir=$5

python3 ${exec_dir}/cli.py offer --play-from ${video_file} \
    --signaling-path /tmp/test.sock --signaling unix-socket \
    --fps $fps --save-dir ${img_save_dir} --verbose 2>${sender_log_file}
