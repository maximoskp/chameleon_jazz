import numpy as np
import os
import json
import pickle
import sys
sys.path.append('..' + os.sep +'0_data_preparation')
import CJ_ChartClasses as ccc

# %% load pickle

with open('../data/all_melody_structs.pickle', 'rb') as handle:
    all_structs = pickle.load(handle)

with open('../data/globalHMM.pickle', 'rb') as handle:
    globalHMM = pickle.load(handle)

# %% load pieces to blend

# i1 will provide the melody and i2 the heaviest transition probabilities
i1, i2 = 4, 17

s1, s2 = all_structs[i1], all_structs[i2]

print(s1.piece_name)
print(s2.piece_name)

# %% construct weighted "blended" transition matrix and get observations

w1, w2, wGlobal = 0.1, 0.1, 0.8

t1 = s1.hmm.transition_matrix.toarray()
t2 = s2.hmm.transition_matrix.toarray()
tGlobal = globalHMM.transition_matrix.toarray()

trans_probs = (w1*t1 + w2*t2 + wGlobal*tGlobal)/(w1+w2+wGlobal)

mel_per_chord_probs = s1.hmm.melody_per_chord.toarray()

emissions = s1.melody_information

constraints = s1.constraints


# %% apply HMM

pathIDXs, delta, psi, markov, obs = s1.hmm.apply_cHMM_with_constraints(trans_probs, mel_per_chord_probs, emissions, constraints, adv_exp=0.9)

transp_idxs = s1.transpose_idxs(pathIDXs, s1.tonality['root'])

debug_constraints = np.array([pathIDXs,constraints])

generated_chords = s1.idxs2chordSymbols(transp_idxs)

generated_vs_initial = []
for i in range(len(generated_chords)):
    generated_vs_initial.append( [constraints[i], generated_chords[i], s1.chords[i].chord_symbol] )

new_unfolded = s1.substitute_chordSymbols_in_string( s1.unfolded_string, generated_chords )

# %% costruct GJT-ready structure

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

# %% plot - debug

import matplotlib.pyplot as plt

os.makedirs('../figs', exist_ok=True)
os.makedirs('../figs/hmm_debug', exist_ok=True)

plt.clf()
plt.imshow(trans_probs, cmap='gray_r')
plt.savefig('../figs/hmm_debug/trans_probs.png', dpi=500)

plt.clf()
plt.imshow(tGlobal, cmap='gray_r')
plt.savefig('../figs/hmm_debug/tGlobal.png', dpi=500)

plt.clf()
plt.imshow(t1, cmap='gray_r')
plt.savefig('../figs/hmm_debug/t1.png', dpi=500)

plt.clf()
plt.imshow(t2, cmap='gray_r')
plt.savefig('../figs/hmm_debug/t2.png', dpi=500)

plt.clf()
plt.imshow(delta, cmap='gray_r')
plt.savefig('../figs/hmm_debug/delta.png', dpi=500)

plt.clf()
plt.imshow(markov, cmap='gray_r')
plt.savefig('../figs/hmm_debug/markov.png', dpi=500)

plt.clf()
plt.imshow(obs, cmap='gray_r')
plt.savefig('../figs/hmm_debug/obs.png', dpi=500)

# %% debug-print top chords and transition

# global
max_idxs = np.unravel_index(np.argmax(tGlobal), tGlobal.shape)
row_global = max_idxs[0]
column_global = max_idxs[1]
print('tGlobal top chords: ')

print('tGlobal top transition: ')
print( globalHMM.idx2chord[row_global] + '->' + globalHMM.idx2chord[column_global] )