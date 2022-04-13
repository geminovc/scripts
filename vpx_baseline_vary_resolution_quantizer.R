#!/usr/bin/env Rscript
# This script produces a timeseries of bitrate consumption 
# at different fps levels

library(ggplot2)
library(cowplot, warn.conflicts = FALSE)
library(scales)
library(sysfonts)
library(showtext)
library(showtextdb)
showtext_auto()

args <- commandArgs(trailingOnly=TRUE)
file <- "data/baseline_diff_resolutions"
plot_filename <- "pdfs/baseline_resolution_bitrate_tradeoff.pdf"
data<-read.csv(file)

bitrate_plot <- ggplot(data, aes(x=kbps,y=ssim,color=resolution,linetype=resolution)) + 
        geom_line(size=0.8) +

        labs(y="SSIM", y="Bitrate (Kbps)") +
        
        theme_minimal(base_size=15) +
        theme(axis.text.x=element_text(size=rel(1.0)), axis.text.y=element_text(size=rel(1.0))) +
        theme(legend.text=element_text(size=rel(0.9)), legend.key.size=unit(15,"points"), legend.position="top",
              legend.box.margin=margin(-10,-10,-10,-10), legend.margin=margin(c(0,0,0,0)))

ggsave(plot_filename, width=12.2,height=5)
