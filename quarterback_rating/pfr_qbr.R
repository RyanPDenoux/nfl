library(tidyverse)

df <- read.csv(paste('data', 'pfr_qbr.csv', sep = '/'))
number_of_weeks <- 1:max(df$week)

for (i in number_of_weeks) {
  df.sorted <- df[df$week == i,]
  df.sorted <- df.sorted[order(df.sorted$passer_rating, decreasing = T), ]
  # score.to.beat <- df.sorted[df.sorted$player == 'Andy_Dalton', 'passer_rating']
  score.to.beat <- 100
  df.sorted$is_shit <- ifelse(df.sorted[ ,'passer_rating'] >= score.to.beat, 'Decent', 'Dog shit')
  df.sorted$is_shit[df.sorted$player == 'Andy Dalton'] <- 'Dalton'
  first.name <- paste('PFR_Week', i, 'distribution', sep = '_')
  second.name <- paste('PFR_Week', i, 'ratings', sep = '_')
  
  g1 <- ggplot(df.sorted) +
    geom_histogram(aes(passer_rating), bins = 12) + 
    xlab('Total Quarterback Rating') + ggtitle(paste('PFR Week', i, 'distribution'))
  ggsave(paste('results', paste(first.name, '.png', sep = ''), sep = '/'),
         plot = g1, width = 4, height = 3)
  
  g2 <- ggplot(df.sorted) + 
    geom_bar(aes(x = reorder(player, passer_rating), passer_rating, fill = is_shit),
             stat = 'identity') + 
    coord_flip() + 
    xlab('Total Quarterback Rating') + ggtitle(paste('PFR Week', i, 'ratings'))
  ggsave(paste('results', paste(second.name, '.png', sep = ''), sep = '/'),
         plot = g2, width = 5, height = 7)
}
