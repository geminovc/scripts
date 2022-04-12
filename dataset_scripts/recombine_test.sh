# Divide the videos into clips of 10 second
DIR="/Users/panteababaahmadi/Documents/GitHub/nets_meta/youtube_dataset/dataset"
for speaker in "tucker" #"jen_psaki" # "xiran" # "fancy_fueko" "seth_meyer" "tucker" #"kayleigh" "trever_noah" "tucker"
do
    mkdir -p ${DIR}/${speaker}/${speaker}/test
    for start in {1..5..1}
    do
        echo ${start}
        for f in ${DIR}/${speaker}/spatially_cropped/test/*_${start}.mp4
        do
            echo file \'$f\' >> ${DIR}/${speaker}/test_${start}.txt
        done
        ffmpeg -safe 0 -f concat -i ${DIR}/${speaker}/test_${start}.txt -c copy ${DIR}/${speaker}/${speaker}/test/id${speaker}_${start}.mp4
    done
done
