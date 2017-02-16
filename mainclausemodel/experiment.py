import numpy as np
import pandas as pd

from model import MainClauseModel

class MainClauseExperiment(object):

    def __init__(self, data, seed=25472):
        self._data = data
        self._seed = seed

        np.random.seed(seed)

    def _initialize_models(self):
        self._models = {c: [MainClauseModel()
                            for _ in np.arange(self._niters)]
                        for c in self._data.iterkeys()}

    def run(self, niters=10):
        self._niters = niters
        self._initialize_models()
        
        for c, m in self._models.iteritems():
            for i in np.arange(self._niters):
                print c, i
                m[i].fit(self._data[c])

    @property
    def results(self):
        try:
            return self._results_verbreps, self._results_projection
        except AttributeError:        
            results_verbreps = []
            results_projection = []

            for c, m in self._models.iteritems():
                for i in np.arange(self._niters):        
                    vh = m[i].verbreps_history
                    ph = m[i].projection_history

                    vh['child'] = c
                    ph['child'] = c

                    vh['itr'] = i
                    ph['itr'] = i

                    results_verbreps.append(vh)
                    results_projection.append(ph)

            self._results_verbreps = pd.concat(results_verbreps)
            self._results_projection = pd.concat(results_projection)

            return self._results_verbreps, self._results_projection

def main():
    import data
    
    data = data.main()

    exp = MainClauseExperiment(data)
    exp.run()

    verbreps, projection = exp.results

    verbs = ['want', 'see', 'know', 'think', 'say', 'like', 'tell', 'try', 'need', 'remember']
    
    verbreps[verbreps.verb.isin(verbs)].to_csv('../bin/results/verbreps_results.csv', index=False)
    projection.to_csv('../bin/results/projection_results.csv', index=False)

    return exp

if __name__ == '__main__':
    exp = main()
    
