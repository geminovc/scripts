DIR_PATH=/Users/panteababaahmadi/Documents/GitHub/nets_meta/youtube_dataset
for person in "needle_drop" #"fancy_fueko"  "jen_psaki"  "kayleigh"  "seth_meyer"  "trever_noah"  "tucker"  "xiran";
do
    for folder in "train" "test";
    do
        for file in $DIR_PATH/dataset_1024/fom_personalized_1024/${person}/${folder}/*;
        do
            mkdir -p $DIR_PATH/dataset/fom_personalized_512/${person}/${folder}
            filename=$(basename "$file")
            fbname=${filename%%.*}
            source=$DIR_PATH/dataset_1024/fom_personalized_1024/${person}/${folder}/${fbname}.mp4
            dest=$DIR_PATH/dataset/fom_personalized_512/${person}/${folder}/${fbname}.mp4
            #echo ${dest}
            #echo ${source}
            ffmpeg -i ${source} -s 512x512 -c:a copy ${dest}
        done;
    done;
done;
