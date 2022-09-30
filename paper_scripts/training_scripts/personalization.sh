#!/bin/bash
DEVICE_NUM=$1
OUTPUT_DIR=$2

for person in "seth_meyers" "kayleigh" "needle_drop" "trevor_noah" "jen_psaki" "generic"
do
    CUDA_VISIBLE_DEVICES=${DEVICE_NUM} python run.py \
        --config config/paper_configs/personalization/resolution512_our_model.yaml \
        --experiment_name ${speaker} \
        --checkpoint /video-conf/scratch/vibhaa_chunky_directory/vox-cpk.pth.tar \
        --log_dir ${OUTPUT_DIR} \
        --person_id ${person}
done
