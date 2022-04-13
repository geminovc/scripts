#!/usr/bin/env Rscript
# This script produces a timeseries of bitrate consumption 
# at different fps levels

source("style.R")

args <- commandArgs(trailingOnly=TRUE)
file <- "data/baseline_diff_resolutions"
plot_filename <- "pdfs/baseline_resolution_bitrate_tradeoff.pdf"
data<-read.csv(file)
data$resolution <-factor(data$resolution, levels = c("256x256", "512x512", "1024x1024"))

ssim_plot <- ggplot(data, aes(x=bpp,y=ssim,color=resolution,linetype=resolution)) + 
        geom_line(size=0.8) +
        geom_point(size=2) + 

        labs(y="SSIM", x="Bits-per-pixel") 
ggsave(plot_filename, width=12.2,height=5)
  
psnr_plot <- ggplot(data, aes(x=bpp,y=psnr,color=resolution,linetype=resolution)) + 
        geom_line(size=0.8) +
        geom_point(size=2) +

        theme(legend.text=element_text(size=rel(1)), legend.key.size=unit(15,"points"), legend.position="none",
              legend.box.margin=margin(-10,-10,-10,-10), legend.title=element_blank(),
              legend.margin=margin(c(0,0,0,0))) + 
        labs(y="PSNR (dB)", x="Bits-per-pixel") 

lpips_plot <- ggplot(data, aes(x=bpp,y=lpips,color=resolution,linetype=resolution)) + 
        geom_line(size=0.8) +
        geom_point(size=2) + 

        labs(y="LPIPS", x="Bits-per-pixel") 
 

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
