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

# Results for model without a either-or bias ``nopen(alty)''
v2nopen <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 0e0 x10en may20/verbreps_resultsen 5-15 0e0 2.csv")
v3nopen <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 0e0 x10en may20/verbreps_resultsen 5-15 0e0 3.csv")
v4nopen <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 0e0 x10en may20/verbreps_resultsen 5-15 0e0 4.csv")
v5nopen <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 0e0 x10en may20/verbreps_resultsen 5-15 0e0 5.csv")
v2nopen$itr <- ifelse(v2nopen$itr == 0, 2, 3)
v3nopen$itr <- ifelse(v3nopen$itr == 0, 4, 5)
v4nopen$itr <- ifelse(v4nopen$itr == 0, 6, 7)
v5nopen$itr <- ifelse(v5nopen$itr == 0, 8, 9)

verbreps_nopen_results <- rbind(
  read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 0e0 x10en may20/verbreps_resultsen 5-15 0e0 1.csv"),
  v2nopen, v3nopen, v4nopen, v5nopen
)

# Results for model with a either-or KLD bias
v2kl <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results kl 5-15 1e0 x10en may21/verbreps_resultsen kl 5-15 1e0 2.csv")
v3kl <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results kl 5-15 1e0 x10en may21/verbreps_resultsen kl 5-15 1e0 3.csv")
v4kl <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results kl 5-15 1e0 x10en may21/verbreps_resultsen kl 5-15 1e0 4.csv")
v5kl <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results kl 5-15 1e0 x10en may21/verbreps_resultsen kl 5-15 1e0 5.csv")
v2kl$itr <- ifelse(v2kl$itr == 0, 2, 3)
v3kl$itr <- ifelse(v3kl$itr == 0, 4, 5)
v4kl$itr <- ifelse(v4kl$itr == 0, 6, 7)
v5kl$itr <- ifelse(v5kl$itr == 0, 8, 9)

verbreps_kl_results <- rbind(
  read_csv("C:/Users/znhua/Documents/raspberry transfers/results kl 5-15 1e0 x10en may21/verbreps_resultsen kl 5-15 1e0 1.csv"),
  v2kl, v3kl, v4kl, v5kl
)

# Results for model with a either-or JSD bias
v2 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10en may19/verbreps_resultsen 5-15 1e0 2.csv")
v3 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10en may19/verbreps_resultsen 5-15 1e0 3.csv")
v4 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10en may19/verbreps_resultsen 5-15 1e0 4.csv")
v5 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10en may19/verbreps_resultsen 5-15 1e0 5.csv")
v2$itr <- ifelse(v2$itr == 0, 2, 3)
v3$itr <- ifelse(v3$itr == 0, 4, 5)
v4$itr <- ifelse(v4$itr == 0, 6, 7)
v5$itr <- ifelse(v5$itr == 0, 8, 9)

verbreps_results <- rbind(
  read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10en may19/verbreps_resultsen 5-15 1e0 1.csv"),
  v2, v3, v4, v5
)

p2 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10en may19/projection_resultsen 5-15 1e0 2.csv")
p3 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10en may19/projection_resultsen 5-15 1e0 3.csv")
p4 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10en may19/projection_resultsen 5-15 1e0 4.csv")
p5 <- read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10en may19/projection_resultsen 5-15 1e0 5.csv")
p2$itr <- ifelse(p2$itr == 0, 2, 3)
p3$itr <- ifelse(p3$itr == 0, 4, 5)
p4$itr <- ifelse(p4$itr == 0, 6, 7)
p5$itr <- ifelse(p5$itr == 0, 8, 9)

projection_results <- rbind(
  read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10en may19/projection_resultsen 5-15 1e0 1.csv"),
  p2, p3, p4, p5
)

#read_csv("C:/Users/znhua/Documents/raspberry transfers/results 5-15 1e0 x10 en may19/verbreps_resultsen 5-15 1e0 1.csv")
verbreps_results <- read_csv("C:/Users/znhua/Documents/raspberry transfers/verbreps_resultsen 5e0.csv")
projection_results <- read_csv("C:/Users/znhua/Documents/raspberry transfers/projection_resultsen 5e0.csv")

