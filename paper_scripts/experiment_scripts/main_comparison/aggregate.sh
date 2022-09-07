#!/bin/sh
# aggregate main comparison between bicubic, SinIR-LTE, Ours and VPX

cd ../../end2end_experiment
python aggregate_approach_comparison_data.py \
--data-paths /data4/pantea/nsdi_fall_2022/main_comparison/data/vpx_full_quantizer /data4/pantea/nsdi_fall_2022/main_comparison/data/ours_full_quantizer /data4/pantea/nsdi_fall_2022/main_comparison/data/swinir_lte_full_quantizer /data4/pantea/nsdi_fall_2022/main_comparison/data/bicubic_full_quantizer \
--settings VPX Ours SwinIR-LTE Bicubic \
--csv-name /data4/pantea/nsdi_fall_2022/main_comparison/data/aggregated_full_quantizer \
--columns-names setting kbps psnr ssim ssim_db orig_lpips \
