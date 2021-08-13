# Syntactic bootstrapping model

## Overview

This package implements the model of syntactic bootstrapping described in [Huang, White, Liao, Hacquard, & Lidz, 2021](https://doi.org/10.1080/10489223.2021.1934686) 
([Lingbuzz preprint](https://ling.auf.net/lingbuzz/005553)). This model is a modification of the one in [White, Hacquard, & Lidz 2017](http://aswhite.net/papers/white_labeling_2017.pdf), which is in turn based on the models in [White 2015](http://aswhite.net/papers/white_information_2015.pdf) and [White & Rawlins 2016](http://aswhite.net/papers/white_computational_2016_salt.pdf). 

## Running the model

This model can be either run for English (`en`) or Mandarin (`mc`).

```bash
python3 experiment.py -l en
python3 experiment.py -l mc
```

Doing so will generate 3 sets of files: verbreps, projection_results, and featureprobs. Verbreps contains the probabilities for semantic features for each verb and tracks how these probabilities change over time. The probability that a semantic feature maps to a particular (language-specific) syntactic feature and how the probability changes over time is recorded in projection_results. The final probability of each syntactic feature for a given verb is listed in featureprobs.

By default, the model implements an either-or bias that is based on Jensen-Shannon divergence; see `model.py` for details. The model also contains an alternative implementation, based on Kullback-Leibler divergence. If you prefer using that variant of the bias, you will have to directly specify that in `model.py`.

## Data
The data found in `bin/data/gleason_data.csv` was extracted based on an algorithm described in [White, Resnik, Hacquard, & Lidz under review](http://aswhite.net/papers/white_contextual_2016.pdf).

The data found in `bin/data/Mandarin_corpora_data.csv` was based on child-ambient utterances in 10 Mandarin CHILDES corpora, as described in Huang et al. (Section 5.3.2). Note that the syntactic features listed for a given sentence might not align with one's intuitions. For subordinate clauses, this is because of errors introduced by the automated annotation process. For main clauses, this is because the features and sentence type (e.g. declarative or imperative) are actually derived directly from manual annotations of a smaller random sample of 600 utterances.