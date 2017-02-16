import numpy as np
import pandas as pd

from theano import shared
from patsy import dmatrix

class MainClauseData(object):
    
    def __init__(self, data, mainclause_features=None, feature_interactions=1,
                 feature_threshold=0.01):
        '''
        Parameters
        ----------
        data : pandas.DataFrame
            A dataframe containing at least the following columns:
            - sentenceid
            - verb
            - clausetype
            Any remaining columns are treated as syntactic features
            collocated with the verb

        mainclause_features : pandas.DataFrame
            A dataframe containing at least the following columns:
            - clausetype
            Any remaining columns are treated as syntactic features
            associated with the main clause type (e.g. DECLARATIVE, 
            IMPERATIVE). There must be exactly one row per clause type 
            and columns for each syntactic feature specified in data (i.e. 
            its columns) must be exactly those in data minus sentenceid 
            and verb

        feature_interactions : int
            Number of feature interactions to include

        feature_threshold : float or int
            Threshold a feature must pass for inclusion in the feature set
            If given a float, the feature must be on in that proportion of
            the data or greater. If given an int, the absolute number of 
            times the feature is on must be at leas that number
        '''
        
        self._data = data
        
        if mainclause_features is not None:
            self._mainclause_features = mainclause_features

            self._append_mainclause_features()

        else:
            self._data = self._data.drop('clausetype', axis=1)
            self._nclausetypes = 0
            
        self._convert_idvars_to_category()
        self._convert_features_to_dummies(feature_interactions,
                                          feature_threshold)
        self._extract_data_attrs()
        self._create_shared()

    def _append_mainclause_features(self):
        mcdata = pd.merge(self._data[['sentenceid', 'clausetype']],
                          self._mainclause_features)
        mcdata = mcdata.rename(columns={'clausetype': 'verb'})

        self._cclausetype = mcdata.verb.unique()
        self._nclausetype = self._cclausetype.shape[0]
        
        self._data = pd.concat([self._data.drop('clausetype', axis=1), mcdata])
        
    def _convert_idvars_to_category(self):
        self._data.sentenceid = self._data.sentenceid.astype('category')

        if self._nclausetype:
            realverbs = [v for v in self._data.verb.unique() if v not in self._cclausetype]
            verbcats = list(self._cclausetype)+realverbs
            self._data.verb = self._data.verb.astype('category', categories=verbcats)
        else:
            self._data.verb = self._data.verb.astype('category')

    def _convert_features_to_dummies(self, interactions, threshold):
        idvars = np.intersect1d(['child', 'sentenceid', 'speaker', 'verb', 'matrix'],
                                self._data.columns)
        feature_cols = self._data.drop(idvars, axis=1).columns

        dummies = dmatrix('('+'+'.join(feature_cols)+')**'+str(interactions),
                          self._data,
                          return_type='dataframe')

        dropcols = ['Intercept'] + [c for c in dummies.columns if 'NONE' in c]
        features = dummies.drop(dropcols, axis=1)

        feature_sums = features.sum(axis=0)

        if isinstance(threshold, int):
            self._featcols = np.array(feature_sums[feature_sums>=threshold].index)
        elif isinstance(threshold, float):
            feature_props = feature_sums / features.shape[0]
            self._featcols = np.array(feature_props[feature_props>=threshold].index)
        else:
            raise ValueError('threshold must be float or int')    

        self._features = shared(np.array(features[self._featcols]), name='features')
        
    def _extract_data_attrs(self):
        self._nfeature = self._featcols.shape[0]
        
        for col in ['sentenceid', 'verb']:
            self.__dict__['_c'+col] = self._data[col].cat.categories
            self.__dict__['_n'+col] = self.__dict__['_c'+col].shape[0]

    def _create_shared(self):
        for col in ['sentenceid', 'verb']:
            self.__dict__[col+'_shared'] = shared(np.array(self._data[col].cat.codes),
                                                  name=col)
        
                
    @property
    def verb(self):
        return self._data.verb.cat.codes
    
    @property
    def features(self):
        return self._features

    @property
    def feature_names(self):
        return np.array(self._featcols)
    
    def n(self, col):
        return self.__dict__['_n'+col]
        
    def categories(self, col):
        return self.__dict__['_c'+col]    

    def sentence(self, idx):
        return np.where(self._data.sentenceid==idx)[0].astype(np.int32)
    
def main(datapath='../bin/data/gleason_data.csv', featurepath='../bin/data/mainclause_features.csv',
         separate_children=True):
    d = pd.read_csv(datapath)
    f = pd.read_csv(featurepath)
    
    d['sentenceid'] = d.child+d.context.astype(str)+d.sentenceid.astype(str)

    d['clausetype'] = 'SUBORDINATE'
    d.ix[(d.matrix) & (d.subj), 'clausetype'] = 'DECLARATIVE'
    d.ix[(d.matrix) & ~(d.subj), 'clausetype'] = 'IMPERATIVE'

    d = d.drop(['matrix', 'subj'], axis=1)
        
    def preprocess_features(d):
        dropcols = ['pobj'+str(i) for i in range(1,4)]+['child', 'sent', 'context']
        d = d.drop(dropcols, axis=1)

        boolcols = ['prep'+str(i) for i in range(1,4)]
        d[boolcols] = d[boolcols] != 'NONE'

        def comp_map(c):
            if c in ['who', 'what', 'why', 'when', 'where', 'how', 'which']:
                return 'WH'
            elif c in ['whether', 'if']:
                return 'POLAR'
            elif c in ['that', 'like']:
                return 'DECLARATIVE'
            else:
                return 'NONE'

        d['comp'] = d.comp.map(comp_map)
        d['embpred'] = d.embpred != 'NONE'

        return d
    
    if separate_children:
        data = {}
        
        for c in d.child.unique():
            d_proc = preprocess_features(d[d.child==c])
            data[c] = MainClauseData(d_proc, f)

    else:
        d = preprocess_features(d)
        data = MainClauseData(d)
            
    return data

        
if __name__ == '__main__':
    data = main()
