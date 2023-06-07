#!/usr/bin/env Rscript
# This script produces a cdf of per frame metrics 
# for the same video with different schemes

source("style.R")

args <- commandArgs(trailingOnly=TRUE)
file1 <- args[1]
file2 <- args[2]
plot_filename <- args[3] 
data1<-read.csv(file1)
data2<-read.csv(file2)

label_list <- c(
                 "pure_upsampling" = "Pure Upsampling",
                 #"fomm_skip_connections_lr_in_decoder" = "Conditional SR w/ warped HR",
                 #"sme_3_pathways_with_occlusion" = "Gemino w/ RGB-based warping",
                 "fomm_3_pathways_with_occlusion" = "Gemino")

line_list <- c(
                 "pure_upsampling" = "dashed",
                 #"fomm_skip_connections_lr_in_decoder" = "dotted",
                 #"sme_3_pathways_with_occlusion" = "twodash",
                 "fomm_3_pathways_with_occlusion" = "solid")

color_list <- c(
                 #"fomm_skip_connections_lr_in_decoder" = "#A3A500",
                 #"sme_3_pathways_with_occlusion" = "#E76BF3",
                 "pure_upsampling" = "#F8766D",
                 "fomm_3_pathways_with_occlusion" = "#00B0F6")


breaks_list <- c("pure_upsampling", 
                 #"fomm_skip_connections_lr_in_decoder", 
                 #"sme_3_pathways_with_occlusion",
                 "fomm_3_pathways_with_occlusion")

frames_plot <- ggplot(data1) +
        stat_ecdf(aes(orig_lpips,color=setting,linetype=setting), size=1) + 
        scale_color_manual(
                values = color_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=2)) +

        scale_linetype_manual(
                values = line_list,
                labels=label_list,
                breaks=breaks_list,
                guide=guide_legend(title=NULL, nrow=2)) +

        labs(x="LPIPS", y="CDF (across frames)") 

videos_plot <- ggplot(data2) +
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
        labs(x="LPIPS", y="CDF (across videos)") +
        theme(legend.text=element_text(size=unit(25,"points")), legend.key.size=unit(15,"points"), legend.position="none",
              legend.box.margin=margin(-10,-10,-10,-10), legend.title=element_blank(),
              legend.margin=margin(c(0,0,0,0))) 

legend <- get_legend(videos_plot + theme(legend.position="top"))


prow <- plot_grid(frames_plot + theme(legend.position="none"),
                  videos_plot + theme(legend.position="none"),
                  ncol = 2, align = "v", axis = "l")

# this tells it what order to put it in
# so basically tells it put legend first then plots with th legend height 20% of the
# plot
p <- plot_grid(legend, prow, rel_heights=c(.2,1), ncol =1)

ggsave(plot_filename, width=12.2, height=5)
