library(readr)
library(dplyr)
library(reshape2)
library(ggplot2)
library(tikzDevice)

# set ggplot2 theme

theme_set(theme_classic()+ theme(axis.line.x = element_line(colour = 'black', size=0.5, linetype='solid'),
                                 axis.line.y = element_line(colour = 'black', size=0.5, linetype='solid'),
                                 panel.grid.major = element_line(size = (0.2), colour="grey")
))

# Load CSV files
## Example here loads model output for English
verbreps_wpen_results <- rbind(
  read_csv("~/gh/MainClauseModel/bin/results/en/verbreps_resultsen 0010.csv")
)

# Load corpus data
# For English
corpus_data <- read_csv("~/gh/MainClauseModel/bin/data/corpus_data_orig.csv")
# For Mandarin
corpus_data <- read_csv("~/gh/MainClauseModel/bin/data/Mandarin_corpora_data.csv")


# Checks - there should be 10 children, 10 verbs, 20000 entries / verb / child
verbreps_results %>% group_by(child) %>% summarize(average_1 = mean(`0`), count = n())
verbreps_results %>% group_by(verb) %>% summarize(average_1 = mean(`0`), count = n())

# PART ONE:
# Plot verb representations
repmeans <- group_by(verbreps_results, verb, sentence, child) %>% 
  summarise(belief=mean(`0`), desire=mean(`1`)) %>% filter(!((sentence%%10)>0))

repmeans.melt <- melt(repmeans, c('verb', 'sentence', 'child'))

repmeans.summ <- group_by(repmeans.melt, verb, variable, sentence) %>% 
  summarise(med=median(value), q25=quantile(value, .25), q75=quantile(value, .75), 
            q025=quantile(value, .025), q975=quantile(value, .975),
            qmin=min(value), qmax=max(value))

verb.counts <- count(corpus_data, verb, sort = T)
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
                                 "告诉" = "gaosu 'tell' (B/D)", 
                                 "叫" = "jiao 'call/get' (D)",
                                 "准备" = "zhunbei 'prepare to' (D)",
                                 
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

ggplot(repmeans.summ
       %>% filter(verbPlot != "vacuous-verb"
         & verbPlot != "IMPERATIVE" & verbPlot !="DECLARATIVE"
         & verbPlot != "bang 'help' (O)" & verbPlot != "rang 'let' (O)"
         & verbPlot != "kankan 'see-DUP' (B)"
         #& verbPlot != "zhunbei 'prepare to' (D)"
         & verbPlot != "jiao 'call/get' (D)"
       ), 
       aes(x=(sentence+1)*10, y=med, color = variable, linetype = variable, fill = variable)) + # 
  geom_ribbon(aes(ymin=qmin, ymax=qmax,  fill = variable), alpha = 0.1, color = NA) +
  geom_ribbon(aes(ymin=q25, ymax=q75),  alpha = 0.3, color = NA) +
  #geom_ribbon(alpha=.05, aes(ymin=q025, ymax=q975)) +
  geom_line(size = 1) + # color = black
  facet_wrap(~verbPlot, ncol = 5) + 
  scale_linetype(name='') +
  scale_x_continuous(name='Number of sentences seen (thousands)', breaks=c(0,10000,20000), labels=c('0', '10', '20')) +
  scale_y_continuous(name='Probability of semantic component') +
  scale_fill_hue(l=40) + # how light/dark the ribbon fill is
  scale_color_hue(l=40) + # how light/dark the line is
  theme(legend.title=element_blank()) + # hide legend name
  theme(strip.text.x = element_text(size = 8)) +
  labs(color = "", linetype = "", fill = "") # needed to merge legends - otherwise there will be separate legends
#dev.off()

### PART TWO: Probability of semantics vs. frequency of clausal complements
corpus_data$has.embpred <- corpus_data$embpred!='NONE' # English
#corpus_data$has.embpred <- corpus_data$embpred!='FALSE' # Uncomment this line for MC

emb.counts <- filter(corpus_data, verb %in% unique(repmeans.summ$verb)) %>%
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
                                 "看看" = "kankan\n'see-DUP' (B)", 
                                 "想" = "xiang\n'think, want' (B, D)", 
                                 "让" = "rang\n'let' (O)", 
                                 "喜欢" = "xihuan\n'like' (D)",  
                                 "觉得" = "juede\n'feel' (B)",
                                 "讲" = "jiang\n'say' (B)",
                                 "知道" = "zhidao\n'know' (B)", 
                                 "告诉" = "gaosu\n'tell' (B/D)", 
                                 "叫" = "jiao\n'call/get' (D)",
                                 "帮" = "bang\n'help' (O)", 
                                 "准备" = "zhunbei\n'prepare to' (D)", 
                            
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
                                "看看" = "kankan\n'see-DUP' (B)", 
                                "想" = "xiang\n'think, want' (B, D)", 
                                "让" = "rang\n'let' (O)", 
                                "喜欢" = "xihuan\n'like' (D)",  
                                "觉得" = "juede\n'feel' (B)",
                                "讲" = "jiang\n'say' (B)",
                                "知道" = "zhidao\n'know' (B)", 
                                "告诉" = "gaosu\n'tell' (B/D)", 
                                "叫" = "jiao\n'call/get' (D)",
                                "帮" = "bang\n'help' (O)", 
                                "准备" = "zhunbei\n'get ready to' (D)", 
                                
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
                  #& verb != "jiao\n'call/get' (D)"
                  & verb != "zhunbei\n'prepare to' (D)"
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

ggplot(filter(repmeans.emb %>% 
                filter(verb != "vacuous-verb"
                       & verb != "IMPERATIVE" & verb !="DECLARATIVE"
                       & verb != "bang\n'help' (O)" & verb != "rang\n'let' (O)"
                       & verb != "kankan\n'see-DUP' (B)"
                       & verb != "jiao\n'call/get' (D)"
                       #& verb != "zhunbei\n'prepare to' (D)"
                ) %>% filter(variable == 'belief'), has.embpred), aes(x=verb, y=prop)) + 
  geom_boxplot(outlier.shape = NA) + geom_jitter(width = 0.2) +
  scale_y_log10(name='Proportion of sentences with embedded clause', 
                breaks = c(0.001, 0.1, 0.25, 0.5, .9999), 
                labels = c('~0', 0.1, .25, .5, '~1')) +
  xlab('Verb')
