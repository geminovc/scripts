cd ../../end2end_experiments
# xiran
python structure_comparison_experiments.py --duration 300 \
--csv-name ./xiran_1024_diget.csv --save-prefix ./xiran_1024 \
--executable-dir /data4/pantea/aiortc/examples/videostream-cli \
--root-dir /video-conf/scratch/pantea/fom_personalized_1024/ \
--person-list xiran --num-runs 1 --window 1 --resolution 1024
