#!/bin/bash
DEVICE_NUM=$1
CPK_BASE_DIR=$2
# expects a generic and personalization directory in the CPK_BASE

for person in "seth_meyers" "kayleigh" "needle_drop" "trevor_noah" "jen_psaki"
do
    CUDA_VISIBLE_DEVICES=${DEVICE_NUM} python run.py \
        --config config/paper_configs/personalization/resolution512_our_model.yaml \
        --experiment_name single_source \
        --checkpoint ${CPK_BASE_DIR}/personalization/${person}/00000029-checkpoint.pth.tar \
        --person_id ${person} \
        --mode reconstruction
done

for person in "seth_meyers" "kayleigh" "needle_drop" "trevor_noah" "jen_psaki"
do
    CUDA_VISIBLE_DEVICES=${DEVICE_NUM} python run.py \
        --config config/paper_configs/personalization/resolution512_our_model.yaml \
        --experiment_name single_source_${person} \
        --checkpoint ${CPK_BASE_DIR}/generic//00000029-checkpoint.pth.tar \
        --person_id ${person} \
        --mode reconstruction
done
