# generates the average frame to drop a crop box on for each of the original
# videos for the specified speakers
# from the sppech to gesture dataset

DIR="/Users/panteababaahmadi/Documents/GitHub/nets_meta/youtube_dataset/dataset"
for speaker in "tucker" #"jen_psaki" # "xiran" #"fancy_fueko" "seth_meyer" "tucker" #"kayleigh" "trever_noah"
do
	for phase in train test
	do
	    mkdir -p ${DIR}/${speaker}/averages/${phase}
	    for file in ${DIR}/${speaker}/original_youtube/${phase}/*
	    do
	        filename=$(basename "$file")
	        fbname=${filename%%.*}
	        echo $fbname
	        python3 get_average.py $file ${DIR}/${speaker}/averages/${phase}/${fbname}.jpg
	    done
	done
done
