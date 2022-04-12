DIR_PATH=/Users/panteababaahmadi/Documents/GitHub/nets_meta/youtube_dataset
for person in "fancy_fueko" "needle_drop" "xiran" "fancy_fueko"  "jen_psaki"  "kayleigh"  "seth_meyer"  "trever_noah"  "tucker"  "xiran_close_up";
do
    for folder in "test"; #"train";
    do
        # # 1024
        # for file in ${DIR_PATH}/dataset_1024/fom_personalized_1024/${person}/${folder}/*;
        # do
        #     echo ${file};
        #     filename=$(basename "$file")
        # 	fbname=${filename%%.*}
        #     ffmpeg -y -i $file -filter:v fps=30 ${DIR_PATH}/dataset_1024/fom_personalized_1024_30fps/${person}/${folder}/${fbname}.mp4

        # done;

        #512
        for file in ${DIR_PATH}/dataset/fom_personalized_512/${person}/${folder}/*;
        do
            echo ${file};
            filename=$(basename "$file")
        	fbname=${filename%%.*}
            ffmpeg -y -i $file -filter:v fps=30 ${DIR_PATH}/dataset/fom_personalized_512_30fps/${person}/${folder}/${fbname}.mp4

        done;
    done;
done;
