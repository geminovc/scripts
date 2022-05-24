# Download the youtube videos based on the urls, start, and stop times in urls_path
# DIR is the base directory where the datasets is being stored
# speaker is the name of the speaker

DIR=$1
speaker=$2
for phase in train test
do
    python3 download_from_youtube.py \
    --output_folder ${DIR}/${speaker}/original_youtube/${phase} \
    --urls_path ${DIR}/${speaker}/urls_${phase}.txt 
done
