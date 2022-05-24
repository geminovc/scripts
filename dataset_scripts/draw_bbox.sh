# Draw the bounding boxes on the average frames and record the box coordinates

DIR=$1
speaker=$2
resolution=$3
for phase in train test
do
	python3 ds_bbox_ui.py --folder ${DIR}/${speaker} \
	--name ${speaker} --resolution ${resolution} --phase $phase
done
