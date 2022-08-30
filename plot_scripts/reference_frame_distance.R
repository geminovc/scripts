#!/usr/bin/env Rscript
# This script produces a cdf of per frame metrics 
# for the same video with different schemes

source("style.R")

args <- commandArgs(trailingOnly=TRUE)
file <- args[1]
plot_filename <- args[2] 
data<-read.csv(file)
data$video <- as.factor(data$video)
data <- data[data$video == "5", ]
lo <- 1
hi <- 10000

ssim_plot <- ggplot(data[data$frame > lo & data$frame < hi, ], aes(x=frame, y=ssim)) +
        geom_line(aes(colour=video)) + 
        labs(x="Frame ID", y="SSIM") +
        theme(legend.text=element_text(size=rel(1)), legend.key.size=unit(15,"points"), legend.position="top",
              legend.box.margin=margin(-10,-10,-10,-10), legend.title=element_blank(),
              legend.margin=margin(c(0,0,0,0))) 

dist_plot <- ggplot(data[data$frame > lo & data$frame < hi, ], aes(x=frame, y=dist)) +
        geom_line(aes(colour=video)) +
        labs(x="Frame ID", y="Distance") +
        theme(legend.text=element_text(size=rel(1)), legend.key.size=unit(15,"points"), legend.position="top",
              legend.box.margin=margin(-10,-10,-10,-10), legend.title=element_blank(),
              legend.margin=margin(c(0,0,0,0))) 

p <- plot_grid(dist_plot, ssim_plot, rel_heights=c(1,1), ncol =1)
ggsave(plot_filename, width=12.2, height=5)
