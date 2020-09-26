# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 20:33:46 2020

@author: znhua
"""

import pandas as pd, numpy as np, glob

wkdir = r"C:/Users/znhua/OneDrive/Documents/gh/MainClauseModel/bin"

gleason_gold = pd.read_csv(wkdir + r"/data/gleason_corpus_gold.csv")

valid_results_files = []
for f in glob.glob(wkdir+ r"/results/1e2/*.csv"):
    if "feature" in f.replace(wkdir, ""):
        valid_results_files.append(f)

feats = ['comp[T.WH]', 'embpred[T.True]', 'embsubj[T.True]',
       'embtense[T.TENSED]', 'embtense[T.TO]', 'obj[T.True]',
       'prep1[T.True]']
#children = subcorp_gold['child'].unique()
ten_kids = ['andy', 'bobby', 'charlie', 'david', 'eddie', 'frank', 'guy',
       'helen', 'isadora', 'john']
att_verbs = ['want', 'see', 'know', 'think', 'say', 'like', 'tell', 'try', 'need', 'remember']

weight = 0
itr = 1
prob_itrs = []

def loop_itr(prob_itrs, itr, subcorp_gold, w_results):
    print("itr", itr)
    for i, it in enumerate(subcorp_gold):
        # Check only the attitude verbs of interest
        # i.e. let's not worry about the corpus entire corpus
        #if it['verb'] in att_verbs:
        if i%100 == 0:
            print(i)
        it_copy = it.copy()
        it_copy['subcorp_ind'] = subcorp_ind
        it_copy['itr'] = itr
        it_copy['sum_logprob'] = np.nan
        it_copy['att10'] = it['verb'] in att_verbs
        
        sum_logprob = 0
        for feat in feats:
            predicted_prob = w_results.loc[(w_results['itr'] == itr) & 
                      (w_results['child'] == it['child']) & 
                      (w_results['verb'] == it['verb'])
                      ][feat]
            #print('\n', it['child'], it['verb'], feat, it[feat], '\n', predicted_prob)
            # Bernoulli
            if it[feat] == 0:
                predicted_prob = 1 - predicted_prob
            sum_logprob += np.log10(predicted_prob)
        #print(it['child'], it['verb'], 'log10p', 10**sum_logprob)
        
        # Convert these into actual probs
        try:
            it_copy['sum_logprob'] = sum_logprob.values[0]
            it_copy['prob'] = 10**sum_logprob.values[0]
        except:
            it_copy['prob'] = np.nan
        
        prob_itrs.append(it_copy)


prob_itrs = []
for f in valid_results_files:
    #f = valid_results_files[1]
    weight = float(f[-7:-4])
    subcorp_ind = int(f[-9:-8])
    print("file", f, weight, subcorp_ind)
    # These are the feature probs associated with the training dataset
    # verb, child, itr, features
    w_results = pd.read_csv(f)
    # This is our test dataset: verbs and the attested features
    # This syntax generates a list of dictionaries
    subcorp_gold = gleason_gold.loc[gleason_gold['subcorp'] == subcorp_ind].to_dict('records')

    for itr in range(10):
        loop_itr(prob_itrs, itr, subcorp_gold, w_results)


df_probs = pd.DataFrame(prob_itrs)
df_probs = df_probs[df_probs['child'].isin(ten_kids)][['verb', 'prob']].groupby(['verb']).describe()
df_probs['att10'] = (df_probs.index).isin(att_verbs)

df_probs.to_csv(wkdir + '/validation/weight' + str(weight) + ' en.csv')
