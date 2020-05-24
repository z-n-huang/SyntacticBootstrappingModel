library(readr)
library(dplyr)
library(reshape2)
library(ggplot2)
library(tikzDevice)


setwd('..') # ADDED
# set ggplot2 theme

theme_set(theme_classic()+ theme(axis.line.x = element_line(colour = 'black', size=0.5, linetype='solid'),
                                 axis.line.y = element_line(colour = 'black', size=0.5, linetype='solid'),
                                 panel.grid.major = element_line(size = (0.2), colour="grey")
))

# load data
## English
suff = "22wnopen" # "10nopen" "10wpenall", "10wpensel"
#verbreps_results <- read_csv(paste("results/feb2020 draft/verbreps_resultsen ", suff, ".csv", sep = "")) #  w(/o) " 10wpen"
#projection_results <- read_csv(paste("results/feb2020 draft/projection_resultsen ", suff, ".csv", sep = ""))

v2 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10 en may19/verbreps_resultsen 5-15 1e0 2.csv")
v3 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10 en may19/verbreps_resultsen 5-15 1e0 3.csv")
v4 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10 en may19/verbreps_resultsen 5-15 1e0 4.csv")
v5 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10 en may19/verbreps_resultsen 5-15 1e0 5.csv")
v2$itr <- ifelse(v2$itr == 0, 2, 3)
v3$itr <- ifelse(v3$itr == 0, 4, 5)
v4$itr <- ifelse(v4$itr == 0, 6, 7)
v5$itr <- ifelse(v5$itr == 0, 8, 9)

verbreps_results <- rbind(
  v1 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10 en may19/verbreps_resultsen 5-15 1e0 1.csv"),
  v2, v3, v4, v5
)

p2 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10 en may19/projection_resultsen 5-15 1e0 2.csv")
p3 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10 en may19/projection_resultsen 5-15 1e0 3.csv")
p4 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10 en may19/projection_resultsen 5-15 1e0 4.csv")
p5 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10 en may19/projection_resultsen 5-15 1e0 5.csv")
p2$itr <- ifelse(p2$itr == 0, 2, 3)
p3$itr <- ifelse(p3$itr == 0, 4, 5)
p4$itr <- ifelse(p4$itr == 0, 6, 7)
p5$itr <- ifelse(p5$itr == 0, 8, 9)


projection_results <- rbind(
  read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10 en may19/projection_resultsen 5-15 1e0 1.csv"),
  p2, p3, p4, p5
)

read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10 en may19/verbreps_resultsen 5-15 1e0 1.csv")
verbreps_results <- read_csv("C:/Users/znhua/Documents/raspberry transfers/verbreps_resultsen 5e0.csv")
projection_results <- read_csv("C:/Users/znhua/Documents/raspberry transfers/projection_resultsen 5e0.csv")

gleason_data <- read_csv("data/gleason_data.csv")
verbreps_results <- verbreps_results %>% filter(verb != "IMPERATIVE" & verb!="DECLARATIVE")

## END LOADING ENGLISH

## Mandarin
suff = "wpeno" # "wnopen" "wnopen"
verbreps_results <- rbind(
  read_csv(paste("results/feb2020 draft/verbreps_resultsmc 22", suff, ".csv", sep = "")),
  read_csv(paste("results/feb2020 draft/verbreps_resultsmc 20", suff, ".csv", sep = "")),
  read_csv(paste("results/feb2020 draft/verbreps_resultsmc 10", suff, ".csv", sep = ""))
)
projection_results <- rbind(
  read_csv(paste("results/feb2020 draft/projection_resultsmc 22", suff, ".csv", sep = "")),
  read_csv(paste("results/feb2020 draft/projection_resultsmc 20", suff, ".csv", sep = "")),
  read_csv(paste("results/feb2020 draft/projection_resultsmc 10", suff, ".csv", sep = ""))
)

gleason_data <- read_csv("data/processedmc22.csv")
verbreps_results <- verbreps_results %>% filter(verb != "tell")
## END LOADING MANDARIN

# plot verb representations
repmeans <- group_by(verbreps_results, verb, sentence, child) %>% 
  summarise(belief=mean(`0`), desire=mean(`1`)) %>% filter(!((sentence%%10)>0))

repmeans.melt <- melt(repmeans, c('verb', 'sentence', 'child'))

repmeans.summ <- group_by(repmeans.melt, verb, variable, sentence) %>% 
  summarise(med=median(value), q25=quantile(value, .25), q75=quantile(value, .75), 
            q025=quantile(value, .025), q975=quantile(value, .975),
            qmin=min(value), qmax=max(value))

