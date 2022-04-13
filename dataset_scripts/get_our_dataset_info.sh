DIR="/video-conf/scratch/pantea/fom_personalized_512"
SAVE_PREFIX="/video-conf/scratch/pantea/fom_personalized_dataset_info2"

for speaker in "tucker"  "jen_psaki" "xiran" "xiran_close_up" "needle_drop" "fancy_fueko" "seth_meyer"  "kayleigh" "trever_noah"
do
    for phase in train test
    do
        python3 get_dataset_info.py \
            --video_root ${DIR}/${speaker}/${phase} \
            --save_dir ${SAVE_PREFIX}/dataset_info/512/${speaker} \
            --save_name ${phase}
    done
done

DIR="/video-conf/scratch/pantea/fom_personalized_1024"
for speaker in "xiran" "needle_drop" "fancy_fueko" "kayleigh"
do
    for phase in train test
    do
        python3 get_dataset_info.py \
            --video_root ${DIR}/${speaker}/${phase} \
            --save_dir ${SAVE_PREFIX}/dataset_info/1024/${speaker} \
            --save_name ${phase}
    done
done
