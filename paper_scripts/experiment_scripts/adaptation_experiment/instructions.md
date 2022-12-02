### Key Instructions for Running Adaptation Experiments ###
First, modify all the paths to point to your local directories.

In the `aiortc` codebase, this is in the first line of `src/aiortc/contrib/cached_models.py`.
In experiment scripts, for  `ours_perfect.sh` and `vpx_perfect.sh`, change the `nets_scripts_dir`, `aiortc_dir`, and `save_prefix`. Make sure that all intermediary directories for the `save_prefix` exist.

All logs go to the `save_prefix`. You might have a few levels of indirections, but keep going until the last parent folder with the logs, frames, and graphs.

Increasing the duration of the experiment may not always result in additional frames being processed because of consent expiration issue. One hack for now is to modify the ice consent failure threshold. To run 1mbps experiments, Vibhaa used the following in `/video-conf/scratch/vibhaa/.conda/envs/vibhaa-new-nets-fom/lib/python3.8/site-packages/aioice-0.7.6-py3.8.egg/aioice/ice.py` (Path depends on your installation):
```python
CONSENT_FAILURES=40
CONSENT_INTERVAL=10
```
Make sure to recompile aiortc with this change by running `python setup.py install` from the `aiortc` directory.

If you want to regenerate plots without rerunning the video, add `--just-aggregate` to the first command in `ours_perfect.sh` and `vpx_perfect.sh`. 

A good idea is to just run the model using `python run.py ...` to make sure you have the necessary dependencies. If the end-to-end adaptation experiment works as intended, you will see output lines with `Predicted! 0`, `Predicted! 1000`, and so on for Gemino. For VPX, corresponding `Displayed! 0` lines will show up. 

The relevant graphs are `bitrates_using_encoder_lr_video_sender_w1000_ms.png`, and `bitrates_using_encoder_video_sender_w1000_ms.png` for Gemino and VPX respectively. Make sure they look as desired.

If they do, you can use `aggregate_adaptation_results.py` in `post_experiment_process`, and `plot_scripts/adaptation_facet.R` to process the data and plot it. Full command examples can be found in `paper_scripts/experiment_scripts/ml_pipeline_aggregating_and_plotting.sh` on the `master` branch.