verb.counts <- count(gleason_data, verb, sort = T)
verb.counts <- filter(verb.counts, verb %in% unique(repmeans.summ$verb))

repmeans.summ$verb <- ordered(repmeans.summ$verb, levels=verb.counts$verb)

repmeans.summ$verbPlot <- recode(repmeans.summ$verb, 
                                 DECLARATIVE = "DECLARATIVE",
                                 IMPERATIVE = "IMPERATIVE",
                                 "要" = "yao 'want' (D)",
                                 "看" = "kan 'see' (B)", 
                                 "说" = "shuo 'say' (B)",
                                 "看看" = "kankan 'see-DUP' (B)", 
                                 "讲" = "jiang 'say' (B)",
                                 "想" = "xiang 'think, want' (B, D)", 
                                 "知道" = "zhidao 'know' (B)", 
                                 "叫" = "jiao 'call/get' (D)",
                                 "喜欢" = "xihuan 'like' (D)",  
                                 "告诉" = "gaosu 'tell' (B)", 
                                 "帮" = "bang 'help' (O)", 
                                 "让" = "rang 'let' (O)", 
                                 "觉得" = "juede 'feel' (B)",
                                 "want" = "want (D)", 
                                 "see" = "see (B)", 
                                 "know" = "know (B)", 
                                 "think" = "think (B)", 
                                 "say" = "say (B)",
                                 "like" = "like (D)",
                                 "tell" = "tell (B/D)", 
                                 "try" = "try (D)", 
                                 "need" = "need (D)", 
                                 "remember" = "remember (B)"
                  ) 

repmeans.summ <- repmeans.summ %>% filter(verbPlot != "<NA>")

#tikz('~/experiments/MainClauseModel/bin/verbrep_prob.tikz', width=5.5, height=4)
ggplot(repmeans.summ
       %>% filter(verbPlot != "vacuous-verb"
         & verbPlot != "IMPERATIVE" & verbPlot !="DECLARATIVE"
         & verbPlot != "bang 'help' (O)" & verbPlot != "rang 'let' (O)"
         & verbPlot != "kankan 'see-DUP' (B)"
       ), 
       aes(x=(sentence+1)*10, y=med, color = variable, fill = variable )) + # linetype=variable, 
  geom_ribbon(aes(ymin=qmin, ymax=qmax), alpha = 0.1, color = NA) +
  geom_ribbon(aes(ymin=q25, ymax=q75),  alpha = 0.3, color = NA) +
  #geom_ribbon(alpha=.05, aes(ymin=q025, ymax=q975)) +
  geom_line(size=1) + # color = black
  facet_wrap(~verbPlot, ncol = 5) + 
  scale_linetype(name='') +
  scale_x_continuous(name='Number of sentences seen (thousands)', breaks=c(0,10000,20000), labels=c('0', '10', '20')) +
  scale_y_continuous(name='Probability of semantic component') +
  scale_fill_hue(l=40) + # how light/dark the ribbon fill is
  scale_color_hue(l=40) + # how light/dark the line is
  theme(legend.title=element_blank()) # hide legend name
#dev.off()

### PART TWO: Probability of semantics vs. frequency of clausal complements
gleason_data$has.embpred <- gleason_data$embpred!='NONE' # English
gleason_data$has.embpred <- gleason_data$embpred!='FALSE' # MC version

emb.counts <- filter(gleason_data, verb %in% unique(repmeans.summ$verb)) %>%
  count(child, verb, has.embpred) %>% group_by(child, verb) %>% mutate(tot=sum(n), prop=n/tot)

repmeans.emb <- merge(filter(repmeans.melt, repmeans.melt$sentence==max(repmeans.melt$sentence)), 
                      emb.counts)

repmeans.emb$verb <- ordered(repmeans.emb$verb, levels=verb.counts$verb)

repmeans.emb.cast <- dcast(filter(repmeans.emb, has.embpred), child+verb+prop ~ variable, value.var = 'value')
repmeans.emb.cast$dorb <- 1-(1-repmeans.emb.cast$belief)*(1-repmeans.emb.cast$desire)

logistic <- function(p) log(p)-log(1-p)

