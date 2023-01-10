res=128
bitrates="15" #Kbps
input_base="/video-conf/scratch/pantea/fom_personalized_1024"
output_base="/video-conf/scratch/vibhaa_tardy/vp9_dataset/"
for data_type in "test" "train";
do
    for speaker in "xiran" "needle_drop" # "adam_neely" "fancy_fueko" "kayleigh" "needle_drop" "xiran";
    do 
        for v in ${input_base}/${speaker}/${data_type}/*;
        do
            output_prefix="${output_base}/${speaker}/${res}/${data_type}"
            mkdir -p ${output_prefix}

            v_base="$(basename -- $v)"
            resized_y4m="${v_base}_${res}.y4m"
            ffmpeg -i ${v} -vf scale=${res}:${res} -sws_flags bilinear ${resized_y4m}

            for bitrate in ${bitrates};
            do
                output="${output_prefix}/${v_base}_${bitrate}K.webm"

                vpxenc \
                    --webm \
                    --codec=vp9 \
                    --rt \
                    --passes=1 \
                    --threads=2 \
                    --cpu-used=7 \
                    --end-usage=cbr \
                    --target-bitrate=${bitrate} \
                    --buf-initial-sz=500 \
                    --buf-optimal-sz=600 \
                    --buf-sz=1000 \
                    --lag-in-frames=0 \
                    --disable-kf \
                    --static-thresh=0 \
                    --min-q=2 \
                    --max-q=52 \
                    --resize-allowed=0 \
                    --undershoot-pct=50 \
                    --overshoot-pct=50 \
                    -o ${output} ${resized_y4m}
            done
            rm ${resized_y4m}
        done
    done
done


