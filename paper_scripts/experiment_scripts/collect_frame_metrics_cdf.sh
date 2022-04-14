#!/bin/sh
python collect_per_frame_stats.py --save-prefix logs --person kayleigh --setting personalized --reference-frame-frequency-list 10 60 --vpx-quantizer-list 2 32 63 --video-name 0_2.mp4 --csv-name data/kayleigh_video0_2_per_frame_data

./frame_quality_cdf.R data/kayleigh_video0_2_per_frame_data pdfs/kayleigh_metrics_cdf.pdf
