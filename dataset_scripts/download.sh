DIR="/Users/panteababaahmadi/Documents/GitHub/nets_meta/youtube_dataset/dataset"
for speaker in  "tucker" #"xiran" #"fancy_fueko" #"seth_meyer" "tucker" #"fancy_fueko" #"kayleigh" "jen_psaki"
do
	for phase in train test
	do
	    # Download the videos
	    python3 download_from_youtube.py --output_folder ${DIR}/${speaker}/original_youtube/${phase} --urls_path ${DIR}/${speaker}/urls_${phase}.txt 

	done
done


