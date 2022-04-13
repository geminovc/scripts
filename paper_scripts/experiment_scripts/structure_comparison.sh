EXCE_DIR=$1
DURATION=$2
PERSON=$3
RESOLUTION=$4
cd ../..

python structure_comparison_experiments.py --duration $DURATION --csv-name ./${PERSON}_${RESOLUTION}_diget.csv --save-prefix ./${PERSON}_${RESOLUTION} --executable-dir "${EXCE_DIR}"  --root-dir /video-conf/scratch/pantea/fom_personalized_${RESOLUTION} --person-list ${PERSON} --num-runs 1 --window $DURATION --resolution ${RESOLUTION}

# Example
# CUDA_VISIBLE_DEVICES=0 python structure_comparison_experiments.py --duration 360 --csv-name ./xiran_1024_diget.csv --save-prefix ./xiran_1024 --executable-dir /data4/pantea/aiortc/examples/videostream-cli --root-dir ./videos/1024/ --person-list xiran --num-runs 1 --window 0.05 --resolution 1024
