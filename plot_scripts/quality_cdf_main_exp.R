#!/usr/bin/env Rscript
# This script produces a cdf of per frame metrics 
# for the same video with different schemes

source("style.R")

args <- commandArgs(trailingOnly=TRUE)
file <- args[1]
plot_filename <- args[2]
metric <- args[3]
if (metric == "ssim_db") {
    metric_name <- "SSIM (dB)"
} else if (metric == "psnr") {
    metric_name <- "PSNR (dB)"
} else {
    metric_name <- "LPIPS"
}


data<-read.csv(file)

label_list <- c(
                 "bicubic" = "Bicubic (VP8)",
                 "ours" = "Gemino",
                 "SwinIR" = "SwinIR",
                 "vp9_bicubic" = "Bicubic (VP9)",
                 "fomm" = "FOMM")

line_list <- c(
                 "bicubic" = "dashed",
                 "ours" = "solid",
                 "SwinIR" = "dotted",
                 "vp9_bicubic" = "twodash",
                 "fomm" = "twodash")

color_list <- c(
                 "bicubic" = "#F8766D",
                 "ours" = "#00B0F6",
                 "SwinIR" = "#A3A500",
                 "vp9_bicubic" = "#000000",
                 "fomm" = "#E76BF3")


breaks_list <- c("bicubic", "SwinIR", "fomm", "ours", "vp9_bicubic")


first_plot <- ggplot(data[data$setting == 'lr128_tgt15Kb' | data$setting == 'lr256_tgt15Kb', ]) +
        stat_ecdf(aes_string(metric,color="approach",linetype="approach"), size=1) +
        ggtitle(metric_name) +

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
        labs(x="15 Kbps", y="CDF") 
  
second_plot <- ggplot(data[data$setting == 'lr256_tgt45Kb' | data$setting == 'fomm', ]) +
        stat_ecdf(aes_string(metric,color="approach",linetype="approach"), size=1) + 
        labs(x="45 Kbps", y="CDF") +

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

third_plot <- ggplot(data[data$setting == 'lr256_tgt75Kb'| data$setting == 'lr512_tgt75Kb', ]) +
        stat_ecdf(aes_string(metric,color="approach",linetype="approach"), size=1) + 
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
        labs(x="75 Kbps", y="CDF") 
    
fourth_plot <- ggplot(data[data$setting == 'lr256_tgt105Kb'| data$setting == 'lr512_tgt105Kb', ]) +
        stat_ecdf(aes_string(metric,color="approach",linetype="approach"), size=1) + 
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
        labs(x="105 Kbps", y="CDF") 

legend <- get_legend(first_plot + theme(legend.position="top"))
title <- get_title(first_plot + theme(plot.title = element_text(hjust = 0.5)))


prow <- plot_grid(first_plot + theme(legend.position="none", plot.title=element_blank()),
                  second_plot + theme(legend.position="none"),
                  third_plot + theme(legend.position="none"),
                  fourth_plot + theme(legend.position="none"),
                  ncol = 4, align = "v", axis = "l")

# this tells it what order to put it in
# so basically tells it put legend first then plots with th legend height 20% of the
# plot
p <- plot_grid(legend, prow, title, rel_heights=c(.2,1, .2), ncol =1) 

ggsave(plot_filename, width=15.5, height=5)
