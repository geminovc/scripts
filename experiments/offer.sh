#!/bin/bash
EXAMPLE_DIR="/home/vibhaa/aiortc/examples/videostream-cli"
video_file=$1
fps=$2
sender_log_file=$3

python3 ${EXAMPLE_DIR}/cli.py offer --play-from ${video_file} \
    --signaling-path /tmp/test.sock --signaling unix-socket \
    --fps $fps --verbose 2>${sender_log_file}
