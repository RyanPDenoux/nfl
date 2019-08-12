library(tidyverse)

df <- read.csv(paste('data', 'espn_qbr.csv', sep = '/'))
number_of_weeks <- 1:max(df$week)

for (i in number_of_weeks) {
  df.sorted <- df[df$week == i,]
  df.sorted <- df.sorted[order(df.sorted$raw_qbr, decreasing = T), ]
  # score.to.beat <- df.sorted[df.sorted$player == 'Andy_Dalton', 'raw_qbr']
  score.to.beat <- 60
  df.sorted$is_shit <- ifelse(df.sorted[ ,'raw_qbr'] >= score.to.beat, 'Decent', 'Dog shit')
  df.sorted$is_shit[df.sorted$player == 'Andy_Dalton'] <- 'Dalton'
  first.name <- paste('ESPN_Week', i, 'distribution', sep = '_')
  second.name <- paste('ESPN_Week', i, 'ratings', sep = '_')
  
  g1 <- ggplot(df.sorted) +
    geom_histogram(aes(raw_qbr), bins = 12) + 
    xlab('Raw Quarterback Rating') + ggtitle(paste('ESPN Week', i, 'distribution'))
  ggsave(paste('results', paste(first.name, '.png', sep = ''), sep = '/'),
         plot = g1, width = 4, height = 3)
  
  g2 <- ggplot(df.sorted) + 
    geom_bar(aes(x = reorder(player, raw_qbr), raw_qbr, fill = is_shit),
             stat = 'identity') + 
    coord_flip() + 
    xlab('Raw Quarterback Rating') + ggtitle(paste('ESPN Week', i, 'ratings'))
  ggsave(paste('results', paste(second.name, '.png', sep = ''), sep = '/'),
         plot = g2, width = 5, height = 7)
}

df.model <- lm(raw_qbr ~ pts_added +
                 pass +
                 run +
                 penalty +
                 total_epa +
                 qb_plays,
               df)
summary(df.model)
