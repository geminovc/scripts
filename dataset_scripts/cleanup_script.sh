DIR_PATH=/Users/panteababaahmadi/Documents/GitHub/nets_meta/youtube_dataset
for person in "needle_drop" #"xiran" #"fancy_fueko"  "jen_psaki"  "kayleigh"  "seth_meyer"  "trever_noah"  "tucker"  "xiran";
do
    for folder in "train" "test";
    do
        # 1024
        for filename in ${DIR_PATH}/dataset_1024/fom_personalized_1024/${person}/${folder}/*;
        do
            val=$(ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -print_format csv ${filename} | cut -d',' -f2);
            if ! [[ "$val" =~ ^[0-9]+$ ]]
            then
                echo ${filename};
                rm ${filename};
            elif [ ${val} -lt 3 ]
            then
                echo ${filename};
                rm ${filename};
            fi
        done;

        #512
        # for filename in ${DIR_PATH}/dataset/fom_personalized_512/${person}/${folder}/*;
        # do
        #     val=$(ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -print_format csv ${filename} | cut -d',' -f2);
        #     if ! [[ "$val" =~ ^[0-9]+$ ]]
        #     then
        #         echo ${filename};
        #         rm ${filename};
        #     elif [ ${val} -lt 3 ]
        #     then
        #         echo ${filename};
        #         rm ${filename};
        #     fi
        # done;
    done;
done;
