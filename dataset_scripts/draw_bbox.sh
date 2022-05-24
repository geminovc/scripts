# Draw the bounding boxes on the average and record the box coordinates

DIR=$1
speaker=$2
for phase in train test
do
	python3 ds_bbox_ui.py --folder ${DIR}/${speaker} \
	--name ${speaker} --resolution 512 --phase $phase
done
