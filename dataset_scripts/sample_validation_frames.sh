#!/bin/bash
path="/video-conf/scratch/pantea/fom_personalized_512"
path2="/video-conf/scratch/vibhaa_tardy/dataset_256"

for speaker in "adam_neely" "xiran" "fancy_fueko" "needle_drop" "kayleigh";
do
    x=0
    for i in 1 2 3 4;
    do
        mkdir -p "${path2}/${speaker}/validation/${x}"
        ffmpeg -y -ss 00:00:05.01 -i "${path}/${speaker}/test/${i}.mp4" \
            -frames:v 1 "${path2}/${speaker}/validation/${x}/source.png" 
        ffmpeg -y -ss 00:00:07.01 -i "${path}/${speaker}/test/${i}.mp4" \
            -frames:v 1 "${path2}/${speaker}/validation/${x}/target.png" 
        ((x=x+1))
        
        mkdir -p "${path2}/${speaker}/validation/${x}"
        ffmpeg -y -ss 00:00:02.01 -i "${path}/${speaker}/test/${i}.mp4" \
            -frames:v 1 "${path2}/${speaker}/validation/${x}/source.png" 
        ffmpeg -y -ss 00:00:08.01 -i "${path}/${speaker}/test/${i}.mp4" \
            -frames:v 1 "${path2}/${speaker}/validation/${x}/target.png" 
        ((x=x+1))
    done
done
