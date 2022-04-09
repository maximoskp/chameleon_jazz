#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 15:58:11 2021

@author: max
"""

import numpy as np
import os
import json
import pickle
import sys
sys.path.insert(1, '../0_data_preparation')
import CJ_ChartClasses as ccc

# %% load pickle

with open('../data/all_structs.pickle', 'rb') as handle:
    all_structs = pickle.load(handle)

# %% isolate section features

section_names = []
section_features = []

chart_names = []
chart_keys = []
chart_features = []

chart_features_chords_distribution = []
chart_features_chords_transition_matrix_all = []

for i_struct,struct in enumerate(all_structs):
    print('processing (' + str(i_struct) + '/' + str(len(all_structs))  + '): ' + struct.piece_name)
    chart_names.append(struct.piece_name)
    chart_keys.append(struct.key)
    chart_features.append(struct.get_features())
    
for i_struct,struct in enumerate(all_structs):
    print('processing (' + str(i_struct) + '/' + str(len(all_structs))  + '): ' + struct.piece_name)
    # chart_names.append(struct.piece_name)
    chart_features_chords_distribution.append(struct.get_features(chords_transition_matrix_all=False))
    
for i_struct,struct in enumerate(all_structs):
    print('processing (' + str(i_struct) + '/' + str(len(all_structs))  + '): ' + struct.piece_name)
    # chart_names.append(struct.piece_name)
    chart_features_chords_transition_matrix_all.append(struct.get_features(chords_distribution_all=False))

for i_struct,struct in enumerate(all_structs):
    print('processing (' + str(i_struct) + '/' + str(len(all_structs))  + '): ' + struct.piece_name)
    for i,s in enumerate(struct.sections):
        print('section: '+ str(i))
        section_names.append( struct.piece_name + '_section_' + str(i) )
        section_features.append( s.get_features() )

# %% save names and features

with open('../data/section_names.pickle', 'wb') as handle:
    pickle.dump(section_names, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../data/section_features.pickle', 'wb') as handle:
    pickle.dump(section_features, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
with open('../data/chart_names.pickle', 'wb') as handle:
    pickle.dump(chart_names, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../data/chart_keys.pickle', 'wb') as handle:
    pickle.dump(chart_keys, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../data/chart_features.pickle', 'wb') as handle:
    pickle.dump(chart_features, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
with open('../data/chart_features_chords_distribution.pickle', 'wb') as handle:
    pickle.dump(chart_features_chords_distribution, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../data/chart_features_chords_transition_matrix_all.pickle', 'wb') as handle:
    pickle.dump(chart_features_chords_transition_matrix_all, handle, protocol=pickle.HIGHEST_PROTOCOL)

'''
# %% isolate section features

section_names = []
section_features = []

for i_struct,struct in enumerate(all_structs):
    print('processing (' + str(i_struct) + '/' + str(len(all_structs))  + '): ' + struct.piece_name)
    for i,s in enumerate(struct.sections):
        print('section: '+ str(i))
        section_names.append( struct.piece_name + '_section_' + str(i) )
        section_features.append( s.get_features() )

# %% save names and features

with open('../data/section_names.pickle', 'wb') as handle:
    pickle.dump(section_names, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../data/section_features.pickle', 'wb') as handle:
    pickle.dump(section_features, handle, protocol=pickle.HIGHEST_PROTOCOL)
'''