gleason_data <- read_csv("data/gleason_data.csv")
# With penalty
verbreps_results <- verbreps_results %>% filter(verb != "IMPERATIVE" & verb!="DECLARATIVE")
# Without penalty
verbreps_results <- verbreps_nopen_results  %>% filter(verb != "IMPERATIVE" & verb!="DECLARATIVE")
# With KLD penalty
verbreps_results <- verbreps_kl_results  %>% filter(verb != "IMPERATIVE" & verb!="DECLARATIVE")

## END LOADING ENGLISH

## START LOADING MANDARIN
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

## With penalty

# v2 <- read_csv(paste("results/verbreps_resultsmc 1-2.csv", sep = "")) # no V2, as v1 has two itrs
v3_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/verbreps_resultsmc 1-3.csv", sep = ""))
v4_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/verbreps_resultsmc 1-4.csv", sep = ""))
v5_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/verbreps_resultsmc 1-5.csv", sep = ""))
v6_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/verbreps_resultsmc 1-6.csv", sep = ""))
v7_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/verbreps_resultsmc 1-7.csv", sep = ""))
v8_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/verbreps_resultsmc 1-8.csv", sep = ""))
v9_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/verbreps_resultsmc 1-9.csv", sep = ""))
v0_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/verbreps_resultsmc 1-0.csv", sep = ""))

#v2$itr <- 2
v3_mc$itr <- 3
v4_mc$itr <- 4
v5_mc$itr <- 5
v6_mc$itr <- 6
v7_mc$itr <- 7
v8_mc$itr <- 8
v9_mc$itr <- 9
v0_mc$itr <- 2
verbreps_results <- rbind(
  read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/verbreps_resultsmc 1-1.csv", sep = "")),
  v3_mc, v4_mc, v5_mc, v6_mc, v7_mc, v8_mc, v9_mc, v0_mc
)

p3_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/projection_resultsmc 1-3.csv", sep = ""))
p4_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/projection_resultsmc 1-4.csv", sep = ""))
p5_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/projection_resultsmc 1-5.csv", sep = ""))
p6_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/projection_resultsmc 1-6.csv", sep = ""))
p7_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/projection_resultsmc 1-7.csv", sep = ""))
p8_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/projection_resultsmc 1-8.csv", sep = ""))
p9_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/projection_resultsmc 1-9.csv", sep = ""))
p0_mc <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/projection_resultsmc 1-0.csv", sep = ""))

#v2$itr <- 2
p3_mc$itr <- 3
p4_mc$itr <- 4
p5_mc$itr <- 5
p6_mc$itr <- 6
p7_mc$itr <- 7
p8_mc$itr <- 8
p9_mc$itr <- 9
p0_mc$itr <- 2
projection_results <- rbind(
  read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 1e0 x10mc may23/projection_resultsmc 1-1.csv", sep = "")),
  p3_mc, p4_mc, p5_mc, p6_mc, p7_mc, p8_mc, p9_mc, p0_mc
)
unique(projection_results$itr)

## Without penalty (original model)
v2_mc_nopen <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 0e0 x10mc may23/verbreps_resultsmc 0-2.csv", sep = "")) # no V2, as v1 has two itrs
v3_mc_nopen <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 0e0 x10mc may23/verbreps_resultsmc 0-3.csv", sep = ""))
v4_mc_nopen <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 0e0 x10mc may23/verbreps_resultsmc 0-4.csv", sep = ""))
v5_mc_nopen <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 0e0 x10mc may23/verbreps_resultsmc 0-5.csv", sep = ""))
v6_mc_nopen <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 0e0 x10mc may23/verbreps_resultsmc 0-6.csv", sep = ""))
v7_mc_nopen <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 0e0 x10mc may23/verbreps_resultsmc 0-7.csv", sep = ""))
v8_mc_nopen <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 0e0 x10mc may23/verbreps_resultsmc 0-8.csv", sep = ""))
v9_mc_nopen <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 0e0 x10mc may23/verbreps_resultsmc 0-9.csv", sep = ""))
v0_mc_nopen <- read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 0e0 x10mc may23/verbreps_resultsmc 0-0.csv", sep = ""))

