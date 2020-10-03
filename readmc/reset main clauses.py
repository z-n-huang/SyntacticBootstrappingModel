# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 20:29:22 2020

@author: znhua
"""

import pandas as pd
import numpy as np




def h_sum_features(verb_type, data = data):
    x = data[data.verb == verb_type]
    print([round(prop, 2) for prop in [x.embSubject.mean(), x.embModal.mean(), 
                                       x.embAspect.mean(), x.embQ.mean()]])

### High level goal: sort main clauses into declaratives, imperatives, and interrogatives
### Reset subjects, modals, etc. for declaratives and imperatives
### Step 1. Code interrogatives
data = pd.read_csv("mc10full.txt", encoding = 'utf-8-sig')
data = data.rename({"head": "verb", "originalLine": "utterance",
                    "has_obj": "obj", "has_clause": "embpred"}, axis = 1)

data['embAspect'] = data['aspect'].notna()
data['embModal'] = data['modal'].notna()
data['embNegation'] = data['neg'].notna()
data['embQ'] = data['has_whAxA'].notna()
data['embSubject']= data['subj'].notna()

data = data.drop(['speaker', 'modal', 'neg', 'has_whAxA', 'subj', 
                  'file', 'clausal_ind', 'cleanedUtterance', 'lineNo'], axis = 1)

    # How many ROOT, ROOTproh, ROOT? are there
data[data.verb.str.startswith('0')].groupby('force').count()

# Change all interrogatives whose 'verbs' are ROOT? or ROOT/ROOTproh with a Q element to INTERROGATIVE
data.loc[(data['force'] == 'Q') & (data['verb'] == "0"), 'verb'] = 'INTERROGATIVE'
data.loc[(data['force'] == 'PROH') & (data['verb'] == "0") & (data.embQ == True), 'verb'] = 'INTERROGATIVE'

q = data[data.verb == 'INTERROGATIVE']

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
n_proh = data[data['verb'] == 'ROOTproh'].shape[0]
### c. How many non-prohibitive imperatives should there be?
n_imp_less_proh = n_imp - n_proh

### Step 4. Re-label these entries as DECLARATIVE and IMPERATIVE
### a. label all non-prohibitives as DECLARATIVES
data.verb.replace(to_replace= {'ROOT': 'DECLARATIVE',
                               'ROOTproh': 'IMPERATIVE'}, inplace = True)
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
data.loc[data.verb == 'DECLARATIVE', 'embSubject'] = np.random.binomial(1, .61, size = n_decl)
data.loc[data.verb == 'DECLARATIVE', 'embModal'] = np.random.binomial(1, .06, size = n_decl)
data.loc[data.verb == 'DECLARATIVE', 'embAspect'] = np.random.binomial(1, .07, size = n_decl)
data.loc[data.verb == 'DECLARATIVE', 'embNegation'] = np.random.binomial(1, .17, size = n_decl)
data.loc[data.verb == 'DECLARATIVE', 'embDiscourse'] = np.random.binomial(1, .39, size = n_decl)
data.loc[data.verb == 'DECLARATIVE', 'embpred'] = 1
data.loc[data.verb == 'DECLARATIVE', 'obj'] = 0
data.loc[data.verb == 'DECLARATIVE', 'embQ'] = 0

data.loc[data.verb == 'IMPERATIVE', 'embSubject'] = np.random.binomial(1, .32, size = n_imp)
data.loc[data.verb == 'IMPERATIVE', 'embModal'] = np.random.binomial(1, .00, size = n_imp)
data.loc[data.verb == 'IMPERATIVE', 'embAspect'] = np.random.binomial(1, .01, size = n_imp)
data.loc[data.verb == 'IMPERATIVE', 'embNegation'] = np.random.binomial(1, .01, size = n_imp)
data.loc[data.verb == 'IMPERATIVE', 'embDiscourse'] = np.random.binomial(1, .21, size = n_imp)
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

# At this point, there should be no verbs starting with ROOT
print(data[data.verb.str.startswith('ROOT')].groupby('verb').count())
"""
# Convert verbs into numerals, for easier processing (unicode is tricky)
verbIndex = {verbLemma: "v"+str(i) for i, verbLemma in enumerate(data.verb.unique())}
inv_verbIndex = {v: k for k, v in verbIndex.items()}
data.verb.replace(to_replace= verbIndex, inplace = True)
"""


### Step 5. Drop irrelevant columns
data = data.drop(['embPreds', 'verbPos', 'embPredIsVV'], axis = 1)

### Step 6. Convert values to TRUE, FALSE
boolean_values_map = {0: 'FALSE', 1: 'TRUE', 2: 'TRUE', 3: 'TRUE', }
for col in data.columns:
    if col not in ['sentenceid', 'utterance', 'verb', 'child']:
        data[col] = data[col].map(boolean_values_map)


# Randomly select 5,000 sentences for each child
children = []
for i in range(10):
    np.random.seed(i)
    random_sentenceid = np.random.choice(data.sentenceid.unique(), 
                                         size = 5000, 
                                         replace = False
                                         )
    
    random_data = data[data['sentenceid'].isin(random_sentenceid)].reset_index(drop = True)
    random_data['child'] = 'c'+ str(i)
    children.append(random_data)
children_data = pd.concat(children)

children_data.to_csv('processedmc2may21.csv', encoding='utf-8-sig', index=False)
