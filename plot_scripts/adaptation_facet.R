#!/usr/bin/env Rscript
# This script compares quality bpp for all schemes

source("style.R")

args <- commandArgs(trailingOnly=TRUE)
file <- "../data/adaptation/summary.csv"
plot_filename <- "pdfs/adaptation.pdf"
data<-read.csv(file)
data<- data[data$time < 220,]

label_list <- c(
                 "vpx" = "VP8 (Chromium)",
                 "ours" = "Gemino",
                 "target" = "Target"
                )


line_list <- c(
                 "vpx" = "twodash",
                 "ours" = "solid",
                 "target" = "dotted"
                )

color_list <- c(
                 "vpx" = "#00BF7D",
                 "ours" = "#00B0F6",
                 "target" = "black"
               )


breaks_list <- c("vpx", "ours", "target")

bitrate_plot <- ggplot(data, aes(x=time,y=total_video_bitrates,color=approach,linetype=approach)) + 
        geom_line(size=1) +
        
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
              legend.margin=margin(c(0,0,0,0)), axis.title.x=element_blank()) + 

        labs(y="Bitrate (Kbps)", x="Time (s)") 
  
lpips_plot <- ggplot(data[data$approach != 'target', ], aes(x=time,y=lpips,color=approach,linetype=approach)) + 
        geom_line(size=0.8) +

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

        labs(y="LPIPS", x="Time (s)") 
 
legend <- get_legend(bitrate_plot + theme(legend.position="top"))

p <- plot_grid(legend,
               bitrate_plot + theme(legend.position="none"), 
               lpips_plot + theme(legend.position="none"),
               ncol = 1, nrow=3, rel_heights=c(.2, 1, 1))

ggsave(plot_filename, width=6.2, height=5)
