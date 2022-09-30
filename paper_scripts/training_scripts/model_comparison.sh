#!/bin/bash
DEVICE_NUM=$1
OUTPUT_DIR=$2

for person in "xiran" "kayleigh" "needle_drop" "adam_neely" "fancy_fueko"
do
    for model in "fomm" "pure_upsampling" "fomm_skip_connections_lr_in_decoder" \
        "sme_3_pathways_with_occlusion" "fomm_3_pathways_with_occlusion"
    do
        CUDA_VISIBLE_DEVICES=${DEVICE_NUM} python run.py \
            --config config/paper_configs/model_architecture_comparison/${model}.yaml \
            --experiment_name ${speaker}_${model} \
            --checkpoint /video-conf/scratch/vibhaa_chunky_directory/vox-cpk.pth.tar \
            --log_dir ${OUTPUT_DIR} \
            --person_id ${person}
    done
done
