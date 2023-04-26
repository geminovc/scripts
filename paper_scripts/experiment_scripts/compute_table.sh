## ACCURACY
# depthwise full model accuracy
python collect_results_from_ml_pipeline.py --approaches-to-compare personalization --base-dir-list /video-conf/scratch/vibhaa_lam2_new/depthwise_personalization  --person-list kayleigh jen_psaki trevor_noah seth_meyers needle_drop --people-for-strip needle_drop seth_meyers jen_psaki --save-prefix ../data/compute_experiments/personalization_depthwise --csv-name summary.csv --img-width 512 --video-num 2 --frame-num 1952 --summarize

# regular full model accuracy
python collect_results_from_ml_pipeline.py --approaches-to-compare personalization --base-dir-list /video-conf/scratch/vibhaa_mm_log_directory/personalization/  --person-list kayleigh jen_psaki trevor_noah seth_meyers needle_drop --people-for-strip needle_drop seth_meyers jen_psaki --save-prefix ../data/compuute_experiments_personalization --csv-name summary.csv --img-width 512 --video-num 2 --frame-num 1952 --summarize

# netadapted ones
for conv_type in 'depthwise' 'normal';
do 
    for percent in '10' '1.5';
    do 
        python collect_results_from_ml_pipeline.py --approaches-to-compare personalization --base-dir-list /video-conf/scratch/vedantha/paper_trials/${conv_type}/${percent}  --person-list kayleigh jen_psaki trevor_noah seth_meyers needle_drop --people-for-strip needle_drop seth_meyers jen_psaki --save-prefix ../data/compute_experiments/${conv_type}_${percent}_percent --csv-name summary.csv --img-width 512 --video-num 2 --frame-num 1952 --summarize
    done
done

## PARAMETERS AND MACS
# regular conv
CUDA_VISIBLE_DEVICES=3 python run.py --config config/paper_configs/personalization/resolution512_our_model.yaml --experiment_name single_source_profile --person_id needle_drop --mode reconstruction --checkpoint /video-conf/scratch/vibhaa_mm_log_directory/personalization/personalization/needle_drop/00000029-checkpoint.pth.tar --profile

# depthwise
CONV_TYPE='depthwise' CUDA_VISIBLE_DEVICES=3 python run.py --config config/paper_configs/personalization/resolution512_our_model.yaml --experiment_name single_source_profile --person_id needle_drop --mode reconstruction --checkpoint /video-conf/scratch/vibhaa_tardy/depthwise_conv/no_encoder/generic_depthwise\ 24_03_23_15.24.30/00000029-checkpoint.pth.tar --profile

# netadapted versions
for conv_type in 'depthwise' 'normal';
do 
    for percent in '10' '1.5';
    do 
        CONV_TYPE=${conv_type} CUDA_VISIBLE_DEVICES=3 python run.py --config config/paper_configs/netadapt/netadapt.yaml --experiment_name single_source_profile --person_id needle_drop --mode reconstruction --netadapt_checkpoint /video-conf/scratch/vedantha/paper_trials/${conv_type}/${percent}/generic/00000038-checkpoint.pth.tar --profile;
    done
done


## TIMING (needs to be rerun on each platform)
for conv_type in 'depthwise' 'normal';
do 
    # full models
    CONV_TYPE=${conv_type} python measure_times.py --resolution 512 --config config/paper_configs/personalization/resolution512_our_model.yaml

    # netadapted versions
    for percent in '10' '1.5';
    do 
        CONV_TYPE=${conv_type} python measure_times.py --config config/paper_configs/netadapt/netadapt.yaml --resolution 512 --netadapt_checkpoint /video-conf/scratch/vedantha/paper_trials/${conv_type}/${percent}/generic/00000038-checkpoint.pth.tar
    done
done
