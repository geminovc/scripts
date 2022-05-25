# Divide the train videos into clips of 10 second
DIR=$1
speaker=$2
mkdir -p ${DIR}/${speaker}/${speaker}/train
for file in ${DIR}/${speaker}/spatially_cropped/train/*
do
    val=$(ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -print_format csv ${file} | cut -d',' -f2);

    filename=$(basename "$file")
    fbname=${filename%%.*}

    if [ ${val} -gt 300 ]
    then
        for start in {0..120..10}
        do
            ((end=start+10))
            ffmpeg -ss $start -to $end  -i $file -c copy ${DIR}/${speaker}/${speaker}/train/id${speaker}_${end}_${fbname}.mp4
        done
    else
        cp $file ${DIR}/${speaker}/${speaker}/train/id${speaker}_10_${fbname}.mp4
    fi
done
