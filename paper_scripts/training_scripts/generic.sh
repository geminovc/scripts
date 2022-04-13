CODE_DIR=$1
PREV_CHECKPOINT=$2
cd $CODE_DIR
export PYTHONPATH=$PYTHONPATH:$PWD
cd  first_order_model

python run.py --config config/overview_exps_for_512_resolution.yaml --log_dir /video-conf/scratch/pantea_experiments_tardy --experiment_name generic_512_kp_at_256_with_hr_skip_connections --person_id generic --checkpoint "${PREV_CHECKPOINT}"
