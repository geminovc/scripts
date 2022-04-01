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
file <- args[1]
plot_filename <- args[2]
data<-read.csv(file)
data$speed <- factor(data$speed)

bitrate_plot <- ggplot(data, aes(x=frame_frequency,y=bitrate,color=speed,linetype=deadline,shape=speed)) + 
        geom_line(size=0.8) +
        geom_point(size=2) + 

        labs(x="Frame Selection Frequency", y="Bitrate (Kbps)") +
        #ylim(0, 1500) +
        
        theme_minimal(base_size=15) +
        theme(axis.text.x=element_text(size=rel(1.0)), axis.text.y=element_text(size=rel(1.0))) +
        theme(legend.text=element_text(size=rel(0.9)), legend.key.size=unit(15,"points"), legend.position="top",
              legend.box.margin=margin(-10,-10,-10,-10), legend.margin=margin(c(0,0,0,0)))

ggsave(plot_filename, width=12.2,height=5)