repmeans.emb$verb <- recode(repmeans.emb$verb, 
                                DECLARATIVE = "DECLARATIVE",
                                IMPERATIVE = "IMPERATIVE",
                                "要" = "yao 'want' (D)",
                                "看" = "kan 'see' (B)", 
                                "说" = "shuo 'say' (B)",
                                "看看" = "kankan 'see-DUP' (B)", 
                                "讲" = "jiang 'say' (B)",
                                "想" = "xiang 'think, want' (B, D)", 
                                "知道" = "zhidao 'know' (B)", 
                                "叫" = "jiao 'call/get' (D)",
                                "喜欢" = "xihuan 'like' (D)",  
                                "告诉" = "gaosu 'tell' (B)", 
                                "帮" = "bang 'help' (O)", 
                                "让" = "rang 'let' (O)", 
                                "觉得" = "juede 'feel' (B)",
                                "want" = "want (D)", 
                                "see" = "see (B)", 
                                "know" = "know (B)", 
                                "think" = "think (B)", 
                                "say" = "say (B)",
                                "like" = "like (D)",
                                "tell" = "tell (B/D)", 
                                "try" = "try (D)", 
                                "need" = "need (D)", 
                                "remember" = "remember (B)"
                               ) 
                               

#tikz('~/experiments/MainClauseModel/bin/embclause_prob.tikz', width=5.5, height=4)
ggplot(filter(repmeans.emb %>% 
                filter(verb != "vacuous-verb"
                  & verb != "IMPERATIVE" & verb !="DECLARATIVE"
                  & verb != "bang 'help'" & verb != "rang 'let'"
                  & verb != "kankan 'see-DUP'"
      ), has.embpred), aes(x=prop, y=logistic(value), color = variable)) + 
  geom_point(size=1.5) +
  facet_wrap(~verb, ncol=5) + 
  scale_shape_manual(name='', values = c(16, 1)) +
  labs(color='Semantic\nfeature') + # legend name
  scale_x_log10(name='Proportion of sentences with embedded clause', 
                     breaks = c(0, 0.1, 0.5, 1), 
                     labels=c('~0', 0.1, 0.5, '~1'))+
  scale_y_continuous(name='Probability of semantic component', breaks=logistic(c(0.0001, 0.1, 0.5, 0.9, 0.9999)), labels=c('~0', 0.1, 0.5, 0.9, '~1'))# +
#theme(axis.text.x=element_text(angle=45, hjust=1))
#dev.off()

# Bar plot version
ggplot(filter(repmeans.emb %>% 
                filter(verb != "vacuous-verb"
                       & verb != "IMPERATIVE" & verb !="DECLARATIVE"
                       & verb != "bang\n'help'" & verb != "rang\n'let'"
                       & verb != "kankan\n'see-DUP'"
                ), has.embpred), aes(x=verb, y=prop)) + 
  geom_boxplot(outlier.shape = NA) + geom_jitter(width = 0.2) +
  scale_y_log10(name='Proportion of sentences with embedded clause', 
                breaks = c(0.001, 0.1, 0.25, 0.5, .9999), 
                labels = c('~0', 0.1, .25, .5, '~1')) +
  xlab('Verb')

# plot projection
### PART THREE: PROJECTION
projection_results$component <- 0:7
# 0 child 1compT 2embpred 3embsubj 4ebtensetensed 5embtenseto 6itr 7objtrue preptrue sentence
projection.melt <- melt(projection_results, c('child', 'component', 'itr', 'sentence'))

projection.mean <- filter(projection.melt, !(((sentence)%%10)>0), 
                          component %in% c(0, 1),
                          !(variable %in% c('obj'))) %>% 
  group_by(child, component, sentence, variable) %>%
  summarise(m=mean(value))

projection.summ <- group_by(projection.mean, component, sentence, variable) %>% 
  summarise(med=median(m, na.rm=T), q25=quantile(m, .25, na.rm=T), q75=quantile(m, .75, na.rm=T), 
            q025=quantile(m, .025, na.rm=T), q975=quantile(m, .975, na.rm=T),
            qmin=min(m, na.rm=T), qmax=max(m, na.rm=T))

#levels(projection.summ$variable) <- c('[emb comp]', '[emb clause]', '[emb subj]', '[emb tense]', '[emb infinitival]', '[do]', '[pp]')
levels(projection.summ$variable) <- unique(projection.summ$variable)
# levels can be obtained by unique(projection.summ$variable)
ggplot(filter(projection.summ, sentence<101), aes(x=(sentence+1)*10, y=med, linetype=factor(component))) +
  geom_ribbon(aes(ymin=qmin, ymax=qmax), fill="grey95") +
  geom_ribbon(aes(ymin=q25, ymax=q75), fill="grey80") +
  #geom_ribbon(alpha=.05, aes(ymin=q025, ymax=q975)) +
  geom_line(color="black", size=1) +
  facet_wrap(~variable, ncol = 4) + 
  scale_linetype(name='') +
  scale_x_continuous(name='Number of sentences seen', breaks=c(0,500,1000), labels=c('0', '500', '1000')) +
  scale_y_continuous(name='Probability of semantic component')