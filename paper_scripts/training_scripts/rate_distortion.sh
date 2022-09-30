#!/bin/bash
DEVICE_NUM=$1
OUTPUT_DIR=$2

for person in "xiran" "kayleigh" "needle_drop" "adam_neely" "fancy_fueko"
do
    for config in "lr128_tgt15Kb" "lr256_tgt45Kb" "lr256_tgt75Kb" "lr256_tgt105Kb" "lr512_tgt180Kb" "lr512_tgt420Kb"
    do
        CUDA_VISIBLE_DEVICES=${DEVICE_NUM} python run.py \
            --config config/paper_configs/exps_overview/${config}.yaml \
            --experiment_name ${speaker}_${config} \
            --checkpoint /video-conf/scratch/vibhaa_chunky_directory/vox-cpk.pth.tar \
            --log_dir ${OUTPUT_DIR} \
            --person_id ${person}
    done
done
