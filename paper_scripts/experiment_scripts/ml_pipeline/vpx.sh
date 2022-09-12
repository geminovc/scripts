#!/bin/sh

# main ML experiment for VPX
cd /data4/pantea/aiortc/nets_implementation/first_order_model
FINAL_DIR=/video-conf/scratch/pantea_mapmaker/final_results/vpx
MAIN_CONFIG_DIR=/data4/pantea/aiortc/nets_implementation/first_order_model/config/paper_configs/exps_overview/vpx
for person in "adam_neely" "xiran" "fancy_fueko" "needle_drop" "kayleigh";
do
    for setting in lr1024_tgt1000Kb lr1024_tgt800Kb lr1024_tgt600Kb lr1024_tgt400Kb lr1024_tgt200Kb
    do
        CUDA_VISIBLE_DEVICES=0 python run.py --config ${MAIN_CONFIG_DIR}/${setting}.yaml \
		--experiment_name single_source --person_id ${person} --mode reconstruction \
		--checkpoint ${FINAL_DIR}/${setting}/${person}/00000029-checkpoint.pth.tar
    done
done
