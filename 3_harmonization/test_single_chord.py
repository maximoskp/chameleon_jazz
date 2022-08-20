#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 20 16:20:38 2022

@author: max
"""

import numpy as np
import os
import json
import pickle
import sys
sys.path.append('..' + os.sep +'0_data_preparation')
import CJ_ChartClasses as ccc
import copy

# %% load pickle

with open('../data/all_melody_structs.pickle', 'rb') as handle:
    all_structs = pickle.load(handle)

with open('../data/globalHMM.pickle', 'rb') as handle:
    globalHMM = pickle.load(handle)

# %% load piece to change and chord idx to modify

# piece i1 will be selected by the user
i1 = 0

# chord idx to be replaced will be selected by the user
chord2replace_idx = 10

s1 = all_structs[i1]

print(s1.piece_name)

# %% only global transition matrix and get observations

tGlobal = globalHMM.transition_matrix.toarray()

trans_probs = tGlobal

mel_per_chord_probs = s1.hmm.melody_per_chord.toarray()

emissions = s1.melody_information


# %% modify chord

constraints = s1.get_all_chords_idxs().astype(np.int)
# remember which chord to substitute
chord2sub = constraints[chord2replace_idx] # we can keep a list of chords to allow multiple new runs
constraints[chord2replace_idx] = -1

pathIDXs = copy.deepcopy(constraints)
pathIDXs[chord2replace_idx] = chord2sub

adv_exp = 1.0

while pathIDXs[chord2replace_idx] == chord2sub:
    print('adv_exp: ', adv_exp)
    pathIDXs, delta, psi = s1.hmm.apply_cHMM_with_constraints(trans_probs, mel_per_chord_probs, emissions, constraints, adv_exp=adv_exp)
    adv_exp /= 1.5

transp_idxs = s1.transpose_idxs(pathIDXs, s1.tonality['root'])

debug_constraints = np.array([transp_idxs,constraints])

generated_chords = s1.idxs2chordSymbols(transp_idxs)

generated_vs_initial = []
for i in range(len(generated_chords)):
    generated_vs_initial.append( [constraints[i], generated_chords[i], s1.chords[i].chord_symbol] )

new_unfolded = s1.substitute_chordSymbols_in_string( s1.unfolded_string, generated_chords )

# %% costruct GJT-ready structure

new_key = 'MOD_' + s1.key

mod_piece = {
    new_key: {}
}

mod_piece[new_key]['string'] = new_unfolded
mod_piece[new_key]['original_string'] = new_unfolded
mod_piece[new_key]['unfolded_string'] = new_unfolded
mod_piece[new_key]['original_string'] = new_key
mod_piece[new_key]['appearing_name'] = 'MOD_' + s1.piece_name
mod_piece[new_key]['tonality'] = s1.tonality
