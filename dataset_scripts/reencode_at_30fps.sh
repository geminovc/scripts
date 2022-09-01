DIR=$1
speaker=$2
for folder in "test" "train";
do
    for file in ${DIR}/${speaker}/${folder}/*;
    do
        echo ${file};
        filename=$(basename "$file");
        fbname=${filename%%.*};
        ffmpeg -y -i $file -filter:v fps=30 ${DIR}/${speaker}/${folder}/${fbname}.mp4

    done;
done;
