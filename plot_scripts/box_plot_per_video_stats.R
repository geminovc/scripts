#!/usr/bin/env Rscript
# This script produces a boxplot
# to show the distribution of visual metrics
# across a whole lot of videos grouped by people

source("style.R")

args <- commandArgs(trailingOnly=TRUE)
file <- args[1]
plot_filename <- args[2] 
data<-read.csv(file)

ssim_plot <- ggplot(data, aes(x=setting, y=ssim, color=person), size=1) + 
        geom_boxplot(outlier.size=1) + 
        theme(axis.text.x=element_blank(), axis.ticks.x=element_blank()) +
        labs(x="Video", y="SSIM") 
  

psnr_plot <- ggplot(data, aes(x=setting, y=psnr, color=person), size=1) + 
        geom_boxplot(outlier.size=1) + 
        labs(x="Video", y="PSNR (dB)") + 
        theme(axis.text.x=element_blank(), axis.ticks.x=element_blank()) +
        theme(legend.text=element_text(size=rel(1)), legend.key.size=unit(15,"points"), legend.position="none",
              legend.box.margin=margin(-10,-10,-10,-10), legend.title=element_blank(),
              legend.margin=margin(c(0,0,0,0))) 

lpips_plot <- ggplot(data, aes(x=setting, y=lpips, color=person), size=1) + 
        geom_boxplot(outlier.size=1) + 
        theme(axis.text.x=element_blank(), axis.ticks.x=element_blank()) +
        labs(x="Video", y="LPIPS") 

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
