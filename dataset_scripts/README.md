# Generate videoconferencing datasets from youtube

## Collecting the videos

First, for each person make a directory:
```bash
mkdir <ROOT_DIR>/speaker
cd <ROOT_DIR>/speaker
```

In `speaker` folder, you need to make two text files:
```bash
touch urls_train.txt
touch urls_train.txt
```
These files contain the youtube url and the start and stop time of the video in `hour:minute:second` format. Example of the content of these files
is given in [here](https://github.mit.edu/NeTS/nets_scripts/tree/master/dataset_scripts/sample_urls):

```text
youtube_url,start_time,stop_time
https://youtu.be/SmDls15895I,00:02:37,00:05:37
```

Note that there is no extra space between elements in the text files and the files do not end with a new line. You can pick multiple start and stop times for a video. For the train videos, each of them will be treated as a separate video and cut into smaller sessions, but for the test videos they different sessions of the same video (same `youtube_url`) will be attached in the end to make a longer test video. Make sure to use the correct resolution when you are seaching for the videos.

The process of collecting the videos is time-consuming. I also suggest to use private mode in the browser if you don't want to mess up with your feeds:) The list of the `speaker`s that I used is:

```
"tucker", "xiran", "fancy_fueko", "seth_meyer", "kayleigh", "jen_psaki", "needle_drop", "trever_noah"
```

## Downloading the videos

To download the train and test videos use:
```bash
cd dataset_scripts
bash download.sh <ROOT_DIR> speaker
```
The output videos will be saved in `<ROOT_DIR>/speaker/original_youtube/{train, test}`. 

## Getting the average frame
Next, we generates the average frame for each video to find a crop box for each of the orignal videos. To get the average frames, run:
```bash
bash get_average_frame.sh <ROOT_DIR> speaker
```
The output average frames will be saved in `<ROOT_DIR>/speaker/averages/{train, test}`. 

## Draw the bounding boxes

In this part, we draw the bounding boxes on the average frames and record the box coordinates: 
```bash
bash draw_bbox.sh <ROOT_DIR> speaker <resolution>
```
After running this, python will pop up the average frames of `speaker` both in the test and train folders, and you can choose the top-left corner of the box you want to crop. You can modify your box selection multiple times. The title of the pop-up image will show the height and width of the box you have chosen. For a square box, you want both of these values to be equal to resolution, so be careful with choosing your box corners. After choosing your box, press `'a'` to record the coordinates of the box. 

All the coordinates will be saved in `<ROOT_DIR>/speaker/speaker_{train, test}.pkl`. Make sure this file does not exists if you want to rerun the `draw_bbox.sh`. 

## Crop the videos

Now, we crop the videos based on the useing the pickle file per speaker with annotations on what square to cut and cuts
