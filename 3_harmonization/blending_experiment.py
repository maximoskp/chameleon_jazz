import numpy as np
import os
import json
import pickle
import sys
sys.path.append('..' + os.sep +'0_data_preparation')
import CJ_ChartClasses as ccc
import matplotlib.pyplot as plt

file_name = 'experiment_blends.json'
blends = []
# # Open a file with access mode 'a' or 'w'
# file_object = open(file_name, 'w')

# %% load pickle

with open('../data/all_melody_structs.pickle', 'rb') as handle:
    all_structs = pickle.load(handle)

with open('../data/globalHMM.pickle', 'rb') as handle:
    globalHMM = pickle.load(handle)

# %% load pieces to blend

# i1_pieces and i2_pieces should be of the same length
i1_pieces = [4,13,16,20,23]
i2_pieces = [17,11,12,17,17]

for i in range(len(i1_pieces)):
    # i1 will provide the melody and i2 the heaviest transition probabilities
    i1, i2 = i1_pieces[i], i2_pieces[i]

    s1, s2 = all_structs[i1], all_structs[i2]

    print(s1.piece_name)
    print(s2.piece_name)

    # construct weighted "blended" transition matrix and get observations

    w1, w2, wGlobal = 0.0, 0.99, 0.01

    t1 = s1.hmm.transition_matrix.toarray()
    t2 = s2.hmm.transition_matrix.toarray()
    tGlobal = globalHMM.transition_matrix.toarray()
    trans_probs = (w1*t1 + w2*t2 + wGlobal*tGlobal)/(w1+w2+wGlobal)
    for i in range(trans_probs.shape[0]):
        if np.sum( trans_probs[i,:] ) > 0:
            trans_probs[i,:] = trans_probs[i,:]/np.sum( trans_probs[i,:] )
    
    # m1 = s1.hmm.melody_per_chord.toarray()
    # m2 = s2.hmm.melody_per_chord.toarray()
    mGlobal = globalHMM.melody_per_chord.toarray()
    # mel_per_chord_probs = w1*m1 + w2*m2 + wGlobal*mGlobal
    mel_per_chord_probs = mGlobal
    for i in range(mel_per_chord_probs.shape[0]):
        if np.sum( mel_per_chord_probs[i,:] ) > 0:
            mel_per_chord_probs[i,:] = mel_per_chord_probs[i,:]/np.sum( mel_per_chord_probs[i,:] )
    
    emissions = s1.melody_information

    constraints = s1.constraints


    # apply HMM

    pathIDXs, delta, psi, markov, obs = s1.hmm.apply_cHMM_with_constraints(trans_probs, mel_per_chord_probs, emissions, constraints, adv_exp=0.9)

    transp_idxs = s1.transpose_idxs(pathIDXs, s1.tonality['root'])

    debug_constraints = np.array([pathIDXs,constraints])

    generated_chords = s1.idxs2chordSymbols(transp_idxs)

    generated_vs_initial = []
    for i in range(len(generated_chords)):
        generated_vs_initial.append( [constraints[i], generated_chords[i], s1.chords[i].chord_symbol] )

    new_unfolded = s1.substitute_chordSymbols_in_string( s1.unfolded_string, generated_chords )

    # costruct GJT-ready structure

    new_key = 'BL_' + s1.key + '-' + s2.key

    blended_piece = {
        new_key: {}
    }

    blended_piece[new_key]['string'] = new_unfolded
    blended_piece[new_key]['original_string'] = new_unfolded
    blended_piece[new_key]['unfolded_string'] = new_unfolded
    blended_piece[new_key]['original_string'] = new_key
    blended_piece[new_key]['appearing_name'] = 'BL_' + s1.piece_name + '-' + s2.piece_name
    blended_piece[new_key]['tonality'] = s1.tonality['symbol']

    # # Append string at the end of file
    # file_object.write(repr(blended_piece) + '\n')
    blends.append( blended_piece )

    # plot - debug

    os.makedirs('../figs', exist_ok=True)
    os.makedirs('../figs/experiment_hmm_debug', exist_ok=True)

    plt.clf()
    plt.imshow(trans_probs, cmap='gray_r')
    plt.savefig('../figs/experiment_hmm_debug/trans_probs' + s1.key.replace(' ', '_') + '-' + s2.key.replace(' ', '_') + '.png', dpi=500)

    plt.clf()
    plt.imshow(delta, cmap='gray_r')
    plt.savefig('../figs/experiment_hmm_debug/delta' + s1.key.replace(' ', '_') + '-' + s2.key.replace(' ', '_') + '.png', dpi=500)

    plt.clf()
    plt.imshow(markov, cmap='gray_r')
    plt.savefig('../figs/experiment_hmm_debug/markov' + s1.key.replace(' ', '_') + '-' + s2.key.replace(' ', '_') + '.png', dpi=500)

    plt.clf()
    plt.imshow(obs, cmap='gray_r')
    plt.savefig('../figs/experiment_hmm_debug/obs' + s1.key.replace(' ', '_') + '-' + s2.key.replace(' ', '_') + '.png', dpi=500)
# end for

# # Close the file
# file_object.close()

with open(file_name, 'w') as outfile:
    json.dump(blends, outfile)