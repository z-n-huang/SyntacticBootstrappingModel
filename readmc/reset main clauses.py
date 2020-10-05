# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 20:29:22 2020

@author: znhua
"""

import pandas as pd
import numpy as np


### High level goal: sort main clauses into declaratives, imperatives, and interrogatives
### Reset subjects, modals, etc. for declaratives and imperatives
### Step 1. Code interrogatives
data = pd.read_csv("mc10all.txt", encoding = 'utf-8-sig')
data = data.rename({"head": "verb", "originalLine": "utterance",
                    "has_obj": "obj", "has_clause": "embpred"}, axis = 1)

data['embAspect'] = data['aspect'].notna()
data['embModal'] = data['modal'].notna()
data['embNegation'] = data['neg'].notna()
data['embQ'] = data['has_whAxA'].notna()
data['embSubject'] = data['subj'].notna()
data['sentenceid'] = data['file'] + data['lineNo'].astype(str)

data = data.drop(['speaker', 'modal', 'neg', 'has_whAxA', 'subj', 
                  'file', 'clausal_ind', 'cleanedUtterance', 'lineNo'], axis = 1)

def h_sum_features(verb_type, data = data):
    x = data[data.verb == verb_type]
    print([round(prop, 2) for prop in [x.embSubject.mean(), x.embModal.mean(), 
                                       x.embAspect.mean(), x.embQ.mean()]])

# How many ROOT, ROOTproh, ROOT? are there
data[data.verb.str.startswith('0')].groupby('force').count()

# Change all interrogatives whose 'verbs' are ROOT? or ROOT/ROOTproh with a Q element to INTERROGATIVE
data.loc[(data['force'] == 'Q') & (data['verb'] == "0"), 'verb'] = 'INTERROGATIVE'
data.loc[(data['force'] == 'PROH') & (data['verb'] == "0") & (data.embQ == True), 'verb'] = 'INTERROGATIVE'

n_int = data[data.verb == 'INTERROGATIVE'].shape[0]

# Check to make sure there are embedded questions
print('n embedded questions (overt wh/AnotA): ', data[(data['embQ'] == True) & (data['verb'] != 'INTERROGATIVE')].shape[0])
# Check to make sure there are main clause questions
print('n main clause questions with overt wh/AnotA: ', data[(data['embQ'] == True) & (data['verb'] == 'INTERROGATIVE')].shape[0])
print('n main clause questions without overt wh/AnotA: ', data[(data['embQ'] == False) & (data['verb'] == 'INTERROGATIVE')].shape[0])

# What does the main clause distribution look like so far?
data[data['verb'].isin(('0', 'INTERROGATIVE'))].groupby('verb').count()
# CHECK: What are the proportions of overt subjects, etc.?
h_sum_features('0', data)

### Step 2. calculate total number of items, calculate prohibitives n_proh
### 3a. How many non-prohibitives + prohibitives are there?
n_all = data[data['verb'].isin(['0'])].shape[0]

### Step 3. Assign a 2:1 ratio for declaratives and imperatives
n_decl_ratio = 2/3

### a. How many declaratives and imperatives should there be?
n_decl = int(n_all * n_decl_ratio)
n_imp = n_all - n_decl
### b. How many prohibitives are there already?
n_proh = data[(data['force'] == 'PROH') & (data['verb'] == "0")].shape[0]
### c. How many non-prohibitive imperatives should there be?
n_imp_less_proh = n_imp - n_proh

# Check - should add up to a nice round number
print(n_int + n_decl + n_imp_less_proh + n_proh)

### Step 4. Re-label these entries as DECLARATIVE and IMPERATIVE
### a. label all non-prohibitives as DECLARATIVES
# Recode the root as IMPERATIVE
data.loc[(data['force'] == 'PROH') & (data['verb'] == "0"), 'verb'] = 'IMPERATIVE'
# Recode all existing roots as DECLARATIVE
data.loc[(data['force'].isna()) & (data['verb'] == "0"), 'verb'] = 'DECLARATIVE'

# Check. Should add up to a nice round number
data[data['verb'].isin(('DECLARATIVE', 'IMPERATIVE', 'INTERROGATIVE'))].groupby('verb').count()
h_sum_features('DECLARATIVE', data)
print(data[data['verb'] == 'DECLARATIVE'].shape[0])
h_sum_features('IMPERATIVE', data)
print(data[data['verb'] == 'IMPERATIVE'].shape[0])
h_sum_features('INTERROGATIVE', data)
print(data[data['verb'] == 'INTERROGATIVE'].shape[0])

if n_imp_less_proh > 0:
    ### b. Take the set of sentences with DECLARATIVE and whose heads are Verbs (not adjectives, nouns...)
    ### Randomly select a subset (w/o replacement) of size n_imp_less_proh
    random_imperative = data[(data['verb'].isin(['DECLARATIVE'])) & 
                             data['embPredIsVV'] == 1].sample(n_imp_less_proh, 
                                                              replace = False, 
                                                              random_state = 0)
    ### c. Label the verb in this subset as imperative
    data.loc[random_imperative.index, 'verb'] = 'IMPERATIVE'
    print("DECLARATIVE and IMPERATIVE assigned!")
else:
    print("ERROR!")

h_sum_features('DECLARATIVE', data)
print(data[data['verb'] == 'DECLARATIVE'].shape[0], 
      data[data['verb'] == 'DECLARATIVE'].shape[0] == n_decl)
h_sum_features('IMPERATIVE', data)
print(data[data['verb'] == 'IMPERATIVE'].shape[0],  
      data[data['verb'] == 'IMPERATIVE'].shape[0] == n_imp)

### d. Re-tag subjects, modals, aspect, etc.
### Figures are taken from a hand-coded random sample of 600 main clauses
#	            subj	modal	asp	    neg	    type
#declarative	60.3%	6.7%	8.4%	14.0%	100.0%
#imperative	    26.7%	1.1%	0.0%	6.7%	100.0%

np.random.seed(0)
data.loc[data.verb == 'DECLARATIVE', 'embSubject'] = np.random.binomial(1, .603, size = n_decl)
data.loc[data.verb == 'DECLARATIVE', 'embModal'] = np.random.binomial(1, .067, size = n_decl)
data.loc[data.verb == 'DECLARATIVE', 'embAspect'] = np.random.binomial(1, .084, size = n_decl)
data.loc[data.verb == 'DECLARATIVE', 'embNegation'] = np.random.binomial(1, .140, size = n_decl)
#data.loc[data.verb == 'DECLARATIVE', 'embDiscourse'] = np.random.binomial(1, .39, size = n_decl)
data.loc[data.verb == 'DECLARATIVE', 'embpred'] = 1
data.loc[data.verb == 'DECLARATIVE', 'obj'] = 0
data.loc[data.verb == 'DECLARATIVE', 'embQ'] = 0

data.loc[data.verb == 'IMPERATIVE', 'embSubject'] = np.random.binomial(1, .267, size = n_imp)
data.loc[data.verb == 'IMPERATIVE', 'embModal'] = np.random.binomial(1, .011, size = n_imp)
data.loc[data.verb == 'IMPERATIVE', 'embAspect'] = np.random.binomial(1, .000, size = n_imp)
data.loc[data.verb == 'IMPERATIVE', 'embNegation'] = np.random.binomial(1, .067, size = n_imp)
#data.loc[data.verb == 'IMPERATIVE', 'embDiscourse'] = np.random.binomial(1, .21, size = n_imp)
data.loc[data.verb == 'IMPERATIVE', 'embpred'] = 1
data.loc[data.verb == 'IMPERATIVE', 'obj'] = 0
data.loc[data.verb == 'IMPERATIVE', 'embQ'] = 0

### e. Check overall statistics
h_sum_features('DECLARATIVE', data)
print(data[data['verb'] == 'DECLARATIVE'].shape[0], data[data['verb'] == 'DECLARATIVE'].shape[0] == n_decl)
h_sum_features('IMPERATIVE', data)
print(data[data['verb'] == 'IMPERATIVE'].shape[0],  data[data['verb'] == 'IMPERATIVE'].shape[0] == n_imp)
# No particular expectations about interrogatives, but for transparency:
h_sum_features('INTERROGATIVE', data)
print(data[data['verb'] == 'INTERROGATIVE'].shape[0])

h_sum_features('说', data)
h_sum_features('要', data)
h_sum_features('吃', data)

# At this point, there should be no verbs starting with 0 (root)
print(data[data.verb.str.startswith('0')].groupby('verb').count())
"""
# Convert verbs into numerals, for easier processing (unicode is tricky)
verbIndex = {verbLemma: "v"+str(i) for i, verbLemma in enumerate(data.verb.unique())}
inv_verbIndex = {v: k for k, v in verbIndex.items()}
data.verb.replace(to_replace= verbIndex, inplace = True)
"""

### Step 5. Drop irrelevant columns
data = data[["embAspect", "embModal", "embNegation", "embQ", "embSubject", "embpred", "obj", "utterance", "verb", "child", "sentenceid"]]
data['child'] = "c" + data['child'].astype(str)
### Step 6. Convert values to TRUE, FALSE
boolean_values_map = {0: False, 1: True, 2: True, 3: True, }
for col in data.columns:
    if col not in ['sentenceid', 'utterance', 'verb', 'child']:
        data[col] = data[col].map(boolean_values_map)


# Randomly select 5,000 sentences for each child
data.to_csv('processedmc3oct3.csv', encoding='utf-8-sig', index=False)
