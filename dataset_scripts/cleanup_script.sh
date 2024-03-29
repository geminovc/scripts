# Delete very short clips (containing less than 3 frames) that are created while dividing the videos in shorter clips
DIR=$1
speaker=$2
for folder in "train" "test";
do
    echo ha ${DIR}/${speaker}
    for filename in ${DIR}/${speaker}/${folder}/*;
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
done;
