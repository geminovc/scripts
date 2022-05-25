#!/bin/sh
# useful for generating strips for presentations by taking videos
# from https://drive.google.com/drive/folders/1O0viPTI-az_pW8fyKaC5x8DaxuamsE7K
# and extracting the corresponding subframes
# to produce a source | target | method1 | method2..
person=$1

ffmpeg -y -i ${person}_src.jpg -filter:v "crop=1024:1024:0:0" ${person}_source.jpg
ffmpeg -y -i ${person}.jpg -filter:v "crop=1024:1024:0:0" ${person}_target.jpg
ffmpeg -y -i ${person}.jpg -filter:v "crop=1024:1024:1024:0" ${person}_fom_standard.jpg
ffmpeg -y -i ${person}.jpg -filter:v "crop=1024:1024:4096:0" ${person}_hr_skip.jpg

ffmpeg -y -i ${person}_source.jpg -i ${person}_target.jpg \
    -i ${person}_fom_standard.jpg -i ${person}_hr_skip.jpg \
    -filter_complex "[0][1][2][3]hstack=inputs=4" ${person}_strip.jpg

rm ${person}_source.jpg ${person}_target.jpg \
    ${person}_fom_standard.jpg ${person}_hr_skip.jpg
