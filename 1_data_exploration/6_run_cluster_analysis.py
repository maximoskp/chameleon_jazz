import numpy as np
import os
import json
import pickle
import matplotlib.pyplot as plt
import copy
import sys
sys.path.insert(1, '../0_data_preparation')
import CJ_ChartClasses as ccc
import json

# %% load 
print('loading data')
with open('../data/n_clusters.pickle', 'rb') as handle:
    n_clusters = pickle.load(handle)

with open('../data/km_labels.pickle', 'rb') as handle:
    km_labels = pickle.load(handle)

with open('../data/discarded_idx.pickle', 'rb') as handle:
    discarded_idx = pickle.load(handle)

with open('../data/all_structs.pickle', 'rb') as handle:
    all_structs = pickle.load(handle)

with open('../data/f_dense.pickle', 'rb') as handle:
    f_dense = pickle.load(handle)

# %% get labels of features
states = all_structs[0].sections[0].all_chord_states
f_labels = copy.deepcopy( states )
for c1 in states:
    for c2 in states:
        f_labels.extend( [c1 + ' -> ' + c2] )
num_features = len(f_labels) + 12
print('len(states): ', len(states))
print('num_features: ', num_features)

# %% keep undiscarded idxs
undiscarded_idx = np.delete(np.arange( num_features ), discarded_idx)

# print('f_labels: ', f_labels)
print('len(undiscarded_idx): ', len(undiscarded_idx))

# %% define idx for parts of features
chord_idx = np.where(undiscarded_idx < len( states ))[0][-1] + 1
transition_idx = len(undiscarded_idx) - 12

# %% for each cluster
# save figs of rpcps
from pathlib import Path
Path('../data/cluster_rpcp_figs').mkdir(parents=True, exist_ok=True)

cluster_stats = []
for i in range(n_clusters):
    cluster_averages = np.mean( f_dense[ km_labels == i, : ], axis=0 )
    # top 5 chords
    chords_arg_sort = np.argsort( cluster_averages[:chord_idx] )[::-1][:5]
    top_5_chords = []
    for c in chords_arg_sort:
        top_5_chords.append( states[c] )
    # top 5 transitions
    transitions_arg_sort = np.argsort( cluster_averages[chord_idx:transition_idx] )[::-1][:5] + len(states)
    top_5_transitions = []
    for t in transitions_arg_sort:
        top_5_transitions.append( f_labels[t] )
    c_stats = {
        'top_5_chords': top_5_chords,
        'top_5_transitions': top_5_transitions,
        'rpcp': cluster_averages[-12:].tolist()
    }
    plt.clf()
    plt.bar( np.arange(12), c_stats['rpcp'] )
    plt.savefig( '../data/cluster_rpcp_figs/c'+str(i)+'.png', dpi=150 )
    # print('cluster ' + str(i) + ': ' + repr(c_stats))
    cluster_stats.append( c_stats )

with open('../data/cluster_analysis.json', 'w') as fp:
    json.dump(cluster_stats, fp)
