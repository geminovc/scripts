# uses a pickle file per celebrity with annotations on what
# square to cut and cuts all the input "temporally cropped" videos
# to that square, essentially spatially cropping them also

DIR=$1
speaker=$2
for phase in train test
do
    python3 crop_coordinates.py \
        --data-dir ${DIR}/${speaker} \
        --pickle-name ${DIR}/${speaker}/${speaker}_${phase}.pkl \
        --phase ${phase}
done
