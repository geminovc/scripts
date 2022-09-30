#!/bin/bash
DEVICE_NUM=$1
CPK_BASE_DIR=$2

for person in "xiran" "kayleigh" "needle_drop" "adam_neely" "fancy_fueko"
do
    for model in "fomm" "pure_upsampling" "fomm_skip_connections_lr_in_decoder" \
        "sme_3_pathways_with_occlusion" "fomm_3_pathways_with_occlusion"
    do
        CUDA_VISIBLE_DEVICES=${DEVICE_NUM} python run.py \
            --config config/paper_configs/model_architecture_comparison/${model}.yaml \
            --experiment_name single_source \
            --checkpoint ${CPK_BASE_DIR}/${model}/${person}/00000029-checkpoint.pth.tar \
            --person_id ${person} \
            --mode reconstruction
    done
done
