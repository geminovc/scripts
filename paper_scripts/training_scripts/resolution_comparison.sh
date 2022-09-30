#!/bin/bash
DEVICE_NUM=$1
OUTPUT_DIR=$2

for person in "xiran" "kayleigh" "needle_drop" "adam_neely" "fancy_fueko"
do
    for config in "lr64_tgt45Kb" "lr128_tgt45Kb" "lr256_tgt45Kb"
    do
        CUDA_VISIBLE_DEVICES=${DEVICE_NUM} python run.py \
            --config config/paper_configs/resolution_comparison/${config}.yaml \
            --experiment_name ${speaker}_${config} \
            --checkpoint /video-conf/scratch/vibhaa_chunky_directory/vox-cpk.pth.tar \
            --log_dir ${OUTPUT_DIR} \
            --person_id ${person}
    done
done
