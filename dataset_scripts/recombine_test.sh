# Combine sessions (clips) from the same url into a single video 
DIR=$1
speaker=$2
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
