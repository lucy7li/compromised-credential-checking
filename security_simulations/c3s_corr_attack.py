import gensim
from gensim.models import FastText
import json
import csv
import time
import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from word2keypress import Keyboard
import pdb
import gensim
import numpy as np
from numpy import dot
from gensim.models.utils_any2vec import _save_word2vec_format, _load_word2vec_format, _compute_ngrams, _ft_hash
from numpy import dot
import numpy as np
import math
from gensim import utils, matutils

  
KB = Keyboard()

model = gensim.models.Word2Vec.load('/hdd/c3s/models/fastText2_keyseq_mincount:10_ngram:1-4_negsamp:5_subsamp:0.001_d:100')
model.init_sims()
def get_vector_ngram(word):
    word_vec = np.zeros(model.wv.vectors_ngrams.shape[1], dtype=np.float32)
  
    ngrams = _compute_ngrams(word, model.wv.min_n, model.wv.max_n)
    ngrams_found = 0
    
    for ngram in ngrams:
        ngram_hash = _ft_hash(ngram) % model.wv.bucket
        if ngram_hash in model.wv.hash2index:
            word_vec += model.wv.vectors_ngrams_norm[model.wv.hash2index[ngram_hash]]
        
            ngrams_found += 1
    if word_vec.any():
        return word_vec / max(1, ngrams_found)
def similarity(word1,word2):
    return dot(matutils.unitvec(get_vector_ngram(word1)), matutils.unitvec(get_vector_ngram(word2)))
def get_vec(word1):
    return matutils.unitvec(get_vector_ngram(word1))

import numpy as np
import pdb

def cal_max(l1,l2,p1,p2):
    #l1 is list of password
    #p1 is the probabilities of that password
    # l2 is the list of password to reorder
    
    v1 = [get_vec(KB.word_to_keyseq(w)) for w in l1]
    v2 = [get_vec(KB.word_to_keyseq(w)) for w in l2]
    #pdb.set_trace()
    a1 = np.array(v1)
    a2 = np.array(v2).T
    prod = a1.dot(a2)
    
    probs = (prod.T * p1).T
    sum_p = probs.sum(axis=0)

    final = np.divide(sum_p,p2)
    
    res = np.array(np.argsort(final)[::-1])
    return np.array(l2)[res]

if __name__ == "__main__":
    res = cal_max(["qwerty","password"]*10000,["Password","timepass"]*10000,[0.001,0.001]*10000)
    print(res)

