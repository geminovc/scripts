# design section figure comparing FOMM and Gemino
python collect_results_from_ml_pipeline.py --approaches-to-compare design_model_comparison --base-dir-list /video-conf/scratch/vibhaa_lam2/final_results/model_comparisons  --person-list kayleigh xiran needle_drop fancy_fueko adam_neely  --people-for-strip kayleigh xiran adam_neely --save-prefix ../data/model_design_comparison --csv-name summary.csv --img-width 1024 --video-num 2 --frame-num 2006 --summarize

# main plot
python collect_results_from_ml_pipeline.py --approaches-to-compare main_exp:fomm main_exp:vpx main_exp:bicubic main_exp:SwinIR main_exp:ours --base-dir-list /video-conf/scratch/vibhaa_lam2/final_results/model_comparisons /video-conf/scratch/pantea_tardy/final_results/vpx /video-conf/scratch/pantea_tardy/final_results/bicubic /video-conf/scratch/pantea_tardy/final_results/swinir /video-conf/scratch/vibhaa_tardy/final_results/training_with_encoder/ --person-list kayleigh xiran needle_drop fancy_fueko adam_neely  --people-for-strip kayleigh xiran needle_drop fancy_fueko --save-prefix ../data/main_experiment --csv-name summary.csv --img-width 1024 --video-num 4 --frame-num 2006 --summarize
./main_comparison.R
./main_comparison_zoomed_in.R

# main exp cdf
python collect_results_from_ml_pipeline.py --approaches-to-compare main_exp:fomm main_exp:vpx main_exp:bicubic main_exp:SwinIR main_exp:ours --base-dir-list /video-conf/scratch/vibhaa_lam2/final_results/model_comparisons /video-conf/scratch/pantea_tardy/final_results/vpx /video-conf/scratch/pantea_tardy/final_results/bicubic /video-conf/scratch/pantea_tardy/final_results/swinir /video-conf/scratch/vibhaa_tardy/final_results/training_with_encoder/ --person-list kayleigh xiran needle_drop fancy_fueko adam_neely  --people-for-strip kayleigh xiran needle_drop fancy_fueko --save-prefix ../data/main_experiment --csv-name frame_cdf.csv --img-width 1024 --video-num 4 --frame-num 2006 --cdf
./quality_cdf_main_exp.R ../data/main_experiment/frame_cdf.csv pdfs/main_experiment_per_frame_cdf.pdf

# resolution experiments
python collect_results_from_ml_pipeline.py --approaches-to-compare resolution_comparison --base-dir-list /video-conf/scratch/vibhaa_tardy/final_results/training_with_encoder/ --person-list kayleigh needle_drop fancy_fueko xiran adam_neely --people-for-strip kayleigh xiran needle_drop --save-prefix ../data/resolution_comparison --csv-name summary.csv --img-width 1024 --video-num 2 --frame-num 2006 --summarize

# encoder effect
python collect_results_from_ml_pipeline.py --approaches-to-compare encoder_in_training --base-dir-list /video-conf/scratch/vibhaa_lam2/final_results/encoder_effect  --person-list kayleigh xiran adam_neely fancy_fueko needle_drop --people-for-strip adam_neely xiran kayleigh --save-prefix ../data/encoder_effect --csv-name summary.csv --img-width 1024 --video-num 2 --frame-num 1952 --summarize

# model ablation
python collect_results_from_ml_pipeline.py --approaches-to-compare model_ablation --base-dir-list /video-conf/scratch/vibhaa_lam2/final_results/model_comparison_with_encoder  --person-list kayleigh xiran fancy_fueko needle_drop adam_neely  --people-for-strip kayleigh needle_drop xiran --save-prefix ../data/model_ablation_with_encoder --csv-name summary.csv --img-width 1024 --video-num 2 --frame-num 839 --summarize

# model ablation cdf
python collect_results_from_ml_pipeline.py --approaches-to-compare model_ablation --base-dir-list /video-conf/scratch/vibhaa_lam2/final_results/model_comparison_with_encoder  --person-list kayleigh xiran fancy_fueko needle_drop adam_neely  --people-for-strip kayleigh needle_drop xiran --save-prefix ../data/model_ablation_with_encoder --csv-name video_cdf.csv --img-width 1024 --video-num 2 --frame-num 839 --cdf --per-video
python collect_results_from_ml_pipeline.py --approaches-to-compare model_ablation --base-dir-list /video-conf/scratch/vibhaa_lam2/final_results/model_comparison_with_encoder  --person-list kayleigh xiran fancy_fueko needle_drop adam_neely  --people-for-strip kayleigh needle_drop xiran --save-prefix ../data/model_ablation_with_encoder --csv-name frame_cdf.csv --img-width 1024 --video-num 2 --frame-num 839 --cdf
./quality_cdf_model_ablation.R ../data/model_ablation_with_encoder/frame_cdf.csv ../data/model_ablation_with_encoder/video_cdf.csv pdfs/model_ablation_combined_videos_frames_cdf.pdf


# personalization effect (both strip and table)
python collect_results_from_ml_pipeline.py --approaches-to-compare personalization --base-dir-list /video-conf/scratch/vibhaa_mm_log_directory/personalization/  --person-list kayleigh jen_psaki trevor_noah seth_meyers needle_drop --people-for-strip needle_drop seth_meyers jen_psaki --save-prefix ../data/personalization --csv-name summary.csv --img-width 512 --video-num 2 --frame-num 1952 --summarize

# adaptation experiment
python aggregate_adaptation_results.py --save-prefix ../data/adaptation --approaches-to-compare vpx ours --base-dir-list /data4/pantea/nsdi_fall_2022/adaptation/final_results/vpx_everything_comparison_perfect_estimator_shrinked_trace/resolution1024x1024/needle_drop/1.mp4/quantizer-1/vpx_min550000_default550000_max550000bitrate/run0/ /data4/pantea/nsdi_fall_2022/adaptation/final_results/ours_everything_comparison_perfect_estimator_shrinked_trace/needle_drop/1.mp4/lrquantizer-1/quantizer32/run0/
./adaptation_facet.R

