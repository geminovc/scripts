#!/bin/sh
path="/video-conf/scratch/pantea/fom_personalized_1024"

for speaker in "xiran" "fancy_fueko" "needle_drop" "kayleigh";
do
    x=0
    for i in 1 2 3 4;
    do
        mkdir -p "${path}/${speaker}/validation/${x}"
        ffmpeg -ss 00:00:05.01 -i "${path}/${speaker}/test/${i}.mp4" \
            -frames:v 1 "${path}/${speaker}/validation/${x}/source.png" 
        ffmpeg -ss 00:01:13.01 -i "${path}/${speaker}/test/${i}.mp4" \
            -frames:v 1 "${path}/${speaker}/validation/${x}/target.png" 
        ((x=x+1))
        
        ffmpeg -ss 00:01:35.01 -i "${path}/${speaker}/test/${i}.mp4" \
            -frames:v 1 "${path}/${speaker}/validation/${x}/source.png" 
        ffmpeg -ss 00:00:20.01 -i "${path}/${speaker}/test/${i}.mp4" \
            -frames:v 1 "${path}/${speaker}/validation/${x}/source.png" 
        ((x=x+1))
    done
done
