#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 20:35:21 2022
@author: konstantinosvelenis
"""

import numpy as np
import os
import json
import pickle
import matplotlib.pyplot as plt
import sys
sys.path.insert(1, '../0_data_preparation')
import CJ_ChartClasses as ccc

# %% load

with open('../data/chart_names.pickle', 'rb') as handle:
    chart_names = pickle.load(handle)
    
with open('../data/chart_features_chords_distribution.pickle', 'rb') as handle:
    chart_features_chords_distribution = pickle.load(handle)
    
with open('../data/chart_features_chords_transition_matrix_all.pickle', 'rb') as handle:
    chart_features_chords_transition_matrix_all = pickle.load(handle)
    
with open('../data/all_structs.pickle', 'rb') as handle:
    all_structs = pickle.load(handle)
    

#making dense array of section_features
n = np.zeros( ( len(chart_features_chords_transition_matrix_all) , chart_features_chords_transition_matrix_all[0].toarray().size ) )
print('n.shape: ', n.shape)
for i,s in enumerate(chart_features_chords_transition_matrix_all):
    #print( str(i) + '/' + str(len(chart_features_chords_transition_matrix_all)) )
    n[i,:] = s.toarray().astype(np.float32)
transitions_dense = n
# remove zero columns
discarded_idx = np.argwhere(np.all(n[..., :] == 0, axis=0))
transitions_dense = np.delete(n, discarded_idx, axis=1)
print('transitions_dense.shape: ', transitions_dense.shape)

# %% NMF

from sklearn.decomposition import NMF

def NMF_preprocessing(x, d):
    model = NMF(n_components=d, init='random', random_state=0)
    W = model.fit_transform(x)
    H = model.components_
    return W
# end NMF_preprocessing

h_trans = NMF_preprocessing(transitions_dense, 10)

# %% save

datapath = 'data/'

with open( datapath + 'h_trans.pickle', 'wb' ) as handle:
    pickle.dump( h_trans, handle, protocol=pickle.HIGHEST_PROTOCOL )


# %%

render_NMF_chart_features_chords_transition_matrix_all = True

def gettopKofmatrix(w, k=4):
    global all_structs
    s0 = all_structs[0]
    chord_names = np.array(s0.get_all_chord_states())
    r = []
    for i in range(w.shape[1]):
        idxs = np.argsort(w[:,i*(-1)-1])[::-1]
        tmpr = chord_names[idxs[:k].astype(int)]
        r.append(tmpr)
    return r  
    
def gettopPercentageofmatrix(w, p=0.9):
    global all_structs
    s0 = all_structs[0]
    chord_names = np.array(s0.get_all_chord_states())
    r = []
    for i in range(w.shape[1]):
        idxs = np.argsort(w[:,i*(-1)-1])[::-1]
        print(np.sum(w[idxs[:],i]))
        sumv = 0
        n = 0
        while sumv < p*np.sum(w[idxs[:],i]):
            sumv += np.sum(w[idxs[n]])
            n += 1
        k = n
        tmpr = chord_names[idxs[:k].astype(int)]
        r.append(tmpr)
    return r

#NMF rendering
if render_NMF_chart_features_chords_transition_matrix_all:
    sum_n = np.sum( n , axis=0 )
    t4nmf = np.reshape( sum_n , (840,840) )
    X = t4nmf
    model = NMF(n_components=3, init='nndsvda', random_state=2, max_iter=5000)
    W = model.fit_transform(X.T)
    H = model.components_
    
    #rt = gettopPercentageofmatrix(W)
    rt = gettopKofmatrix(W)
    
    plt.figure()
    plt.imshow(W,cmap='gray_r',aspect='auto')