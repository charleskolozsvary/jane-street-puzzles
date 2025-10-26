import os
import pickle

def sumTuples(t1: tuple[int], t2: tuple[int]) -> tuple[int]:
    assert len(t1) == len(t2), 'lengths of supplied tuples do not match'
    return tuple(sum(z) for z in zip(t1, t2))

def save_variable(pfile, variable):
    os.chdir('saved_variables')
    with open(pfile, 'wb') as f:
        pickle.dump(variable, f)
    os.chdir('..')
        
def load_variable(pfile):
    var = None
    os.chdir('saved_variables')        
    with open(pfile, 'rb') as f:
        var = pickle.load(f)
    os.chdir('..')        
    return var
