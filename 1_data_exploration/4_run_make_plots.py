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
    
with open('../data/chart_features.pickle', 'rb') as handle:
    chart_features = pickle.load(handle)

with open('../data/chart_names.pickle', 'rb') as handle:
    chart_names = pickle.load(handle)
    
with open('../data/chart_features_chords_distribution.pickle', 'rb') as handle:
    chart_features_chords_distribution = pickle.load(handle)
    
with open('../data/chart_features_chords_transition_matrix_all.pickle', 'rb') as handle:
    chart_features_chords_transition_matrix_all = pickle.load(handle)

# print('making dense array of section_features')
# f = np.zeros( ( len(section_features) , section_features[0].toarray().size ) )
# print('f.shape: ', f.shape)
# for i,s in enumerate(section_features):
#     print( str(i) + '/' + str(len(section_features)) )
#     f[i,:] = s.toarray().astype(np.float32)

# # remove zero columns
# discarded_idx = np.argwhere(np.all(f[..., :] == 0, axis=0))
# f_dense = np.delete(f, discarded_idx, axis=1)
# print('f.shape: ', f_dense.shape)

print('making dense array of chart_features')
t = np.zeros( ( len(chart_features) , chart_features[0].toarray().size ) )
print('t.shape: ', t.shape)
for i,s in enumerate(chart_features):
    print( str(i) + '/' + str(len(chart_features)) )
    t[i,:] = s.toarray().astype(np.float32)

# remove zero columns
discarded_idx = np.argwhere(np.all(t[..., :] == 0, axis=0))
t_dense = np.delete(t, discarded_idx, axis=1)
print('t_dense.shape: ', t_dense.shape)

print('making dense array of chart_features_chords_distribution')
p = np.zeros( ( len(chart_features_chords_distribution) , chart_features_chords_distribution[0].toarray().size ) )
print('p.shape: ', p.shape)
for i,s in enumerate(chart_features_chords_distribution):
    print( str(i) + '/' + str(len(chart_features_chords_distribution)) )
    p[i,:] = s.toarray().astype(np.float32)

# remove zero columns
discarded_idx = np.argwhere(np.all(p[..., :] == 0, axis=0))
distributions_dense = np.delete(p, discarded_idx, axis=1)
print('distributions_dense.shape: ', distributions_dense.shape)

print('making dense array of chart_features_chords_transition_matrix_all')
n = np.zeros( ( len(chart_features_chords_transition_matrix_all) , chart_features_chords_transition_matrix_all[0].toarray().size ) )
print('n.shape: ', n.shape)
for i,s in enumerate(chart_features_chords_transition_matrix_all):
    print( str(i) + '/' + str(len(chart_features_chords_transition_matrix_all)) )
    n[i,:] = s.toarray().astype(np.float32)

# remove zero columns
discarded_idx = np.argwhere(np.all(n[..., :] == 0, axis=0))
transitions_dense = np.delete(n, discarded_idx, axis=1)
print('transitions_dense.shape: ', transitions_dense.shape)
# %% plot sections

#PCA,MDS,NMF,TSNE

from sklearn.manifold import TSNE
from sklearn.manifold import MDS
print('running t-SNE')
# X_embedded = TSNE(n_components=2, init='pca', verbose=2, n_iter=3000).fit_transform(f_dense)



render_MDS_chart_features_chords_distribution = True 
render_MDS_chart_features_chords_transition_matrix_all = True

render_t_SNE_chart_features_chords_distribution = True
render_t_SNE_chart_features_chords_transition_matrix_all = True


if render_MDS_chart_features_chords_distribution:
    X_embedded_MDS_chart_features_chords_distribution = MDS(n_components=2).fit_transform(distributions_dense)
if render_MDS_chart_features_chords_transition_matrix_all:
    X_embedded_MDS_chart_features_chords_transition_matrix_all = MDS(n_components=2).fit_transform(transitions_dense)
    
if render_t_SNE_chart_features_chords_distribution:
    X_embedded_t_SNE_chart_features_chords_distribution = TSNE(n_components=2, init='pca', verbose=2, n_iter=3000).fit_transform(distributions_dense)
if render_t_SNE_chart_features_chords_transition_matrix_all:
    X_embedded_t_SNE_chart_features_chords_transition_matrix_all = TSNE(n_components=2, init='pca', verbose=2, n_iter=3000).fit_transform(transitions_dense)


# plt.clf()
# plt.scatter( X_embedded[:,0], X_embedded[:,1], alpha=0.5, s=3 )
# plt.savefig( '../data/tsne0.png', dpi=500 )

plt.clf()
plt.scatter( X_embedded_MDS_chart_features_chords_distribution[:,0], X_embedded_MDS_chart_features_chords_distribution[:,1], alpha=0.5, s=3 )
plt.savefig( '../data/mds_chart_features_chords_dist.png', dpi=500 )

plt.clf()
plt.scatter( X_embedded_MDS_chart_features_chords_transition_matrix_all[:,0], X_embedded_MDS_chart_features_chords_transition_matrix_all[:,1], alpha=0.5, s=3 )
plt.savefig( '../data/mds_chart_features_chords_trans.png', dpi=500 )

plt.clf()
plt.scatter( X_embedded_t_SNE_chart_features_chords_distribution[:,0], X_embedded_t_SNE_chart_features_chords_distribution[:,1], alpha=0.5, s=3 )
plt.savefig( '../data/tsne_chart_features_chords_dist.png', dpi=500 )

plt.clf()
plt.scatter( X_embedded_t_SNE_chart_features_chords_transition_matrix_all[:,0], X_embedded_t_SNE_chart_features_chords_transition_matrix_all[:,1], alpha=0.5, s=3 )
plt.savefig( '../data/tsne_chart_features_chords_trans.png', dpi=500 )

# %% save
# with open('../data/f_dense.pickle', 'wb') as handle:
#     pickle.dump(f_dense, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('../data/X_embedded.pickle', 'wb') as handle:
#     pickle.dump(X_embedded, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
with open('../data/X_embedded_chart_features_chords_distribution.pickle', 'wb') as handle:
    pickle.dump(X_embedded_MDS_chart_features_chords_distribution, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
with open('../data/X_embedded_chart_features_chords_transition_matrix_all.pickle', 'wb') as handle:
    pickle.dump(X_embedded_MDS_chart_features_chords_transition_matrix_all, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
with open('../data/X_embedded_chart_features_chords_distribution.pickle', 'wb') as handle:
    pickle.dump(X_embedded_t_SNE_chart_features_chords_distribution, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
with open('../data/X_embedded_chart_features_chords_transition_matrix_all.pickle', 'wb') as handle:
    pickle.dump(X_embedded_t_SNE_chart_features_chords_transition_matrix_all, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../data/discarded_idx.pickle', 'wb') as handle:
    pickle.dump(discarded_idx, handle, protocol=pickle.HIGHEST_PROTOCOL)