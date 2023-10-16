import numpy as np
import os
import json
import pickle
import sys
sys.path.append('..' + os.sep +'0_data_preparation')
import CJ_ChartClasses as ccc
import matplotlib.pyplot as plt
import pandas as pd
import aux_output

# %% load pickle

with open('../data/all_melody_structs.pickle', 'rb') as handle:
    all_structs = pickle.load(handle)

with open('../data/globalHMM.pickle', 'rb') as handle:
    globalHMM = pickle.load(handle)
with open('../data/stylesHMM.pickle', 'rb') as handle:
    stylesHMM = pickle.load(handle)

def blend_piece_with_style(piece_idx, style_type, style_subtype, file_name = 'experiment_styles_blend.json'):
    globalHMM.make_group_support()
    # keep chord distributions for counting new chords
    chord_distributions = globalHMM.chords_distribution.toarray()[0]

    # the explanation excels are gathered for each piece and overall
    # as keys in this dictionary
    explain_stats = {}
    tmp_stats = {
        'transitions': 0,
        'constraints': 0,
        'support': 0,
        'normalize': 0,
        'melody_mean': 0,
        'melody_std': 0
    }
    explain_stats['all'] = tmp_stats
    
    s1 = all_structs[piece_idx]

    s2 = stylesHMM[style_type][style_subtype]
    
    print(30*'-')
    print(s1.piece_name)
    print(style_type + ' - ' + style_subtype)

    # construct weighted "blended" transition matrix and get observations

    w1, w2, wGlobal = 0.0, 1.0, 0.0

    t1 = s1.hmm.transition_matrix.toarray()
    s2.make_group_support()
    t2 = s2.group_support
    h2 = s2
    # t2 = s2.hmm.transition_matrix.toarray()
    # tGlobal = globalHMM.transition_matrix.toarray()
    tGlobal = globalHMM.group_support
    trans_probs = (w1*t1 + w2*t2 + wGlobal*tGlobal)/(w1+w2+wGlobal)
    # zero-out t1
    # trans_probs[ t1 > 0 ] = 0
    # normalize
    for i in range(trans_probs.shape[0]):
        if np.sum( trans_probs[i,:] ) > 0:
            trans_probs[i,:] = trans_probs[i,:]/np.sum( trans_probs[i,:] )
    
    # m1 = s1.hmm.melody_per_chord.toarray()
    m2 = s2.melody_per_chord.toarray()
    mGlobal = globalHMM.melody_per_chord.toarray()
    # mel_per_chord_probs = w1*m1 + w2*m2 + wGlobal*mGlobal
    # mel_per_chord_probs = (w1+w2)*m2 + wGlobal*mGlobal
    # mel_per_chord_probs = m2
    mel_per_chord_probs = mGlobal
    for i in range(mel_per_chord_probs.shape[0]):
        if np.sum( mel_per_chord_probs[i,:] ) > 0:
            mel_per_chord_probs[i,:] = mel_per_chord_probs[i,:]/np.sum( mel_per_chord_probs[i,:] )
    
    emissions = s1.melody_information

    constraints = s1.constraints


    # apply HMM
    new_key = 'BL_' + s1.key + '-' + style_type + '_' + style_subtype

    # pathIDXs, delta, psi, markov, obs = s1.hmm.apply_cHMM_with_constraints(trans_probs, mel_per_chord_probs, emissions, constraints, adv_exp=0.0)
    pathIDXs, delta, psi, markov, obs, explain = s1.hmm.apply_cHMM_with_support(trans_probs, mel_per_chord_probs, emissions, constraints, tGlobal, h2, chord_distributions, adv_exp=0.0, make_excel=True, excel_name=new_key + '.xlsx')
    
    # explain structures
    if s1.piece_name not in explain_stats.keys():
        tmp_stats = {
            'transitions': 0,
            'constraints': 0,
            'support': 0,
            'normalize': 0,
            'melody_mean': 0,
            'melody_std': 0
        }
        explain_stats[s1.piece_name] = tmp_stats
    for tmp_label in ['all', s1.piece_name]:
        explain_stats[tmp_label]['transitions'] += len(explain['constraint'])
        explain_stats[tmp_label]['constraints'] += np.sum(explain['constraint'])
        explain_stats[tmp_label]['support'] += np.sum(explain['support'])
        explain_stats[tmp_label]['normalize'] += np.sum(explain['normalize'])
        explain_stats[tmp_label]['melody_mean'] += np.mean(explain['mel_corr'])
        explain_stats[tmp_label]['melody_std'] += np.std(explain['mel_corr'])
    # explain structures

    transp_idxs = s1.transpose_idxs(pathIDXs, s1.tonality['root'])

    debug_constraints = np.array([pathIDXs,constraints])

    generated_chords = s1.idxs2chordSymbols(transp_idxs)

    generated_vs_initial = []
    for i in range(len(generated_chords)):
        generated_vs_initial.append( [constraints[i], generated_chords[i], s1.chords[i].chord_symbol] )

    new_unfolded = s1.substitute_chordSymbols_in_string( s1.unfolded_string, generated_chords )

    # costruct GJT-ready structure

    # new_key = 'BL_' + s1.key + '-' + s2.key

    blended_piece = {
        new_key: {}
    }

    blended_piece[new_key]['string'] = new_unfolded
    blended_piece[new_key]['original_string'] = new_unfolded
    blended_piece[new_key]['unfolded_string'] = new_unfolded
    blended_piece[new_key]['original_string'] = new_key
    blended_piece[new_key]['appearing_name'] = 'BL_' + s1.piece_name + '-' + style_type + '_' + style_subtype
    blended_piece[new_key]['tonality'] = s1.tonality['symbol']

    # # Append string at the end of file
    # file_object.write(repr(blended_piece) + '\n')
    blends = [ blended_piece ]

    # plot - debug
    debug_path = '../figs/experiment_styles_hmm_debug'

    os.makedirs('../figs', exist_ok=True)
    os.makedirs(debug_path, exist_ok=True)

    plt.clf()
    plt.imshow(trans_probs, cmap='gray_r')
    plt.savefig(debug_path + '/trans_probs' + s1.key.replace(' ', '_') + '-' + (style_type + '_' + style_subtype).replace(' ', '_') + '.png', dpi=500)

    plt.clf()
    plt.imshow(delta, cmap='gray_r')
    plt.savefig(debug_path + '/delta' + s1.key.replace(' ', '_') + '-' + (style_type + '_' + style_subtype).replace(' ', '_') + '.png', dpi=500)

    plt.clf()
    plt.imshow(markov, cmap='gray_r')
    plt.savefig(debug_path + '/markov' + s1.key.replace(' ', '_') + '-' + (style_type + '_' + style_subtype).replace(' ', '_') + '.png', dpi=500)

    plt.clf()
    plt.imshow(obs, cmap='gray_r')
    plt.savefig(debug_path + '/obs' + s1.key.replace(' ', '_') + '-' + (style_type + '_' + style_subtype).replace(' ', '_') + '.png', dpi=500)
# end for
    df = pd.DataFrame(explain_stats)
    df.to_excel('../data/explain_styles_stats.xlsx')

    # %%
    blends_dict = {}
    for b in blends:
        blends_dict[ list(b.keys())[0] ] = list(b.values())[0]

    # %%
    with open(file_name, 'w') as outfile:
        json.dump(blends_dict, outfile)
    

    return blended_piece, aux_output.print_ascii_chart(new_unfolded)