# Making a resolution x resolution dataset from a 1024 x 1024 dataset
DIR_PATH=$1
speaker=$2
resolution=$3
for folder in "train" "test";
do
    for file in $DIR_PATH/dataset_1024/fom_personalized_1024/${person}/${folder}/*
    do
        mkdir -p $DIR_PATH/dataset/fom_personalized_${resolution}/${person}/${folder}
        filename=$(basename "$file")
        fbname=${filename%%.*}
        source=$DIR_PATH/dataset_1024/fom_personalized_1024/${person}/${folder}/${fbname}.mp4
        dest=$DIR_PATH/dataset/fom_personalized_${resolution}/${person}/${folder}/${fbname}.mp4
        ffmpeg -i ${source} -s ${resolution}x${resolution} -c:a copy ${dest}
    done
done
