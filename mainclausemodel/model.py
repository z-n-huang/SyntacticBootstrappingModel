import numpy as np
import pandas as pd
import theano.tensor as T

from random import shuffle
from theano import shared, function
from patsy import dmatrix
from collections import defaultdict

class MainClauseModel(object):

    def __init__(self, nlatfeats=8, alpha=1., discount=None, beta=0.5, gamma=0.9,
                 delta=2., orthogonality_penalty=0., nonparametric=False):
        '''
        Parameters
        ----------
        nlatfeats : int
            Number of latent features for each verb; the default of 8 is
            the number of unique subcat frames in the data

        alpha : float (positive)
            Beta process hyperparameter as specified in Teh et al. 2007
            "Stick-breaking Construction for the Indian Buffet Process"; 
            changes meaning based on Pitman-Yor discount hyperparameter 
            (see Teh et al. 2007, p.3)

        discount : float (unit) or None
            If discount is a float, it must satisfy alpha > -discount

        beta : float (positive)
            If parametric=True, concetration parameter for verb-specific 
            beta draws based on beta process sample; if nonparametric=False, 
            hyperparameter of a Beta(beta, beta); in the latter case, beta 
            should be on (0,1), otherwise the verb representations are 
            unidentifiable, since their is a flat prior on the selection
            probability

        gamma : float (positive)
            Hyperparameter of a beta distribution on the projection matrix

        delta : float (positive)
            Hyperparameter of a beta distribution on the verb feature 
            probability matrix

        orthogonality_penalty : float (positive)
            How much to penalize for singularity

        nonparametric : bool
            Whether to use a nonparametric prior

        divergence_weight : float (0 to negative infinity) (ADDED)
            How much to weight the either-or bias. If 0, no either-or bias.
        '''

        self.nlatfeats = nlatfeats
        self.alpha = alpha
        self.discount = discount
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.orthogonality_penalty = orthogonality_penalty
        self.nonparametric = nonparametric
        self.divergence_weight = -1 # For cross-validation: -0.1, -0.5, -1, -5, -10, -100
        
        self._validate_params()

        self._ident = ''.join(np.random.choice(9, size=10).astype(str))

    def _validate_params(self):
        if self.discount is not None:
            self._pitman_yor = True
            
            try:
                assert self.alpha > -self.discount
            except AssertionError:
                raise ValueError('alpha must be greater than -discount')
        else:
            self._pitman_yor = False
            
    def _initialize_model(self, data, stochastic):
        self.data = data

        self._initialize_counter()
        self._initialize_reps()
        self._initialize_loss()
        self._initialize_updaters(stochastic)

    def _initialize_counter(self):
        self._verbcount = T.zeros(self.data.n('verb'))
        self._verbeye = T.eye(self.data.n('verb'))
        
    def _initialize_reps(self):
        self._reps = {}

        if self.nonparametric:
            # nu_aux = np.array([2.]+[-1.]*(self.nlatfeats-1))
            nu_aux = np.array([0.]*self.nlatfeats)

            self._reps['nu'] = shared(nu_aux, name='nu')

            self._nu = T.nnet.sigmoid(self._reps['nu'])
            self._mu = T.cumprod(self._nu)
        
        verbreps_aux = np.random.normal(0., 1e-2, size=[self.data.n('verb')-self.data.n('clausetype'),
                                                         self.nlatfeats])
        projection_aux = np.random.normal(0., 1e-2, size=[self.nlatfeats, self.data.n('feature')])
        verbfeatprob_aux = np.zeros([self.data.n('verb')-self.data.n('clausetype'), self.nlatfeats])-4.

        if self.data.n('clausetype'):
            try:
                assert self.data.n('clausetype') <= self.nlatfeats
            except AssertionError:
                raise ValueError('nlatfeats must be greater than or equal to the number of clausetypes')
            
            ctype_ident = (1.-1e-10)*np.eye(self.data.n('clausetype'))
            ct_aux_vr = np.log(ctype_ident)-np.log(1.-ctype_ident)

            ct_aux_vr = np.concatenate([ct_aux_vr, -np.inf*np.ones([self.data.n('clausetype'),
                                                                    self.nlatfeats-self.data.n('clausetype')])],
                                       axis=1)

            ct_aux_vfp = np.inf*np.ones([self.data.n('clausetype'), self.nlatfeats])


            verbreps_aux = np.concatenate([ct_aux_vr, verbreps_aux])
            verbfeatprob_aux = np.concatenate([ct_aux_vfp, verbfeatprob_aux])
            
        self._reps['verbreps'] = shared(verbreps_aux, name='verbreps')
        self._reps['projection'] = shared(projection_aux, name='projection')        
        self._reps['verbfeatprob'] = shared(verbfeatprob_aux, name='verbfeatprob')

        self._verbreps = T.nnet.sigmoid(self._reps['verbreps'])
        self._projection = T.nnet.sigmoid(self._reps['projection'])
        self._verbfeatprob = T.nnet.sigmoid(self._reps['verbfeatprob'])
        
        softand = self._verbfeatprob[:,:,None]*self._verbreps[:,:,None]*self._projection[None,:,:]
        self._featureprob = 1.-T.prod(1.-softand, axis=1)

    # ADDED: divergence function. Calculates JS-divergence (cf. SciPy version which yields the square root value)
    def _get_js_divergence(self):
        vr = self._verbreps
        assertProb = vr[:, 0]
        requestProb = vr[:, 1]
        m0 = (assertProb + 1-requestProb)/2
        m1 = (1-assertProb + requestProb)/2
        kl_assert = (assertProb * T.log(assertProb / m0) 
                    + (1-assertProb) * T.log((1-assertProb) / m1))
        kl_request = ((1-requestProb) * T.log((1-requestProb) / m0) 
                + requestProb * T.log(requestProb / m1))
        js = ((kl_assert + kl_request) / 2 )**1 
        # Above code leads to NaN error for verbs 0 and 1 (DECLARATIVE & IMPERATIVE), probably because of how Theano deals with floating point representations???
        # These should be 0. Stipulate them as such.
        # cf. https://stackoverflow.com/questions/31919818/theano-sqrt-returning-nan-values. 
        js = T.set_subtensor(js[0], 0.) # try ... js[tuple([0,])], 0...
        js = T.set_subtensor(js[1], 0.)

        return js
		
    # ADDED: divergence function. Calculates KL-divergence
    def _get_kl_divergence(self):
        vr = self._verbreps
        assertProb = vr[:, 0]
        requestProb = vr[:, 1]
        kl_assert = (assertProb * T.log(assertProb / (1-requestProb)) 
                    + (1-assertProb) * T.log((1-assertProb) / requestProb))
        kl_request = ((1-requestProb) * T.log((1-requestProb) / assertProb) 
                + requestProb * T.log(requestProb / (1-assertProb)))
        kl = ((kl_assert + kl_request) / 2 )**1 
        # Above code leads to NaN error for verbs 0 and 1 (DECLARATIVE & IMPERATIVE), probably because of how Theano deals with floating point representations???
        # These should be 0. Stipulate them as such.
        # cf. https://stackoverflow.com/questions/31919818/theano-sqrt-returning-nan-values. 
        kl = T.set_subtensor(kl[0], 0.) # try ... js[tuple([0,])], 0...
        kl = T.set_subtensor(kl[1], 0.)

        return kl                
    def _initialize_loss(self):

        self._log_projection_prior = (self.gamma-1.)*T.log(self._projection) +\
                                     (self.gamma-1.)*T.log(1.-self._projection)

        self._log_verbfeatureprob_prior = (self.delta-1.)*T.log(self._verbfeatprob) +\
                                          (self.delta-1.)*T.log(1.-self._verbfeatprob)
        # self._log_verbfeatureprob_prior = -T.log(self._verbfeatprob)/T.log(self._verbreps)
        
        if self.nonparametric:
            def betaln(alpha, beta):
                return T.gammaln(alpha) + T.gammaln(beta) - T.gammaln(alpha+beta)

            if self._pitman_yor:
                upper_a = self.alpha + self.nlatfeats*self.discount
                upper_b = 1.-self.discount
            else:
                upper_a = 1.
                upper_b = self.alpha

            self._log_upper_prior = (upper_a-1.)*T.log(self._nu) +\
                                    (upper_b-1.)*T.log(1.-self._nu) -\
                                    betaln(upper_a, upper_b)

            lower_a = self.beta*self._mu
            lower_b = self.beta*(1.-self._mu)

            self._log_lower_prior = (lower_a-1.)[None,:]*T.log(self._verbreps) +\
                                    (lower_b-1.)[None,:]*T.log(1.-self._verbreps) -\
                                    betaln(lower_a, lower_b)[None,:]

            self._prior = T.sum(self._log_upper_prior)/self.nlatfeats +\
                          T.sum(self._log_lower_prior)/(self.data.n('verb')*self.nlatfeats) +\
                          T.sum(self._log_projection_prior)/(self.data.n('feature')*self.nlatfeats)+\
                          T.sum(self._log_verbfeatureprob_prior)/(self.data.n('verb')*self.nlatfeats)

        else:
            self._log_verbreps_prior = (self.beta-1.)*T.log(self._verbreps) +\
                                       (self.beta-1.)*T.log(1.-self._verbreps)

            self._prior = T.sum(self._log_verbreps_prior)/(self.data.n('verb')*self.nlatfeats) +\
                          T.sum(self._log_projection_prior)/(self.data.n('feature')*self.nlatfeats)+\
                          T.sum(self._log_verbfeatureprob_prior)/(self.data.n('verb')*self.nlatfeats)

            
        if self.orthogonality_penalty:
            verbrep2 = T.dot(self._verbreps.T, self._verbreps)
            verbrep2_rawsum = T.sum(T.square(verbrep2 - verbrep2*T.identity_like(verbrep2)))
            self._orthogonality_penalty = -self.orthogonality_penalty*\
                                          verbrep2_rawsum/(self.nlatfeats*self.data.n('verb'))
        else:
            self._orthogonality_penalty = 0.	
        
        p = self._featureprob[self.data.verb]
        k = self.data.features
        # r = 1./self._verbreps.sum(axis=1)[self.data.verb,None]

        #self._ll_per_feature = k*T.log(p)+r*T.log(1.-p)+T.gammaln(k+r)-T.gammaln(k+1)-T.gammaln(r)
        self._ll_per_feature = k*T.log(p)+(1.-k)*T.log(1.-p) # log likelihood, by defn. negative (log 1 = 0)

        self._total_ll = T.sum(self._ll_per_feature)/(self.data.verb.shape[0]*\
                                                      self.data.n('feature'))
        self._total_loss = self._prior+self._orthogonality_penalty+self._total_ll
        self._itr = T.ivector('itr')
        
        # Option A: mean of JS divergence for observed verbs
        self._divergence = T.mean(self._get_js_divergence()[self.data.verb][self._itr])*self.divergence_weight
        
        # Option B: mean of KL divergence for observed verbs
        # self._divergence = T.mean(self._get_kl_divergence()[self.data.verb][self._itr])*self.divergence_weight
        
        # Other options:
        # T.mean(self._get_js_divergence()) # Option A1: mean of ALL divergences, regardless of verbs observed for the particular utterance
        # T.mean(self._get_kl_divergence()) # Option B1: mean of ALL divergences, regardless of verbs observed for the particular utterance
        self._itr_ll = T.sum(self._ll_per_feature[self._itr])/self.data.n('feature')
        self._itr_loss = self._prior+self._orthogonality_penalty+self._itr_ll + self._divergence
        #ADDED # Subtract divergence. Effectively, we are taking the raw log-likelihood (_ll_per_feature), a negative value, and adjusting it by this divergence score. Both JSD and KLD yield a positive value. Since the model tries to maximize log-likelihood, we want the adjusted log-likelihood to be lower when the divergence score is high. One way to do so is adjust divergence with a negative weight, effectively subtracting divergence from log-likelihood.
                         
    def _initialize_updaters(self, stochastic):
        update_dict_ada = []

        self.rep_grad_hist_t = {}
        
        for name, rep in self._reps.items():
            if stochastic:
                rep_grad = T.grad(-self._itr_loss, rep)
            else:
                rep_grad = T.grad(-self._total_loss, rep)

            if name in ['verbreps', 'projection', 'verbfeatprob']:
                rep_grad = T.switch((rep>10)*(rep_grad<0),
                                    T.zeros_like(rep_grad),
                                    rep_grad)

                rep_grad = T.switch((rep<-10)*(rep_grad>0),
                                    T.zeros_like(rep_grad),
                                    rep_grad)
                # ADDED; incorporating divergence causes verbreps gradients for DECLARATIVE and IMPERATIVE to equal NaN; so replace NaN with 0s (declaratives and imperative gradients don't change)
                rep_grad = T.switch(T.isnan(rep_grad), 0., rep_grad)
            
            self.rep_grad_hist_t[name] = shared(np.ones(rep.shape.eval()),
                                                name=name+'_hist'+self._ident)

            rep_grad_adj = rep_grad / (T.sqrt(self.rep_grad_hist_t[name]))

            learning_rate = 2.# if name != 'nu' else 1e-20
            
            update_dict_ada += [(self.rep_grad_hist_t[name], self.rep_grad_hist_t[name] +\
                                                             T.power(rep_grad, 2)),
                                (rep, rep - learning_rate*rep_grad_adj)]
            
        self.updater_ada = function(inputs=[self._itr],
                                           outputs=[self._total_ll, self._itr_ll,
                                                    self._verbreps, self._projection, self._divergence],
                                           updates=update_dict_ada,
                                           name='updater_ada'+self._ident)

    def _fit(self, sentid, nupdates, verbose):
        for j, sid in enumerate(sentid):
            idx = self.data.sentence(sid)

            for i in range(nupdates):
                total_loss, itr_loss, verbreps, projection, divergence = self.updater_ada(idx)

            if not j % 10: # NH: originally 10
                self._verbreps_hist.append(verbreps)
                self._projection_hist.append(projection)

            if verbose:
                verb_list = list(self.data.categories('verb')[np.array(self.data.verb)[idx]])

                print('\n', j, '\tloss', np.round(total_loss, 3), '\titr_loss',\
                    np.round(itr_loss,3), '\tdiverge', np.round(divergence, 7), '\t', verb_list,'\n',
                    # ADDED for debugging
                    '\t', verb_list,'\t verb ID', np.array(self.data.verb)[idx],
                    #'\nfp', self._featureprob.eval() #'\njs', divergence, '\nverbrep gradients', self.rep_grad_hist_t['verbreps'].eval()
                    )
                    

        
    def fit(self, data, nepochs=0, niters=20000, nupdates=1, # niters = 20000
            stochastic=True, verbose=True): # DEFAULT verbose = False
        self._initialize_model(data, stochastic)

        sentid = list(self.data.categories('sentenceid'))

        self._verbreps_hist = []
        self._projection_hist = []
        
        if nepochs:
            for e in range(nepochs):
                shuffle(sentid)

                if verbose:
                    print(e)
                    
                self._fit(sentid, nupdates, verbose)
                
        else:
            order = np.random.choice(sentid, size=niters)

            self._fit(order, nupdates, verbose)
            
        return self

    @property
    def verbreps(self):
        return pd.DataFrame(T.nnet.sigmoid(self._reps['verbreps']).eval(),
                            index=self.data.categories('verb'))

    @property
    def verbfeatprob(self):
        return pd.DataFrame(T.nnet.sigmoid(self._reps['verbfeatprob']).eval(),
                            index=self.data.categories('verb'))
    
    @property
    def projection(self):
        return pd.DataFrame(T.nnet.sigmoid(self._reps['projection']).eval(),
                            columns=self.data.feature_names)

    @property
    def verbreps_history(self):
        reps = []
        
        for t, r in enumerate(self._verbreps_hist):
            r = pd.DataFrame(r)
            r['verb'] = self.data.categories('verb')
            r['sentence'] = t

            reps.append(r)
            
        return pd.concat(reps)

    @property
    def projection_history(self):
        reps = []
        
        for t, r in enumerate(self._projection_hist):
            r = pd.DataFrame(r)
            r.columns = self.data.feature_names
            r['sentence'] = t

            reps.append(r)
            
        return pd.concat(reps)
    
    @property
    def feature_prob(self):
        # NH amended
        featprob = pd.DataFrame(self._featureprob.eval(), index=self.data.categories('verb'),
                            columns=self.data.feature_names)
        featprob['verb'] = self.data.categories('verb')
        return featprob #pd.DataFrame(self._featureprob.eval(),
               #             index=self.data.categories('verb'),
               #             columns=self.data.feature_names)
    
def main():
    import data
    
    data = data.main()

    models = {c: MainClauseModel() for c in data.keys()}

    for c, m in models.items():
        print('model-main', c,'\n') #modified
        m.fit(data[c])
        print('\n')

        break
        
    return data, models 
        
if __name__ == '__main__':
    data, models = main()
