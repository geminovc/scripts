#!/usr/bin/env Rscript
# This script compares quality bpp for all schemes

source("style.R")

args <- commandArgs(trailingOnly=TRUE)
file <- "../data/main_experiment_with_vp9/summary.csv"
plot_filename <- "pdfs/main_experiment_with_vp9_zoomed_in.pdf"
data<-read.csv(file)

label_list <- c(
                 "bicubic" = "Bicubic",
                 "vp9_bicubic" = "Bicubic (VP9)",
                 "ours" = "Gemino",
                 "SwinIR" = "SwinIR",
                 "fomm" = "FOMM")


shape_list <- c(
                 "bicubic" = 8,
                 "vp9_bicubic" = 17,
                 "ours" = 16,
                 "SwinIR" = 20,
                 "fomm" = 17)

line_list <- c(
                 "bicubic" = "dashed",
                 "vp9_bicubic" = "dotdash",
                 "ours" = "solid",
                 "SwinIR" = "dotted",
                 "fomm" = "blank")

color_list <- c(
                 "SwinIR" = "#A3A500",
                 "vp9_bicubic" = "#7570B3",
                 "bicubic" = "#F8766D",
                 "ours" = "#00B0F6",
                 "fomm" = "#E76BF3")


breaks_list <- c("bicubic", "vp9_bicubic", "SwinIR", "fomm", "ours")

ssim_plot <- ggplot(data, aes(x=kbps,y=ssim_db,color=approach,linetype=approach, shape=approach)) + 
        geom_line(size=1) +
        geom_point(size=3) +
        #geom_errorbar(aes(ymin=ssim_db-ssim_db_sd, ymax=ssim_db+ssim_db_sd), width=.2) +
        xlim(0, 200) + 
        
        scale_color_manual(
                values = color_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=1)) +

        scale_shape_manual(
                values=shape_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=1)) +

        scale_linetype_manual(
                values = line_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=1)) +


        labs(y="SSIM (dB)", x="Kbps") 
ggsave(plot_filename, width=12.2,height=5)
  
psnr_plot <- ggplot(data, aes(x=kbps,y=psnr,color=approach,linetype=approach, shape=approach)) + 
        geom_line(size=1) +
        geom_point(size=3) +
        #geom_errorbar(aes(ymin=psnr-psnr_sd, ymax=psnr+psnr_sd), width=.2) +
        xlim(0, 200) +  

        scale_color_manual(
                values = color_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=1)) +

        scale_shape_manual(
                values=shape_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=1)) +

        scale_linetype_manual(
                values = line_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=1)) +


        theme(legend.text=element_text(size=rel(1)), legend.key.size=unit(15,"points"), legend.position="none",
              legend.box.margin=margin(-10,-10,-10,-10), legend.title=element_blank(),
              legend.margin=margin(c(0,0,0,0))) + 
        labs(y="PSNR (dB)", x="Kbps") 

lpips_plot <- ggplot(data, aes(x=kbps,y=orig_lpips,color=approach,linetype=approach, shape=approach)) + 
        geom_line(size=1) +
        geom_point(size=3) + 
        #geom_errorbar(aes(ymin=orig_lpips-orig_lpips_sd, ymax=orig_lpips+orig_lpips_sd), width=.2) +
        xlim(0, 200) +

        scale_color_manual(
                values = color_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=1)) +

        scale_shape_manual(
                values=shape_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=1)) +

        scale_linetype_manual(
                values = line_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=1)) +

        labs(y="LPIPS", x="Kbps") 
 

legend <- get_legend(psnr_plot + theme(legend.position="top"))


prow <- plot_grid(ssim_plot + theme(legend.position="none"),
                  psnr_plot + theme(legend.position="none"),
                  lpips_plot + theme(legend.position="none"),
                  ncol = 3, align = "v", axis = "l")

# this tells it what order to put it in
# so basically tells it put legend first then plots with th legend height 20% of the
# plot
p <- plot_grid(legend, prow, rel_heights=c(.2,1), ncol =1)

ggsave(plot_filename, width=12.2, height=5)
