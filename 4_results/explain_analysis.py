#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 07:18:06 2022

@author: max
"""

import os
import pickle
import numpy as np
import copy

# %%

with open('../data/explain_stats_s1.pickle', 'rb') as handle:
    s1 = pickle.load(handle)

with open('../data/explain_stats_s2.pickle', 'rb') as handle:
    s2 = pickle.load(handle)

# %% 

keys = list(s1.keys())
song_keys = keys[1:]
s1_keys = list( s1['all'].keys() )

s1_extra_analysis = ['const_over_trans', 'supp_over_trans' ,'snc_over_trans','melmean_over_trans', 'new_over_trans', 'norm_over_trans', 'nnc_over_trans']
extra_offset = len( s1_extra_analysis )

unified_array = np.zeros( (len(keys)-1 , 2*len(s1_keys)+extra_offset ) )

# %%

analysis_keys = copy.deepcopy(s1_keys)
analysis_keys.extend( s1_keys )
analysis_keys.extend( s1_extra_analysis )

# %%

unified_expanded = {}

i = 0
for k in keys:
    unified_expanded[k] = {}
    j = 0
    for s1k in s1_keys:
        if k != 'all':
            unified_array[i,j] = s1[k][s1k]
            unified_array[i,j+len(s1_keys)] = s2[k][s1k]
            unified_expanded[k]['s1_' + s1k] = s1[k][s1k]
            unified_expanded[k]['s2_' + s1k] = s2[k][s1k]
            j += 1
    # end s1_keys
    unified_expanded[k]['const_over_trans'] = s1[k]['constraints']/s1[k]['transitions']
    unified_expanded[k]['supp_over_trans'] = s1[k]['support']/s1[k]['transitions']
    unified_expanded[k]['snc_over_trans'] = s1[k]['suppNotConstraint']/s1[k]['transitions']
    unified_expanded[k]['melmean_over_trans'] = s1[k]['melody_mean']
    unified_expanded[k]['new_over_trans'] = s1[k]['new_chords']/s1[k]['transitions']
    unified_expanded[k]['norm_over_trans'] = s1[k]['normalize']/s1[k]['transitions']
    unified_expanded[k]['nnc_over_trans'] = s1[k]['normNotConstraint']/s1[k]['transitions']
    if k != 'all':
        unified_array[i,j+len(s1_keys)] = unified_expanded[k]['const_over_trans']
        unified_array[i,j+len(s1_keys)+1] = unified_expanded[k]['supp_over_trans']
        unified_array[i,j+len(s1_keys)+2] = unified_expanded[k]['snc_over_trans']
        unified_array[i,j+len(s1_keys)+3] = unified_expanded[k]['melmean_over_trans']
        unified_array[i,j+len(s1_keys)+4] = unified_expanded[k]['new_over_trans']
        unified_array[i,j+len(s1_keys)+5] = unified_expanded[k]['norm_over_trans']
        unified_array[i,j+len(s1_keys)+6] = unified_expanded[k]['nnc_over_trans']
        i += 1
# end keys

# %% 

corrs = np.corrcoef( unified_array.T )

# %% 

compount_idxs = np.arange(2*len(s1_keys), 2*len(s1_keys)+extra_offset, 1, dtype=int)
s2_idxs = np.arange(len(s1_keys), 2*len(s1_keys), 1, dtype=int)
s1_idxs = np.arange(0, len(s1_keys), 1, dtype=int)

f = open("compount_corrs.txt", "w")
i = 2*len(s1_keys)
for ii in range(len(compount_idxs)+1):
    j = 2*len(s1_keys)
    for jj in range(len(compount_idxs)+1):
        if ii == 0:
            if jj != 0:
                f.write( '& ' + analysis_keys[j] )
                j += 1
        else:
            if jj == 0:
                f.write(analysis_keys[i])
            else:
                f.write( '& {x:.2f}'.format(x=corrs[i,j]) )
                j += 1
        f.write('\t')
    # end j
    if ii != 0:
        i += 1
    f.write('\\\\ \n')
# end i
f.close()

f = open("cross_corrs.txt", "w")
i = 0
for ii in range(len(s1_idxs)+1):
    j = len(s1_keys)
    for jj in range(len(s2_idxs)+1):
        if ii == 0:
            if jj != 0:
                f.write( '& ' + analysis_keys[j] )
                j += 1
        else:
            if jj == 0:
                f.write(analysis_keys[i])
            else:
                f.write( '& {x:.2f}'.format(x=corrs[i,j]) )
                j += 1
        f.write('\t')
    # end j
    if ii != 0:
        i += 1
    f.write('\\\\ \n')
# end i
f.close()


# %%

n = 10
supp_over_trans_sort_idxs = np.argsort( unified_array[:, analysis_keys.index('supp_over_trans')] )
top_sup = []
bottom_sup = []

for i in range(n):
    bottom_sup.append(song_keys[supp_over_trans_sort_idxs[i]])
    top_sup.append(song_keys[supp_over_trans_sort_idxs[-1-i]])

mel_sort_idxs = np.argsort( unified_array[:, analysis_keys.index('melody_mean')] )
top_mel = []
bottom_mel = []

for i in range(n):
    bottom_mel.append(song_keys[mel_sort_idxs[i]])
    top_mel.append(song_keys[mel_sort_idxs[-1-i]])


