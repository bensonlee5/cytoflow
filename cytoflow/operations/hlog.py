from traits.api import HasStrictTraits, Str, List, Float, provides
from .i_operation import IOperation

@provides(IOperation)
class HlogTransformOp(HasStrictTraits):
    """An operation that applies the Hyperlog transformation to channels.
    
    Attributes
    ----------
    name : Str
        The name of the transformation (for UI representation)
        
    channels : List(Str)
        A list of the channels on which to apply the transformation
        
    b: List(Float) (default = 500)
        The point at which the transform transitions from linear to log.
        If the list is empty, the default value of 500 is used.
    
    r: List(Float) (default = 10**4)  
        The maximum of the transformed values.  If the list is empty, the
        default value of 10**4 is used.
    
    References
    ----------
    .. [1] "Hyperlog-a flexible log-like transform for negative, 
           zero, and  positive valued data."
           Bagwell CB.
           Cytometry A. 2005 Mar;64(1):34-42.
           PMID: 15700280 [PubMed - indexed for MEDLINE] 
    """
    
    # traits
    id = "edu.mit.synbio.cytoflow.operations.hlog"
    friendly_id = "Hyperlog"
    name = Str()
    channels = List(Str)
    b = List(Float)
    r = List(Float)
    
    def is_valid(self, experiment):
        """Validate this transform instance against an experiment.
        
        Parameters
        ----------
        experiment : Experiment
            The Experiment against which to validate this op.
            
        Returns
        -------
        True if this is a valid operation on the given experiment; 
        False otherwise.
        """
        
        if not experiment:
            return False
        
        if not self.name:
            return False
        
        if not set(self.channels).issubset(set(experiment.channels)):
            return False
        
        return True
    
    def apply(self, old_experiment):
        """Applies the hlog transform to channels in an experiment.
        
        Parameters
        ----------
        old_experiment : Experiment
            The Experiment on which to apply this transformation.
            
        Returns
        -------
        Experiment
            A new Experiment, identical to old_experiment except for the
            transformed channels.
        """
        
        new_experiment = old_experiment.clone()
        
        for idx, channel in enumerate(self.channels):
            # TODO - probably should change this if the channel range changes
            b = self.b[idx] if self.b else 500
            r = self.r[idx] if self.r else 10**4
            d = np.log10(old_experiment.metadata[channel]['range'])
            
            hlog_fwd = \
                lambda x, b = b, r = r, d = d: hlog(x, b = b, r = r, d = d)
            hlog_rev = \
                lambda y, b = b, r = r, d = d: hlog_inv(y, b = b, r = r, d = d)
                               
            new_experiment[channel] = hlog_fwd(old_experiment[channel])
            
            # TODO - figure out what 
            new_experiment.metadata[channel]["xforms"].append(hlog_fwd)
            new_experiment.metadata[channel]["xforms_inv"].append(hlog_rev)

        return new_experiment
    
    
# the following functions were taken from Eugene Yurtsev's FlowCytometryTools
# http://gorelab.bitbucket.org/flowcytometrytools/
# thanks, Eugene!

import numpy as np
import scipy.optimize

_machine_max = 2**18
_l_mmax = np.log10(_machine_max)
_display_max = 10**4

def hlog_inv(y, b=500, r=_display_max, d=_l_mmax):
    '''
    Inverse of base 10 hyperlog transform.
    '''
    aux = 1.*d/r *y
    s = np.sign(y)
    if s.shape: # to catch case where input is a single number
        s[s==0] = 1
    elif s==0:
        s = 1
    return s*10**(s*aux) + b*aux - s

def _make_hlog_numeric(b, r, d):
    '''
    Return a function that numerically computes the hlog transformation for given parameter values.
    '''
    hlog_obj = lambda y, x, b, r, d: hlog_inv(y, b, r, d) - x
    find_inv = np.vectorize(lambda x: scipy.optimize.brentq(hlog_obj, -2*r, 2*r, 
                                        args=(x, b, r, d)))
    return find_inv 

def hlog(x, b=500, r=_display_max, d=_l_mmax):
    '''
    Base 10 hyperlog transform.

    Parameters
    ----------
    x : num | num iterable
        values to be transformed.
    b : num
        Parameter controling the location of the shift 
        from linear to log transformation.
    r : num (default = 10**4)
        maximal transformed value.
    d : num (default = log10(2**18))
        log10 of maximal possible measured value.
        hlog_inv(r) = 10**d
     
    Returns
    -------
    Array of transformed values.
    '''
    hlog_fun = _make_hlog_numeric(b, r, d)
    if not hasattr(x, '__len__'): #if transforming a single number
        y = hlog_fun(x)
    else:
        n = len(x)
        if not n: #if transforming empty container
            return x
        else:
            y = hlog_fun(x)
    return y

