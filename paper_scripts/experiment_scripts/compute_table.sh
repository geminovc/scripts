## ACCURACY
# depthwise full model accuracy
python collect_results_from_ml_pipeline.py --approaches-to-compare personalization --base-dir-list /video-conf/scratch/vibhaa_lam2_new/depthwise_personalization  --person-list kayleigh jen_psaki trevor_noah seth_meyers needle_drop --people-for-strip needle_drop seth_meyers jen_psaki --save-prefix ../data/personalization_depthwise --csv-name summary.csv --img-width 512 --video-num 2 --frame-num 1952 --summarize

# regular full model accuracy
python collect_results_from_ml_pipeline.py --approaches-to-compare personalization --base-dir-list /video-conf/scratch/vibhaa_mm_log_directory/personalization/  --person-list kayleigh jen_psaki trevor_noah seth_meyers needle_drop --people-for-strip needle_drop seth_meyers jen_psaki --save-prefix ../data/personalization --csv-name summary.csv --img-width 512 --video-num 2 --frame-num 1952 --summarize


## PARAMETERS AND MACS
# regular conv
CUDA_VISIBLE_DEVICES=3 python run.py --config config/paper_configs/personalization/resolution512_our_model.yaml --experiment_name single_source_profile --person_id needle_drop --mode reconstruction --checkpoint /video-conf/scratch/vibhaa_mm_log_directory/personalization/personalization/needle_drop/00000029-checkpoint.pth.tar --profile

# depthwise
CONV_TYPE='depthwise' CUDA_VISIBLE_DEVICES=3 python run.py --config config/paper_configs/personalization/resolution512_our_model.yaml --experiment_name single_source_profile --person_id needle_drop --mode reconstruction --checkpoint /video-conf/scratch/vibhaa_tardy/depthwise_conv/no_encoder/generic_depthwise\ 24_03_23_15.24.30/00000029-checkpoint.pth.tar --profile

# timing (needs to be rerun on each platform)
