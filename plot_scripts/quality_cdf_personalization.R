#!/usr/bin/env Rscript
# This script produces a cdf of per frame metrics 
# for the same video with different schemes

source("style.R")

args <- commandArgs(trailingOnly=TRUE)
file <- args[1]
plot_filename <- args[2] 
data<-read.csv(file)

label_list <- c(
                 "generic" = "Generic",
                 "personalization" = "Personalized")

line_list <- c(
                 "generic" = "dashed",
                 "personalization" = "solid")

color_list <- c(
                 "generic" = "#F8766D",
                 "personalization" = "#00B0F6")

breaks_list <- c("generic", "personalization")


ssim_plot <- ggplot(data) +
        stat_ecdf(aes(ssim_db,color=setting,linetype=setting), size=1) +  
        scale_color_manual(
                values = color_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=1)) +

        scale_linetype_manual(
                values = line_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=1)) +
        labs(x="SSIM (dB)", y="CDF") 
  
psnr_plot <- ggplot(data) +
        stat_ecdf(aes(psnr,color=setting,linetype=setting), size=1) + 
        labs(x="PSNR (dB)", y="CDF") + 

        scale_color_manual(
                values = color_list,
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
              legend.margin=margin(c(0,0,0,0))) 

lpips_plot <- ggplot(data) +
        stat_ecdf(aes(orig_lpips,color=setting,linetype=setting), size=1) + 
        scale_color_manual(
                values = color_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=1)) +

        scale_linetype_manual(
                values = line_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=1)) +
        labs(x="LPIPS", y="CDF") 

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
