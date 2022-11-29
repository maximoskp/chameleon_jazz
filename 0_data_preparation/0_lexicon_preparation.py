#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 10:51:44 2019

@author: maximoskaliakatsos-papakostas
"""

import music21 as m21
import os
import numpy as np
import json
import pickle
import pandas as pd

cwd = os.getcwd()

folder_name = '..' + os.sep + 'data' + os.sep + 'Lexikon'
file_name = 'Lexikon.mxl'

# load file
s = m21.converter.parse( folder_name + os.sep + file_name )
# iterate through parts and fill the dictionary
type2pcs_dictionary = {}
for p in s.parts:
    # get first measure to obtain chord pc
    m = p.getElementsByClass('Measure')
    # get extended chord from 1st measure
    c = m[0].getElementsByClass('Chord')
    if len(c.pitches) > 0:
        pcs = []
        for pitch in c.pitches:
            pcs.append( int( np.mod(pitch.midi , 12 ) ) )
        tmp_type_name = p.partName
        if len(tmp_type_name) == 1:
            tmp_type_name = " "
        else:
            # check if polychord lower
            if tmp_type_name[0] == '/':
                tmp_type_name = '/' + tmp_type_name[2:]
            else:
                tmp_type_name = tmp_type_name[1:]
        
        # modes are not necessary in new version
        tmp_dic = {"extended_type": pcs}
        '''
        # get modes from next measures
        for i in range(5):
            c = m[1+i].getElementsByClass('Chord')
            if len(c) > 0:
                pcs = []
                for pitch in c.pitches:
                    pcs.append( int( np.mod(pitch.midi , 12 ) ) )
                tmp_dic['modes'].append(pcs)
            else:
                break;
        '''
        type2pcs_dictionary[ tmp_type_name ] = tmp_dic
        # print( tmp_type_name + ': ' + repr(tmp_dic['extended_type']) + ' - ' + repr(tmp_dic['modes']) )
        print( tmp_type_name + ': ' + repr(tmp_dic['extended_type']) )

with open( folder_name + os.sep + 'type2pcs_dictionary.json', 'w') as f:
    json.dump(type2pcs_dictionary, f)

print('number of types: ', len( list(type2pcs_dictionary.keys()) ))

# %% form type groups

type_groups = {
    'dominant': {},
    'suspended': {},
    'major': {},
    'minor': {},
    'diminished': {},
    'other': {}
}

type2group = {}

for k in type2pcs_dictionary.keys():
    t = type2pcs_dictionary[k]['extended_type']
    if (4 in t and 10 in t) or (4 in t and 8 in t and not 11 in t):
        type_groups['dominant'][k] = t
        type2group[ str(t) ] = {'group': 'dominant', 'group_idx': 0}
    elif 3 not in t and 4 not in t and 5 in t:
        type_groups['suspended'][k] = t
        type2group[ str(t) ] = {'group': 'suspended', 'group_idx': 1}
    elif 4 in t and 10 not in t:
        type_groups['major'][k] = t
        type2group[ str(t) ] = {'group': 'major', 'group_idx': 2}
    elif 3 in t and 6 not in t:
        type_groups['minor'][k] = t
        type2group[ str(t) ] = {'group': 'minor', 'group_idx': 3}
    elif 3 in t and 6 in t:
        type_groups['diminished'][k] = t
        type2group[ str(t) ] = {'group': 'diminished', 'group_idx': 4}
    else:
        type_groups['other'][k] = t
        type2group[ str(t) ] = {'group': 'other', 'group_idx': 5}
# end for

# sanity check
n = np.sum([len(g) for g in type_groups.values()])
print('number of types in groups: ', n)

with open('../data/type_groups.pickle', 'wb') as handle:
    pickle.dump(type_groups, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('../data/type2group.pickle', 'wb') as handle:
    pickle.dump(type2group, handle, protocol=pickle.HIGHEST_PROTOCOL)

df = pd.DataFrame( type_groups )
df.to_excel('../data/type_groups.xlsx')
