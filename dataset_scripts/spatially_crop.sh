# uses a pickle file per celebrity with annotations on what
# square to cut and cuts all the input "temporally cropped" videos
# to that square, essentially spatially cropping them also

DIR="/Users/panteababaahmadi/Documents/GitHub/nets_meta/youtube_dataset/dataset"
for speaker in "tucker" #"jen_psaki" #"xiran" # "fancy_fueko" "seth_meyer" "tucker" #"kayleigh" "trever_noah"
do
    for phase in train test
    do
        python3 crop_coordinates.py \
            --data-dir ${DIR}/${speaker} \
            --pickle-name ${DIR}/${speaker}/${speaker}_${phase}.pkl \
            --phase ${phase}
    done
done
