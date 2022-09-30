#!/bin/bash
DEVICE_NUM=$1
CPK_BASE_DIR=$2

for person in "xiran" "kayleigh" "needle_drop" "adam_neely" "fancy_fueko"
do
    for config in "lr128_tgt15Kb" "lr128_tgt45Kb" "lr128_tgt75Kb" "lr128_tgt_random" "lr128_no_encoder"
    do
        CUDA_VISIBLE_DEVICES=${DEVICE_NUM} python run.py \
            --config config/paper_configs/encoder_effect/${config}.yaml \
            --experiment_name single_source \
            --checkpoint ${CPK_BASE_DIR}/${config}/${person}/00000029-checkpoint.pth.tar \
            --person_id ${person} \
            --mode reconstruction
    done
done
