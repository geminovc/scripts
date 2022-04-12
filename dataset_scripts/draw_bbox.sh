# generates the average frame to drop a crop box on for each of the original
# videos for the specified speakers
# from the sppech to gesture dataset

DIR="/Users/panteababaahmadi/Documents/GitHub/nets_meta/youtube_dataset/dataset"
for speaker in "needle_drop" #"jen_psaki" #"xiran" # "fancy_fueko" "seth_meyer" "tucker" #"trever_noah" "kayleigh"
do
	for phase in train test
	do
    	python3 ds_bbox_ui.py --folder ${DIR}/${speaker} --name ${speaker} --resolution 512 --phase $phase
    done
done
