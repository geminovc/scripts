#!/bin/sh

# main ML experiment for SwinIR 
cd /data1/pantea/aiortc/nets_implementation/first_order_model
FINAL_DIR=/video-conf/scratch/pantea_tardy/final_results/swinir
MAIN_CONFIG_DIR=/data1/pantea/aiortc/nets_implementation/first_order_model/config/paper_configs/exps_overview/swinir
for person in "xiran" "fancy_fueko" "needle_drop" "kayleigh" "adam_neely";
do
    for setting in lr128_tgt15Kb lr256_tgt45Kb lr256_tgt75Kb lr256_tgt105Kb lr512_tgt180Kb lr512_tgt420Kb
    do
        CUDA_VISIBLE_DEVICES=0 python run.py --config ${MAIN_CONFIG_DIR}/${setting}.yaml \
		--experiment_name single_source --person_id ${person} --mode reconstruction \
		--checkpoint ${FINAL_DIR}/${setting}/${person}/00000029-checkpoint.pth.tar
    done
done


for person in "xiran" "fancy_fueko" "needle_drop" "kayleigh" "adam_neely";
do
    for setting in lr128_tgt15Kb lr256_tgt45Kb lr256_tgt75Kb lr256_tgt105Kb lr512_tgt180Kb lr512_tgt420Kb
    do
        CUDA_VISIBLE_DEVICES=0 python run.py --config ${MAIN_CONFIG_DIR}/${setting}.yaml \
		--experiment_name single_source --person_id ${person} --mode reconstruction \
		--checkpoint ${FINAL_DIR}/${setting}/${person}/00000029-checkpoint.pth.tar
    done
done
