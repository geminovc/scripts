DIR: Directory to save the data and meta data in, 
person: Clebritie's name
There should be a directory DIR/person available.

0. Annonate the videos from youtube for `person` with template urls in sample_urls and place train_urls.txt and test_urls,txt in `DIR/person`.
1. Run `bash download.sh DIR person`
2. Run `bash get_average_frame.sh DIR person`
3. Run `bash draw_bbox.sh DIR person` and find the best square by clicking on the image. Ctrl+a for choosing a square, Crtl+z for saving the current chosen square and going to next image 
4. Run `bash spatially_crop.sh DIR person`
5. Run `bash shorten_train.sh DIR person`
6. Run `bash recombine_test.sh DIR person`
7. Run `bash cleanup_script.sh DIR/person person`
8. Re-encode everything at 30fps by `bash reencode_at_30fps.sh DIR/person person`
9. Go through the videos for strange stuff
10. Run `find DIR/person -type f -name '*.DS_Store' -delete`
