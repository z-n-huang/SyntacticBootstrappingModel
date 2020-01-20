library(readr)
library(plyr)
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
verbreps_results <- read_csv("results/verbreps_resultsen nopen.csv") #  w(/o) " 10wpen"
projection_results <- read_csv("results/projection_resultsen nopen.csv")
gleason_data <- read_csv("data/gleason_data.csv")
#verbreps_results <- verbreps_results %>% filter(verb != "IMPERATIVE" & verb!="DECLARATIVE")
#gleason_data <- read_csv("data/processedmc2.csv")
#verbreps_results <- verbreps_results %>% filter(verb != "tell"
#                                              & verb != "IMPERATIVE" & verb!="DECLARATIVE"
#                                              & verb != "帮" & verb !="让"
#                                              & verb != "看看"
#                                        )

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

repmeans.summ$verbPlot <- mapvalues(repmeans.summ$verb, 
                                    from = c("DECLARATIVE", "IMPERATIVE", "要", "看", "说",
                                             "看看", "讲", "想", "知道", "叫",
                                             "喜欢", "告诉", "帮", "让", "觉得",
                                             "want", "see", "know", "think", "say",
                                             "like", "tell", "try", "need", "remember"
                                    ),
                                    to = c("DECLARATIVE", "IMPERATIVE", "yao 'want' (D)", "kan 'see' (B)", "shuo 'say' (B)",
                                           "kankan 'see-DUP' (B)", "jiang 'say' (B)", "xiang 'think/want' (B/D)", "zhidao 'know' (B)",
                                           "jiao 'call/get' (D)", "xihuan 'like' (D)", "gaosu 'tell' (B)", "bang 'help' (O)", 
                                           "rang 'let' (O)", "juede 'feel' (B)",
                                           "want (D)", "see (B)", "know (B)", "think (B)", "say (B)",
                                           "like (D)", "tell (B/D)", "try (D)", "need (D)", "remember (B)"
                                    )
) 
repmeans.summ <- repmeans.summ %>% filter(verbPlot != "<NA>")
#tikz('~/experiments/MainClauseModel/bin/verbrep_prob.tikz', width=5.5, height=4)
ggplot(repmeans.summ, aes(x=(sentence+1)*10, y=med, color = variable, fill = variable )) + # linetype=variable, 
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
gleason_data$has.embpred <- gleason_data$embpred!='FALSE'

emb.counts <- filter(gleason_data, verb %in% unique(repmeans.summ$verb)) %>%
  count(child, verb, has.embpred) %>% group_by(child, verb) %>% mutate(tot=sum(n), prop=n/tot)

repmeans.emb <- merge(filter(repmeans.melt, repmeans.melt$sentence==max(repmeans.melt$sentence)), 
                      emb.counts)

repmeans.emb$verb <- ordered(repmeans.emb$verb, levels=verb.counts$verb)

repmeans.emb.cast <- dcast(filter(repmeans.emb, has.embpred), child+verb+prop ~ variable, value.var = 'value')
repmeans.emb.cast$dorb <- 1-(1-repmeans.emb.cast$belief)*(1-repmeans.emb.cast$desire)

logistic <- function(p) log(p)-log(1-p)

#tikz('~/experiments/MainClauseModel/bin/embclause_prob.tikz', width=5.5, height=4)
ggplot(filter(repmeans.emb, has.embpred), aes(x=prop, y=logistic(value), shape=variable)) + 
  geom_point(size=1.5) +
  facet_wrap(~verb, ncol=5) + 
  scale_shape_manual(name='', values = c(16, 1)) +
  scale_x_continuous(name='Proportion of sentences with embedded clause', breaks=c(0, .5, 1), labels=c(0, .5, 1)) +
  scale_y_continuous(name='Probability of semantic component', breaks=logistic(c(0.0001, 0.1, 0.5, 0.9, 0.9999)), labels=c('~0', 0.1, 0.5, 0.9, '~1'))# +
#theme(axis.text.x=element_text(angle=45, hjust=1))
#dev.off()

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