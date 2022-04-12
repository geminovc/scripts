# Divide the videos into clips of 10 second
DIR="/Users/panteababaahmadi/Documents/GitHub/nets_meta/youtube_dataset/dataset"
for speaker in "jen_psaki" # "xiran" # "fancy_fueko" "seth_meyer" "tucker" #"kayleigh" "trever_noah" "tucker"
do
    for phase in train test
        do
            for file in ${DIR}/${speaker}/spatially_cropped/train/*
            do
                for start in {0..120..10}
                do
                    filename=$(basename "$file")
                    fbname=${filename%%.*}
                    ((end=start+10))
                    ffmpeg -ss $start -to $end  -i $file -c copy ${DIR}/${speaker}/train_short_clips/id${speaker}_${end}_${fbname}.mp4
        done
    done
done
