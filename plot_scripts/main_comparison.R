#!/usr/bin/env Rscript
# This script compares quality bpp for all schemes

source("style.R")

args <- commandArgs(trailingOnly=TRUE)
file <- "data/aggregate_comparison_data"
plot_filename <- "pdfs/main_bpp_quality.pdf"
data<-read.csv(file)

ssim_plot <- ggplot(data, aes(x=kbps,y=ssim_db,color=setting,linetype=setting)) + 
        geom_line(size=0.8) +
        geom_point(size=2) +
        xlim(0, 1000) +  

        labs(y="SSIM (dB)", x="Kbps") 
ggsave(plot_filename, width=12.2,height=5)
  
psnr_plot <- ggplot(data, aes(x=kbps,y=psnr,color=setting,linetype=setting)) + 
        geom_line(size=0.8) +
        geom_point(size=2) +
        xlim(0, 1000) +  

        theme(legend.text=element_text(size=rel(1)), legend.key.size=unit(15,"points"), legend.position="none",
              legend.box.margin=margin(-10,-10,-10,-10), legend.title=element_blank(),
              legend.margin=margin(c(0,0,0,0))) + 
        labs(y="PSNR (dB)", x="Kbps") 

lpips_plot <- ggplot(data, aes(x=kbps,y=lpips,color=setting,linetype=setting)) + 
        geom_line(size=0.8) +
        geom_point(size=2) + 
        xlim(0, 1000) +  

        labs(y="LPIPS", x="Kbps") 
 

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
