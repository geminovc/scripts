library(ggplot2)
library(ggplot2)
library(cowplot, warn.conflicts = FALSE)
library(scales)
library(sysfonts)
library(showtext)
library(showtextdb)
showtext_auto()

ggplot <- function(...) ggplot2::ggplot(...) + 
                        theme_bw() +
                        theme(panel.border = element_blank(), 
                              axis.line = element_line(colour = "black"), 
                              axis.line.x = element_line(), 
                              axis.line.y = element_line(),
			      axis.text = element_text(size = 24, color = "black"),
                              text = element_text(size = 24, family="serif"), 
                              axis.text.x = element_text(size = 16, color = "black"), 
                              axis.text.y = element_text(size = 16, color = "black"),
			      legend.key = element_blank(),
			      strip.background = element_blank(),
                              strip.text.x = element_blank(), 
                              strip.text.y = element_blank())
