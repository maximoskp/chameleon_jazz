#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 18:56:11 2021

@author: max
"""

import numpy as np
import os
import json
import pickle
import matplotlib.pyplot as plt

# %% load 
print('loading data')
with open('../data/section_names.pickle', 'rb') as handle:
    section_names = pickle.load(handle)

with open('../data/section_features.pickle', 'rb') as handle:
    section_features = pickle.load(handle)

print('making dense array')
f = np.zeros( ( len(section_features) , section_features[0].toarray().size ) )
print('f.shape: ', f.shape)
for i,s in enumerate(section_features):
    print( str(i) + '/' + str(len(section_features)) )
    f[i,:] = s.toarray().astype(np.float32)

# remove zero columns
discarded_idx = np.argwhere(np.all(f[..., :] == 0, axis=0))
f_dense = np.delete(f, discarded_idx, axis=1)
print('f.shape: ', f_dense.shape)
# %% plot sections

from sklearn.manifold import TSNE
print('running t-SNE')
X_embedded = TSNE(n_components=2, learning_rate='auto', init='pca', verbose=2, n_iter=3000).fit_transform(f_dense)

plt.clf()
plt.scatter( X_embedded[:,0], X_embedded[:,1], alpha=0.5, s=3 )
plt.savefig( '../data/tsne0.png', dpi=500 )

# %% save
with open('../data/f_dense.pickle', 'wb') as handle:
    pickle.dump(f_dense, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../data/X_embedded.pickle', 'wb') as handle:
    pickle.dump(X_embedded, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../data/discarded_idx.pickle', 'wb') as handle:
    pickle.dump(discarded_idx, handle, protocol=pickle.HIGHEST_PROTOCOL)