v2_mc_nopen$itr <- 2
v3_mc_nopen$itr <- 3
v4_mc_nopen$itr <- 4
v5_mc_nopen$itr <- 5
v6_mc_nopen$itr <- 6
v7_mc_nopen$itr <- 7
v8_mc_nopen$itr <- 8
v9_mc_nopen$itr <- 9
v0_mc_nopen$itr <- 1
verbreps_mc_results <- rbind(
  read_csv(paste("C:/Users/znhua/Documents/raspberry transfers/results 0e0 x10mc may23/verbreps_resultsmc 0-1.csv", sep = "")),
  v2_mc_nopen, v3_mc_nopen, v4_mc_nopen, v5_mc_nopen, v6_mc_nopen, v7_mc_nopen, v8_mc_nopen, v9_mc_nopen, v0_mc_nopen
)
unique(verbreps_mc_results$itr)

## end without penalty

verbreps_results <- read_csv("results/verbreps_resultsmc jsdpen.csv")
projection_results <- read_csv("results/projection_resultsmc jsdpen.csv")

gleason_data <- read_csv("data/processedmc2may21.csv")
verbreps_results <- verbreps_results %>% filter(verb != "tell")
verbreps_results <- verbreps_mc_results %>% filter(verb != "tell")

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
                                 "说" = "shuo 'say' (B)",
                                 "看" = "kan 'see' (B)", 
                                 "想" = "xiang 'think, want' (B, D)", 
                                 "帮" = "bang 'help' (O)", 
                                 "让" = "rang 'let' (O)", 
                                 "喜欢" = "xihuan 'like' (D)",  
                                 "看看" = "kankan 'see-DUP' (B)", 
                                 "觉得" = "juede 'feel' (B)",
                                 "讲" = "jiang 'say' (B)",
                                 "知道" = "zhidao 'know' (B)", 
                                 "告诉" = "gaosu 'tell' (B)", 
                                 "叫" = "jiao 'call/get' (D)",
                                 
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
#Try 800x400 px
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
gleason_data$has.embpred <- gleason_data$embpred!='FALSE' # MC

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
                                 "要" = "yao\n'want' (D)",
                                 "说" = "shuo\n'say' (B)",
                                 "看" = "kan\n'see' (B)", 
                                 "想" = "xiang\n'think, want' (B, D)", 
                                 "让" = "rang\n'let' (O)", 
                                 "喜欢" = "xihuan\n'like' (D)",  
                                 "觉得" = "juede\n'feel' (B)",
                                 "讲" = "jiang\n'say' (B)",
                                 "知道" = "zhidao\n'know' (B)", 
                                 "告诉" = "gaosu\n'tell' (B)", 
                                 "叫" = "jiao\n'call/get' (D)",
                                 "帮" = "bang\n'help' (O)", 
                            
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
repmeans.emb.cast$verb <- recode(repmeans.emb.cast$verb, 
                                DECLARATIVE = "DECLARATIVE",
                                IMPERATIVE = "IMPERATIVE",
                                "要" = "yao\n'want' (D)",
                                "说" = "shuo\n'say' (B)",
                                "看" = "kan\n'see' (B)", 
                                "想" = "xiang\n'think, want' (B, D)", 
                                "让" = "rang\n'let' (O)", 
                                "喜欢" = "xihuan\n'like' (D)",  
                                "觉得" = "juede\n'feel' (B)",
                                "讲" = "jiang\n'say' (B)",
                                "知道" = "zhidao\n'know' (B)", 
                                "告诉" = "gaosu\n'tell' (B)", 
                                "叫" = "jiao\n'call/get' (D)",
                                "帮" = "bang\n'help' (O)", 
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
                  & verb != "bang\n'help' (O)" & verb != "rang\n'let' (O)"
                  & verb != "kankan\n'see-DUP' (B)"
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
                       & verb != "bang\n'help' (O)" & verb != "rang\n'let' (O)"
                       & verb != "kankan\n'see-DUP' (B)"
                ) %>% filter(variable == 'belief'), has.embpred), aes(x=verb, y=prop)) + 
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