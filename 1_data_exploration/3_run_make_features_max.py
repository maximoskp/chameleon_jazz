#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 11 07:59:35 2022

@author: max
"""

import numpy as np
import os
import json
import pickle
import sys
from scipy import sparse
sys.path.append('..' + os.sep +'0_data_preparation')
import CJ_ChartClasses as ccc

# %% load pickle

with open('../data/all_melody_structs.pickle', 'rb') as handle:
    all_structs = pickle.load(handle)

# %% isolate section features

chart_info_structs = {}
roots = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

# %% feaature extraction

chart_features = np.zeros( (len(all_structs), all_structs[0].get_features(separated=False).size) ).astype(np.float32)
chart_names = []
chart_keys = []

for i,s in enumerate(all_structs):
    print('extracting features from: ' + s.piece_name + ' - (' + str(i+1) + '/' + str(len(all_structs)) + ')')
    chart_features[i,:] = s.get_features(separated=False)
    chart_keys.append(s.key)
    chart_names.append(s.piece_name)
    chart_info_structs[ s.key.replace(' ', '_') ] = {
        'title': s.piece_name,
        'key': s.key,
        'tonality': roots[s.tonality['root']] + ' ' + s.tonality['mode'],
        'style': s.sections[0].style,
        'features': s.get_features(separated=False)
    }

# %% save

path2save = '../data/charts_with_melodies'
os.makedirs('../data', exist_ok=True)
os.makedirs( path2save , exist_ok=True )

with open(path2save + '/chart_names.pickle', 'wb') as handle:
    pickle.dump(chart_names, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open(path2save + '/chart_keys.pickle', 'wb') as handle:
    pickle.dump(chart_keys, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open(path2save + '/chart_info_structs.pickle', 'wb') as handle:
    pickle.dump(chart_info_structs, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open(path2save + '/chart_features.pickle', 'wb') as handle:
    pickle.dump(sparse.csr_matrix(chart_features), handle, protocol=pickle.HIGHEST_PROTOCOL)

# %% do NMF and save
print('running NMF')
from sklearn.decomposition import NMF

nmf_models = []
    
for n_components in range(3,10,1):
    print('n_components: ', n_components)
    model = NMF(n_components=n_components, init='random', random_state=0)
    W = model.fit_transform(chart_features.T)
    H = model.components_
    nmf_model = {
        'W': W,
        'H': H,
        'n_components': n_components
    }
    nmf_models.append( nmf_model )
# end for

with open(path2save + '/nmf_models.pickle', 'wb') as handle:
    pickle.dump(nmf_models, handle, protocol=pickle.HIGHEST_PROTOCOL)

# %% check markov

'''
dummyHMM = None
dummyHMM = ccc.ChameleonHMM()
if len(dummyHMM.all_chord_states) == 0:
    dummyHMM.initialize_chord_states()
dummyHMM.make_empty_matrices()
'''
dummyHMM = ccc.ChameleonHMM()
if len(dummyHMM.all_chord_states) == 0:
    dummyHMM.initialize_chord_states()
for i in range(W.shape[1]):
    dummyHMM.build_from_features(W[:,i])
    dummyHMM.debug_print(filename='nmf_explore/' + 'W_' + str(i+1) + '_of_' + str(W.shape[1]) + '.txt')