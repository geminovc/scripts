# Divide the videos into clips of 10 second
DIR="/Users/panteababaahmadi/Documents/GitHub/nets_meta/youtube_dataset/dataset"
for speaker in "fancy_fueko" #"jen_psaki" # "xiran" # "fancy_fueko" "seth_meyer" "tucker" #"kayleigh" "trever_noah" "tucker"
do
    mkdir -p ${DIR}/${speaker}/train_short_clips
    for file in ${DIR}/${speaker}/spatially_cropped/train/*
    do
        val=$(ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -print_format csv ${file} | cut -    d',' -f2);
        if [ ${val} -gt 300 ]
        then
            for start in {0..120..10}
            do
                filename=$(basename "$file")
                fbname=${filename%%.*}
                ((end=start+10))
                ffmpeg -ss $start -to $end  -i $file -c copy ${DIR}/${speaker}/train_short_clips/id${speaker}_${end}_${fbname}.mp4
            done
        fi
    done
done
