#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 16:31:25 2022

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

# %% blending

def blend_by_idx(i1, i2, debug_output=False):
    # i1 will provide the melody and i2 the heaviest transition probabilities
    s1, s2 = all_structs[i1], all_structs[i2]
    w1, w2, wGlobal = 0.1, 0.1, 0.8

    t1 = s1.hmm.transition_matrix.toarray()
    t2 = s2.hmm.transition_matrix.toarray()
    tGlobal = globalHMM.transition_matrix.toarray()

    trans_probs = (w1*t1 + w2*t2 + wGlobal*tGlobal)/(w1+w2+wGlobal)
    mel_per_chord_probs = s1.hmm.melody_per_chord.toarray()
    emissions = s1.melody_information
    constraints = s1.constraints
    
    pathIDXs, delta, psi, markov, obs = s1.hmm.apply_cHMM_with_constraints(trans_probs, mel_per_chord_probs, emissions, constraints, adv_exp=0.5)
    transp_idxs = s1.transpose_idxs(pathIDXs, s1.tonality['root'])

    debug_constraints = np.array([pathIDXs,constraints])
    generated_chords = s1.idxs2chordSymbols(transp_idxs)
    generated_vs_initial = []
    for i in range(len(generated_chords)):
        generated_vs_initial.append( [constraints[i], generated_chords[i], s1.chords[i].chord_symbol] )

    new_unfolded = s1.substitute_chordSymbols_in_string( s1.unfolded_string, generated_chords )
    
    new_key = 'BL_' + s1.key + '-' + s2.key

    blended_piece = {
        new_key: {}
    }
    blended_piece[new_key]['string'] = new_unfolded
    blended_piece[new_key]['original_string'] = new_unfolded
    blended_piece[new_key]['unfolded_string'] = new_unfolded
    blended_piece[new_key]['original_string'] = new_key
    blended_piece[new_key]['appearing_name'] = 'BL_' + s1.piece_name + '-' + s2.piece_name
    blended_piece[new_key]['tonality'] = s1.tonality
    
    if debug_output:
        return blended_piece, debug_constraints, generated_vs_initial
    else:
        return blended_piece
# end blend_by_idx

def blend_by_name(n1, n2, debug_output=False):
    ks = [all_structs[i].key for i in range(len(all_structs))]
    i1 = ks.index(n1)
    i2 = ks.index(n2)
    return blend_by_idx(i1, i2, debug_output=debug_output)
# end blend_by_name

# %% chord substitution

def substitute_chord_by_idx(i1, chord2replace_idx, debug_output=False):
    s1 = all_structs[i1]
    
    tGlobal = globalHMM.transition_matrix.toarray()
    trans_probs = tGlobal
    mel_per_chord_probs = s1.hmm.melody_per_chord.toarray()
    emissions = s1.melody_information
    
    constraints = s1.get_all_chords_idxs()
    # remember which chord to substitute
    chord2sub = constraints[chord2replace_idx] # we can keep a list of chords to allow multiple new runs
    constraints[chord2replace_idx] = -1
    pathIDXs = copy.deepcopy(constraints)
    pathIDXs[chord2replace_idx] = chord2sub

    adv_exp = 1.0

    while pathIDXs[chord2replace_idx] == chord2sub:
        print('adv_exp: ', adv_exp)
        pathIDXs, delta, psi, markov, obs = s1.hmm.apply_cHMM_with_constraints(trans_probs, mel_per_chord_probs, emissions, constraints, adv_exp=adv_exp)
        adv_exp /= 1.5
    
    transp_idxs = s1.transpose_idxs(pathIDXs, s1.tonality['root'])
    debug_constraints = np.array([pathIDXs,constraints])
    generated_chords = s1.idxs2chordSymbols(transp_idxs)
    generated_vs_initial = []
    for i in range(len(generated_chords)):
        generated_vs_initial.append( [constraints[i], generated_chords[i], s1.chords[i].chord_symbol] )
    new_unfolded = s1.substitute_chordSymbols_in_string( s1.unfolded_string, generated_chords )
    
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
    if debug_output:
        return mod_piece, debug_constraints, generated_vs_initial
    else:
        return mod_piece
# end substitute_chord_by_idx

def substitute_chord_by_name(n1, chord2replace_idx, debug_output=False):
    ks = [all_structs[i].key for i in range(len(all_structs))]
    i1 = ks.index(n1)
    return substitute_chord_by_idx(i1, chord2replace_idx, debug_output=debug_output)
# end substitute_chord_by_name
