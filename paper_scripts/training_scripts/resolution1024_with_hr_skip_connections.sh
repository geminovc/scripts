person=$1
CODE_DIR=$2
cd $CODE_DIR
export PYTHONPATH=$PYTHONPATH:$PWD
cd  first_order_model

python3 run.py --config config/paper_configs/resolution1024_with_hr_skip_connections.yaml --log_dir /video-conf/scratch/pantea_experiments_tardy/resolution1024_with_hr_skip_connections --experiment_name ${person}_resolution1024_with_hr_skip_connections --person_id ${person} --checkpoint /video-conf/scratch/vibhaa_mm_log_directory/vox-cpk.pth.tar
