#!/usr/bin/env Rscript
# This script compares quality bpp for all schemes

source("style.R")

args <- commandArgs(trailingOnly=TRUE)
file <- "../data/full_comparison_with_vp9_after_recalibrating/wrangled_summary.csv"
plot_filename <- "pdfs/full_comparison_with_vp9_after_recalibrating_with_break.pdf"
data<-read.csv(file)

label_list <- c(
                 "vpx" = "VP8 (Chromium)",
                 "bicubic" = "Bicubic",
                 "vp9_bicubic" = "Bicubic (VP9)",
                 "ours" = "Gemino",
                 "SwinIR" = "SwinIR",
                 "vp9" = "VP9",
                 "fomm" = "FOMM")


shape_list <- c(
                 "vpx" = 15,
                 "bicubic" = 8,
                 "vp9_bicubic" = 8,
                 "ours" = 16,
                 "SwinIR" = 20,
                 "vp9" = 18,
                 "fomm" = 17)

line_list <- c(
                 "vpx" = "twodash",
                 "bicubic" = "dashed",
                 "vp9_bicubic" = "twodash",
                 "ours" = "solid",
                 "SwinIR" = "dotted",
                 "vp9" = "twodash",
                 "fomm" = "blank")

color_list <- c(
                 "vpx" = "#00BF7D",
                 "SwinIR" = "#A3A500",
                 "bicubic" = "#F8766D",
                 "vp9_bicubic" = "#000000",
                 "vp9" = "#bf5b17",
                 "ours" = "#00B0F6",
                 "fomm" = "#E76BF3")


breaks_list <- c("vpx", "vp9", "bicubic", "vp9_bicubic", "SwinIR", "fomm", "ours")

ssim_plot <- ggplot(data, aes(x=kbps,y=ssim_db,color=approach,linetype=approach, shape=approach)) + 
        geom_line(size=1) +
        geom_point(size=3) +
        #geom_errorbar(aes(ymin=ssim_db-ssim_db_sd, ymax=ssim_db+ssim_db_sd), width=.2) +
        scale_x_continuous(breaks=seq(0,600,100), limits=c(0,600)) +
        
        scale_color_manual(
                values = color_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=2)) +

        scale_shape_manual(
                values=shape_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=2)) +

        scale_linetype_manual(
                values = line_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=2)) +
        scale_x_break(c(200, 500), scales=0.5, space=0.75) +
        
        annotate("segment", x = 580, xend = 520, y = 6, yend = 9,
           colour = "grey", size = 2, arrow = arrow()) +
        annotate("text", x = 572, y = 7.8, angle=305, size=5,
           colour = "grey", label="Better") +


        labs(y="SSIM (dB)", x="Kbps") 
  
psnr_plot <- ggplot(data, aes(x=kbps,y=psnr,color=approach,linetype=approach, shape=approach)) + 
        geom_line(size=1) +
        geom_point(size=3) +
        #geom_errorbar(aes(ymin=psnr-psnr_sd, ymax=psnr+psnr_sd), width=.2) +
        scale_x_continuous(breaks=seq(0,600,100), limits=c(0,600)) +
        scale_x_break(c(200, 500), scales=0.5, space=.75) +

        scale_color_manual(
                values = color_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=2)) +

        scale_shape_manual(
                values=shape_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=2)) +

        scale_linetype_manual(
                values = line_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=2)) +
        
        annotate("segment", x = 580, xend = 520, y = 20, yend = 25,
           colour = "grey", size = 2, arrow = arrow()) +
        annotate("text", x = 570, y = 23, angle=305, size=5,
           colour = "grey", label="Better") +


        theme(legend.text=element_text(size=rel(1)), legend.key.size=unit(15,"points"), legend.position="none",
              legend.box.margin=margin(-10,-10,-10,-10), legend.title=element_blank(),
              legend.margin=margin(c(0,0,0,0))) + 
        labs(y="PSNR (dB)", x="Kbps") 

lpips_plot <- ggplot(data, aes(x=kbps,y=orig_lpips,color=approach,linetype=approach, shape=approach)) + 
        geom_line(size=1) +
        geom_point(size=3) + 
        #geom_errorbar(aes(ymin=orig_lpips-orig_lpips_sd, ymax=orig_lpips+orig_lpips_sd), width=.2) +
        scale_x_continuous(breaks=seq(0,600,100), limits=c(0,600)) +
        scale_x_break(c(200, 500), scales=0.5, space=.75) +

        scale_color_manual(
                values = color_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=2)) +

        scale_shape_manual(
                values=shape_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=2)) +

        scale_linetype_manual(
                values = line_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=2)) +
        
        annotate("segment", x = 580, xend = 520, y = 0.38, yend = 0.31,
           colour = "grey", size = 2, arrow = arrow()) +
        annotate("text", x = 540, y = 0.37, angle=52, size=5,
           colour = "grey", label="Better") +

        labs(y="LPIPS", x="Kbps") 
 

legend <- get_legend(psnr_plot + theme(legend.position="top"))


prow <- plot_grid(print(ssim_plot + theme(legend.position="none")),
                  print(psnr_plot + theme(legend.position="none")),
                  print(lpips_plot + theme(legend.position="none")),
                  ncol = 3, align = "v", axis = "l")

# this tells it what order to put it in
# so basically tells it put legend first then plots with th legend height 20% of the
# plot
p <- plot_grid(legend, prow, rel_heights=c(.2,1), ncol =1)

ggsave(plot_filename, width=12.2, height=5)
