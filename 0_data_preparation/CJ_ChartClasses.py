#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 1 2021

@author: maximoskaliakatsos-papakostas
"""

import numpy as np
from itertools import combinations
import os
import json
import music21 as m21
import newGCT as ng
from scipy import sparse
import computeDIC as dic
import copy
import pandas as pd
import pickle

class ChameleonContext:
    # static scope for chord dictionary and initiall (0s) transition matrix
    with open('..' + os.sep + 'data' + os.sep + 'Lexikon' + os.sep + 'type2pcs_dictionary.json') as json_file:
        type2pc = json.load(json_file)
    with open('../data/type_groups.pickle', 'rb') as handle:
        type_groups = pickle.load(handle)
    with open('../data/type2group.pickle', 'rb') as handle:
        type2group = pickle.load(handle)
    type_names = list(type2pc.keys())
    type_names.sort()
    type2index = { k : i for i,k in enumerate(type_names) }
    index2type = { i : k for i,k in enumerate(type_names) }
    accidental_symbols = ['-', 'b', '#']
    # all_chord_states = []
    # TODO: construct root2int for numerical roots
    root2int = {
        'C': 0,
        'B#': 0,
        'C#': 1,
        'Db': 1,
        'D-': 1,
        'D': 2,
        'D#': 3,
        'Eb': 3,
        'E-': 3,
        'E': 4,
        'Fb': 4,
        'F-': 4,
        'F': 5,
        'F#': 6,
        'Gb': 6,
        'G-': 6,
        'G': 7,
        'G#': 8,
        'Ab': 8,
        'A-': 8,
        'A': 9,
        'A#': 10,
        'Bb': 10,
        'B-': 10,
        'B': 11,
        'Cb': 11,
        'C-': 11
    }
    int2root = {
        0: 'C',
        1: 'Db',
        2: 'D',
        3: 'Eb',
        4: 'E',
        5: 'F',
        6: 'Gb',
        7: 'G',
        8: 'Ab',
        9: 'A',
        10: 'Bb',
        11: 'B'
    }
    chord2idx = {}
    idx2chord = {}
    idx2chordSymbol = {}
    idx2chordnp = {}
    all_chord_states = []
    all_states_np = []
    all_chord_symbols = []
    # translation between numeric root/types and chord state (string)
    def chord2state(self, numeric_root=None, numeric_type=None, tonality='estimated_tonality'):
        if numeric_root is None:
            # self refers only to Chord, in this case
            numeric_root = self.relative_root[tonality]
            numeric_type = self.numeric_type
        return str(numeric_root) + ', ' + repr(list(numeric_type))
    # end chord2state
    # key finding
    major_profile = m21.analysis.discrete.KrumhanslSchmuckler().getWeights('major')
    minor_profile = m21.analysis.discrete.KrumhanslSchmuckler().getWeights('minor')
    def tonality_from_pcp( self, pcp ):
        major_corrs = np.zeros(12).astype(np.float32)
        minor_corrs = np.zeros(12).astype(np.float32)
        for i in range(12):
            major_corrs[i] = np.corrcoef( pcp, np.roll( 
                self.major_profile, i ) )[0][1]
            minor_corrs[i] = np.corrcoef( pcp, np.roll( 
                self.minor_profile, i ) )[0][1]
        major_max_idx = np.argmax( major_corrs )
        minor_max_idx = np.argmax( minor_corrs )
        major_max = np.max( major_corrs )
        minor_max = np.max( minor_corrs )
        if major_max > minor_max:
            return {'root': major_max_idx,
                    'mode': 'major',
                    'correlation': major_max}
        else:
            return {'root': minor_max_idx,
                    'mode': 'minor',
                    'correlation': minor_max}
    # end tonality_from_pcp
    def tonality_from_symbol( self, s ):
        root_idx = 1
        if len(s) > 1 and s[1] in self.accidental_symbols:
            root_idx = 2
        mode = 'major'
        if s[root_idx-1:] == 'm':
            mode = 'minor'
        return {'root': self.root2int[s[:root_idx]], 'mode':mode, 'symbol': s}
    # end tonality_from_symbol
    
    def make_empty_chords_distribution(self):
        chords_distribution = np.zeros( 12*len(list(self.type2pc.keys())) )
    # end make_empty_chords_distribution

    def initialize_chord_states(self):
        # self.all_chord_states = []
        # self.all_states_np = []
        for i in range(12):
            for k in self.type2pc.keys():
                v = self.type2pc[k]
                tmp_chord_state = self.chord2state(numeric_root=i, numeric_type=v['extended_type'], tonality= "piece_tonality" )
                self.all_chord_states.append( tmp_chord_state )
                self.all_states_np.append( np.fromstring( tmp_chord_state.replace(' ', '').replace('[', '').replace(']', '') , dtype=int, sep=',' ) )
                self.all_chord_symbols.append( str(self.int2root[i]) + k )
        for i in range( len(self.all_chord_states) ):
            self.chord2idx[self.all_chord_states[i]] = i
            self.idx2chord[i] = self.all_chord_states[i]
            self.idx2chordnp[i] = self.all_states_np[i]
            self.idx2chordSymbol[i] = self.all_chord_symbols[i]
    # end initialize_chord_states

    def compute_dic_value(self, c1, c2, d):
        b = False
        p1 = np.mod( c1[0]+c1[1:], 12 )
        p2 = np.mod( c2[0]+c2[1:], 12 )
        v,ids = dic.computeDICfromMIDI(p1,p2)
        if v[ np.where( ids == d )[0][0] ] > 0:
            b = True
        return b
    # end compute_dic_value
    
    def idxs2chords(self, idxs):
        if len(self.idx2chord) == 0:
            self.initialize_chord_states()
        c = []
        for i in idxs:
            c.append( self.idx2chord[int(i)] )
        return c
    # end idxs2chords
    
    def idxs2chordSymbols(self, idxs):
        if len(self.idx2chord) == 0:
            self.initialize_chord_states()
        c = []
        for i in idxs:
            c.append( self.idx2chordSymbol[int(i)] )
        return c
    # end idxs2chordSymbols
    
    def idxs2chordsnp(self, idxs):
        if len(self.idx2chord) == 0:
            self.initialize_chord_states()
        c = []
        for i in idxs:
            c.append( self.idx2chordnp[int(i)] )
        return c
    # end idxs2chordsnp
    
    def transpose_idxs(self, idxs_in, root_number):
        if len(self.all_chord_states) == 0:
            self.initialize_chord_states()
        return ( np.array(idxs_in) + root_number*len(self.type2pc.keys()) )%len(self.all_chord_states)
    # end transpose_idxs
    
    def substitute_chordSymbols_in_string(self, unfolded_string, chordSymbols):
        # first, remove melody
        unfolded_split = unfolded_string.split('melody~[')
        unfolded_no_melody = [ unfolded_split[0] ]
        for i in range(1, len(unfolded_split), 1):
            end_split = unfolded_split[i].split('end],')
            unfolded_no_melody.append( end_split[1] )
        unfolded_string_no_melody = ''.join( unfolded_no_melody )
        chordsplit = unfolded_string_no_melody.split('chord~')
        newsplit = [chordsplit[0]]
        for i in range(len(chordsplit) - 1):
            c = chordsplit[i+1]
            atsplit = c.split('@')
            newsplit.append( '@'.join([ chordSymbols[i] , atsplit[1] ]) )
        out_string = 'chord~'.join( newsplit )
        # we don't need the first bar if it only inlcludes melody before the
        # chords begin
        if out_string.startswith('bar~'):
            # check if section starts the string
            if 'section~' in out_string:
                if out_string.index('section~') < out_string.index('style~'):
                    out_split = out_string.split('section~')
                    out_string = 'section~'.join( out_split[1:] )
                else:
                    out_split = out_string.split('style~')
                    out_string = 'style~'.join( out_split[1:] )
            else:
                out_split = out_string.split('style~')
                out_string = 'style~'.join( out_split[1:] )
        return out_string
    # end substitute_chordSymbols_in_string
    
    def chord_state2root_type_group(self, s):
        r = int( s.split(', ')[0] )
        t = ', '.join( s.split(', ')[1:] )
        g = self.type2group[t]['group_idx']
        return r, g
    # end chord_state2root_type_group
# end ChameleonContext

class ChameleonHMM(ChameleonContext):
    def __init__(self):
        # rows: 840, columns: 12
        self.melody_per_chord = sparse.csr_matrix( np.zeros( (len(self.all_chord_states), 12) ) )
        # 840x840
        self.transition_matrix = sparse.csr_matrix( np.zeros( (len(self.all_chord_states), len(self.all_chord_states)) ) )
        # starting and ending probs
        self.starting = sparse.csr_matrix( np.ones( len(self.all_chord_states) )/len(self.all_chord_states ) )
        self.ending = sparse.csr_matrix( np.ones( len(self.all_chord_states) )/len(self.all_chord_states ) )
        # chords distribution
        self.chords_distribution = sparse.csr_matrix( np.zeros( len(self.all_chord_states) ) )
    # end init
    
    def make_empty_matrices(self):
        # rows: 840, columns: 12
        self.melody_per_chord = sparse.csr_matrix( np.zeros( (len(self.all_chord_states), 12) ) )
        # 840x840
        self.transition_matrix = sparse.csr_matrix( np.zeros( (len(self.all_chord_states), len(self.all_chord_states)) ) )
        # starting and ending probs
        self.starting = sparse.csr_matrix( np.ones( len(self.all_chord_states) )/len(self.all_chord_states ) )
        self.ending = sparse.csr_matrix( np.ones( len(self.all_chord_states) )/len(self.all_chord_states ) )
        # chords distribution
        self.chords_distribution = sparse.csr_matrix( np.zeros( len(self.all_chord_states) ) )
    # end make_empty_matrices

    def add_melody_information_with_chords(self, chords):
        self.melody_per_chord = self.melody_per_chord.toarray()
        for chord in chords:
            idx = self.chord2idx[ chord.chord_state ]
            # also enable chord rpcp information
            self.melody_per_chord[idx,:] += chord.melody_information + 0.1*chord.rpcp['piece_tonality']
            # self.melody_per_chord[idx,:] += chord.melody_information['piece_tonality']
        for i in range( self.melody_per_chord.shape[0] ):
            if np.sum( self.melody_per_chord[i,:] ) != 0:
                self.melody_per_chord[i,:] /= np.sum( self.melody_per_chord[i,:] )
        self.melody_per_chord = sparse.csr_matrix( self.melody_per_chord )
    # end add_melody_information_with_chords

    def add_melody_information_with_matrix(self, m):
        self.melody_per_chord = self.melody_per_chord.toarray()
        self.melody_per_chord += m
        for i in range( self.melody_per_chord.shape[0] ):
            if np.sum( self.melody_per_chord[i,:] ) != 0:
                self.melody_per_chord[i,:] /= np.sum( self.melody_per_chord[i,:] )
        self.melody_per_chord = sparse.csr_matrix( self.melody_per_chord )
    # end add_melody_information_with_matrix

    def add_transition_information(self, t):
        self.transition_matrix = self.transition_matrix.toarray()
        self.transition_matrix += t
        for i in range(self.transition_matrix.shape[0]):
            if np.sum( self.transition_matrix[i,:] ) != 0:
                self.transition_matrix[i,:] /= np.sum( self.transition_matrix[i,:] )
        self.transition_matrix = sparse.csr_matrix( self.transition_matrix )
    # end add_transition_information
    
    def apply_cHMM_with_constraints(self, trans_probs, mel_per_chord_probs, emissions, constraints, adv_exp = 0.0):
        markov = copy.deepcopy( trans_probs )
        obs = np.matmul( mel_per_chord_probs , emissions )
        # apply adventure
        # markov = adv_exp*np.power(markov, adv_exp) + (1-adv_exp)*np.power(np.random.rand( markov.shape[0], markov.shape[1] ), 1-adv_exp)
        # obs = adv_exp*np.power(obs, adv_exp) + (1-adv_exp)*np.power(np.random.rand( obs.shape[0], obs.shape[1] ), 1-adv_exp)
        markov = (1-adv_exp)*markov + adv_exp*(np.random.rand( markov.shape[0], markov.shape[1] )+1)/2.
        obs = (1-adv_exp)*obs + adv_exp*(np.random.rand( obs.shape[0], obs.shape[1] )+1)/2.
        '''
        Do not smooth, to check where dead-ends occur
        # smooth obs
        obs[ obs == 0 ] = 0.00000001
        # smooth markov
        markov[ markov == 0 ] = 0.00000001
        '''
        constraints = constraints.astype(int)
        '''
        # neutralise diagonal
        for i in range(markov.shape[0]):
            markov[i,i] = 0.000000001*markov[i,i]
        '''
        # re-normalise
        for i in range(markov.shape[0]):
            if np.sum( markov[i,:] ) > 0:
                markov[i,:] = markov[i,:]/np.sum( markov[i,:] )
        for i in range(obs.shape[0]):
            if np.sum( obs[i,:] ) > 0:
                obs[i,:] = obs[i,:]/np.sum( obs[i,:] )
        # beginning chord probabilities
        pr = self.starting.toarray()
        delta = np.zeros( ( markov.shape[0] , obs.shape[1] ) )
        psi = np.zeros( ( markov.shape[0] , obs.shape[1] ) )
        pathIDXs = np.zeros( obs.shape[1] )
        t = 0
        delta[:,t] = np.multiply( pr , obs[:,t] )
        if constraints[0] != -1:
            delta[:,t] = np.zeros( markov.shape[0] )
            delta[ constraints[0], t ] = 1
        else:
            if np.sum(delta[:,t]) != 0:
                delta[:,t] = delta[:,t]/np.sum(delta[:,t])
        
        psi[:,t] = 0 # arbitrary value, since there is no predecessor to t=0
        
        for t in range(1, obs.shape[1], 1):
            if constraints[t] == -1 :
                for j in range(0, markov.shape[0]):
                    tmp_trans_prob = markov[:,j]
                    # if np.sum( tmp_trans_prob ) != 0:
                    #     tmp_trans_prob = tmp_trans_prob/np.sum( tmp_trans_prob )
                    delta[j,t] = np.max( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] )
                    psi[j,t] = np.argmax( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] ).astype(int)
                if np.sum(delta[:,t]) != 0:
                    delta[:,t] = delta[:,t]/np.sum(delta[:,t])
            else:
                j = int(constraints[t])
                # tmp_trans_prob = markov[:,j]
                # straight zero
                # tmp_trans_prob = np.ones( markov[:,j].size )*0.000000001
                tmp_trans_prob = np.zeros( markov[:,j].size )
                tmp_trans_prob[j] = 1
                # check if previous is constrained and leave a corridor
                if t > 0:
                    if constraints[t-1] != -1:
                        delta[ j ,t-1 ] = 1
                tmp_trans_prob = tmp_trans_prob/np.sum(tmp_trans_prob)
                delta[j,t] = np.max( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] )
                psi[j,t] = np.argmax( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] ).astype(int)
                if np.sum(delta[:,t]) != 0:
                    delta[:,t] = delta[:,t]/np.sum(delta[:,t])
            # report zeros
            if np.sum(delta[:,t]) == 0:
                print('HMM zero probability encoundered for t = ', t)
        # end for t
        if constraints[-1] == -1:
            pathIDXs[obs.shape[1]-1] = int(np.argmax(delta[:,obs.shape[1]-1]))
        else:
            pathIDXs[obs.shape[1]-1] = int(constraints[-1])
        
        for t in range(obs.shape[1]-2, -1, -1):
            pathIDXs[t] = int(psi[ int(pathIDXs[t+1]) , t+1 ])
        # print('pathIDXs: ', pathIDXs)
        '''
        gcts_out = []
        gct_labels_out = []
        for i in range( len(pathIDXs) ):
            gcts_out.append( maf.str2np(c.gcts_labels[ int(pathIDXs[i]) ]) )
            gct_labels_out.append( c.gcts_labels[ int(pathIDXs[i]) ] )
        '''
        return pathIDXs, delta, psi, markov, obs
    # end apply_cHMM_with_constraints
    
    def apply_cHMM_with_support(self, trans_probs, mel_per_chord_probs, emissions, constraints, support, hmm, adv_exp = 0.0, make_excel=True, excel_name='test_explain.xlsx'):
        markov = copy.deepcopy( trans_probs )
        # penalize non-existent melodic notes
        mel_per_chord_probs[ mel_per_chord_probs <= .01 ] = -100
        obs = np.matmul( mel_per_chord_probs , emissions )
        obs[obs < 0] = 0
        # apply adventure
        # markov = adv_exp*np.power(markov, adv_exp) + (1-adv_exp)*np.power(np.random.rand( markov.shape[0], markov.shape[1] ), 1-adv_exp)
        # obs = adv_exp*np.power(obs, adv_exp) + (1-adv_exp)*np.power(np.random.rand( obs.shape[0], obs.shape[1] ), 1-adv_exp)
        markov = (1-adv_exp)*markov + adv_exp*(np.random.rand( markov.shape[0], markov.shape[1] )+1)/2.
        obs = (1-adv_exp)*obs + adv_exp*(np.random.rand( obs.shape[0], obs.shape[1] )+1)/2.
        if make_excel:
            self.explain = {
                'constraint': [],
                'support': [],
                'normalize': [],
                'sel_chord': [],
                'trans_prob': [],
                'mel_corr': [],
                'song_mel': [],
                'chord_mel': [],
                'mel_match': []
            }
            explain_trans_probs = np.zeros( ( markov.shape[0] , obs.shape[1] ) )
            explain_mel_corrs = np.zeros( ( markov.shape[0] , obs.shape[1] ) )
            explain_constraints = np.zeros( obs.shape[1], dtype=bool )
            explain_support = np.zeros( obs.shape[1], dtype=bool )
            explain_normalize = np.zeros( obs.shape[1], dtype=bool )
        else:
            self.explain = None
        # end if make_excel
        '''
        Do not smooth, to check where dead-ends occur
        # smooth obs
        obs[ obs == 0 ] = 0.00000001
        # smooth markov
        markov[ markov == 0 ] = 0.00000001
        '''
        constraints = constraints.astype(int)
        '''
        # neutralise diagonal
        for i in range(markov.shape[0]):
            markov[i,i] = 0.000000001*markov[i,i]
        '''
        # re-normalise
        for i in range(markov.shape[0]):
            if np.sum( markov[i,:] ) > 0:
                markov[i,:] = markov[i,:]/np.sum( markov[i,:] )
        '''
        for i in range(obs.shape[0]):
            if np.sum( obs[i,:] ) > 0:
                obs[i,:] = obs[i,:]/np.sum( obs[i,:] )
        '''
        # beginning chord probabilities
        pr = self.starting.toarray()
        delta = np.zeros( ( markov.shape[0] , obs.shape[1] ) )
        psi = np.zeros( ( markov.shape[0] , obs.shape[1] ) )
        pathIDXs = np.zeros( obs.shape[1] )
        t = 0
        delta[:,t] = np.multiply( pr , obs[:,t] )
        # ============== EXPLAIN ================
        if make_excel:
            explain_trans_probs[:,t] = pr
            explain_mel_corrs[:,t] = obs[:,t]
        # end if make_excel
        # ============== EXPLAIN ================
        if constraints[0] != -1:
            delta[:,t] = np.zeros( markov.shape[0] )
            # delta[ constraints[0], t ] = 1
            # get group of constraint
            gc = hmm.groups_dictionary[ repr( self.chord_state2root_type_group( self.idx2chord[constraints[0]] ) ) ]
            for j in gc:
                delta[j,t] = 1
            delta[:,t] = np.multiply( delta[:,t] , obs[:,t] )
            # ============== EXPLAIN ================
            if make_excel:
                explain_constraints[t] = 1
            # end if make_excel
            # ============== EXPLAIN ================
        else:
            if np.sum(delta[:,t]) != 0:
                delta[:,t] = delta[:,t]/np.sum(delta[:,t])
        
        psi[:,t] = 0 # arbitrary value, since there is no predecessor to t=0
        
        for t in range(1, obs.shape[1], 1):
            # print('---------- t: ', t)
            if constraints[t] == -1 :
                for j in range(0, markov.shape[0]):
                    tmp_trans_prob = markov[:,j]
                    # if np.sum( tmp_trans_prob ) != 0:
                    #     tmp_trans_prob = tmp_trans_prob/np.sum( tmp_trans_prob )
                    delta[j,t] = np.max( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] )
                    psi[j,t] = np.argmax( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] ).astype(int)
                    # ============== EXPLAIN ================
                    if make_excel:
                        explain_trans_probs[j,t] = tmp_trans_prob[ int(psi[j,t]) ]
                        explain_mel_corrs[j,t] = obs[j,t]
                    # end if make_excel
                    # ============== EXPLAIN ================
                if np.sum(delta[:,t]) != 0:
                    delta[:,t] = delta[:,t]/np.sum(delta[:,t])
                else:
                    # print('HMM zero probability encoundered for t = ', t)
                    # print('Employing support')
                    # ============== EXPLAIN ================
                    if make_excel:
                        explain_support[t] = True
                    # end if make_excel
                    # ============== EXPLAIN ================
                    for j in range(0, markov.shape[0]):
                        tmp_trans_prob = support[:,j]
                        delta[j,t] = np.max( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] )
                        psi[j,t] = np.argmax( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] ).astype(int)
                        # ============== EXPLAIN ================
                        if make_excel:
                            explain_trans_probs[j,t] = tmp_trans_prob[ int(psi[j,t]) ]
                            explain_mel_corrs[j,t] = obs[j,t]
                        # end if make_excel
                        # ============== EXPLAIN ================
                    if np.sum(delta[:,t]) != 0:
                        delta[:,t] = delta[:,t]/np.sum(delta[:,t])
                        # print('FIXED with support - 1')
                    else:
                        # print('STILL ZERO AFTER SUPPORT - smoothing')
                        # print( 'np.max(delta[:,t-1]): ', np.max(delta[:,t-1]) )
                        # print( 'np.argmax(delta[:,t-1]): ', np.argmax(delta[:,t-1]) )
                        # print( 'np.sum(delta[:,t-1]): ', np.sum(delta[:,t-1]) )
                        # ============== EXPLAIN ================
                        if make_excel:
                            explain_normalize[t] = True
                        # end if make_excel
                        # ============== EXPLAIN ================
                        tmp_trans_prob = np.ones( support[:,j].size )/support[:,j].size
                        for j in range(0, markov.shape[0]):
                            delta[j,t] = np.max( np.multiply(delta[:,t-1] + 0.0000001, tmp_trans_prob)*(obs[j,t] + 0.0000001) )
                            psi[j,t] = np.argmax( np.multiply(delta[:,t-1] + 0.0000001, tmp_trans_prob)*(obs[j,t] + 0.0000001) ).astype(int)
                            # ============== EXPLAIN ================
                            if make_excel:
                                explain_trans_probs[j,t] = tmp_trans_prob[ int(psi[j,t]) ]
                                explain_mel_corrs[j,t] = obs[j,t]
                            # end if make_excel
                            # ============== EXPLAIN ================
                        if np.sum(delta[:,t]) != 0:
                            delta[:,t] = delta[:,t]/np.sum(delta[:,t])
                        else:
                            pass
                            # print('----------- now it shouldnt be zero ------------- somethings wrong')
            else:
                # j = int(constraints[t])
                # get group of constraint
                gc = hmm.groups_dictionary[ repr( self.chord_state2root_type_group( self.idx2chord[constraints[t]] ) ) ]
                # ============== EXPLAIN ================
                if make_excel:
                    explain_constraints[t] = 1
                # end if make_excel
                # ============== EXPLAIN ================
                # check if previous is constrained - if so no need to compute
                if constraints[t-1] != -1:
                    # delta[ j ,t ] = 1
                    # psi[j,t] = int(constraints[t-1])
                    # print('constraint after constraint')
                    # since previous is constraint, transitions don't matter
                    previous_for_all = np.argmax(delta[:,t-1])
                    for j in gc:
                        delta[j,t] = obs[j,t]
                        psi[j,t] = previous_for_all
                        # ============== EXPLAIN ================
                        if make_excel:
                            explain_trans_probs[j,t] = 1
                            explain_mel_corrs[j,t] = obs[j,t]
                        # end if make_excel
                        # ============== EXPLAIN ================
                    if np.sum(delta[:,t]) != 0: # couldn't be otherwise
                        delta[:,t] = delta[:,t]/np.sum(delta[:,t])
                else:
                    tmp_trans_prob = markov[:,j]
                    for j in gc:
                        delta[j,t] = np.max( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] )
                        psi[j,t] = np.argmax( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] ).astype(int)
                        # ============== EXPLAIN ================
                        if make_excel:
                            explain_trans_probs[j,t] = tmp_trans_prob[ int(psi[j,t]) ]
                            explain_mel_corrs[j,t] = obs[j,t]
                        # end if make_excel
                    # ============== EXPLAIN ================
                    if np.sum(delta[:,t]) != 0:
                        delta[:,t] = delta[:,t]/np.sum(delta[:,t])
                    else:
                        # print('support with constraint')
                        # ============== EXPLAIN ================
                        if make_excel:
                            explain_support[t] = True
                        # end if make_excel
                        # ============== EXPLAIN ================
                        tmp_trans_prob = support[:,j]
                        for j in gc:
                            delta[j,t] = np.max( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] )
                            psi[j,t] = np.argmax( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] ).astype(int)
                            # ============== EXPLAIN ================
                            if make_excel:
                                explain_trans_probs[j,t] = tmp_trans_prob[ int(psi[j,t]) ]
                                explain_mel_corrs[j,t] = obs[j,t]
                            # end if make_excel
                            # ============== EXPLAIN ================
                        if np.sum(delta[:,t]) == 0:
                            # print('FAILED - smoothening support')
                            # ============== EXPLAIN ================
                            if make_excel:
                                explain_normalize[t] = True
                            # end if make_excel
                            # ============== EXPLAIN ================
                            tmp_trans_prob = np.ones(support[:,j].size)/support[:,j].size
                            tmp_trans_prob = tmp_trans_prob/np.sum(tmp_trans_prob)
                            for j in gc:
                                delta[j,t] = np.max( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] )
                                psi[j,t] = np.argmax( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] ).astype(int)
                                # ============== EXPLAIN ================
                                if make_excel:
                                    explain_trans_probs[j,t] = tmp_trans_prob[ int(psi[j,t]) ]
                                    explain_mel_corrs[j,t] = obs[j,t]
                                # end if make_excel
                                # ============== EXPLAIN ================
        # code at the end was here
        # end for t
        '''
        if constraints[-1] == -1:
            pathIDXs[obs.shape[1]-1] = int(np.argmax(delta[:,obs.shape[1]-1]))
        else:
            pathIDXs[obs.shape[1]-1] = int(constraints[-1])
        '''
        pathIDXs[obs.shape[1]-1] = int(np.argmax(delta[:,obs.shape[1]-1]))
        
        for t in range(obs.shape[1]-2, -1, -1):
            pathIDXs[t] = int(psi[ int(pathIDXs[t+1]) , t+1 ])
        # print('pathIDXs: ', pathIDXs)
        # ============== EXPLAIN ================
        if make_excel:
            np.set_printoptions(precision=2)
            if len(self.all_chord_symbols) == 0:
                self.initialize_chord_states()
            for t in range( len(pathIDXs) ):
                pIDX = int(pathIDXs[t])
                self.explain['constraint'].append(explain_constraints[t])
                self.explain['support'].append(explain_support[t])
                self.explain['normalize'].append(explain_normalize[t])
                self.explain['sel_chord'].append(self.all_chord_states[ pIDX ])
                self.explain['trans_prob'].append(explain_trans_probs[ pIDX , t ])
                self.explain['mel_corr'].append(explain_mel_corrs[ pIDX , t ])
                self.explain['song_mel'].append(repr( emissions[:,t] ).replace('array(','').replace(')',''))
                self.explain['chord_mel'].append(repr( mel_per_chord_probs[ pIDX ,:] ).replace('array(','').replace(')',''))
                self.explain['mel_match'].append(repr( emissions[:,t]*mel_per_chord_probs[ pIDX ,:] ).replace('array(','').replace(')',''))
            df = pd.DataFrame( self.explain )
            os.makedirs('explain_hmm', exist_ok=True)
            if excel_name is not None:
                df.to_excel('explain_hmm/' + excel_name, sheet_name='test_explain')
        # end if make_excel
        # ============== EXPLAIN ================
        '''
        gcts_out = []
        gct_labels_out = []
        for i in range( len(pathIDXs) ):
            gcts_out.append( maf.str2np(c.gcts_labels[ int(pathIDXs[i]) ]) )
            gct_labels_out.append( c.gcts_labels[ int(pathIDXs[i]) ] )
        '''
        return pathIDXs, delta, psi, markov, obs, self.explain
    # end apply_cHMM_with_support
    
    def add_starting_chord_distribution(self, c):
        self.starting = self.starting.toarray()
        self.starting += c
        self.starting = sparse.csr_matrix( self.starting )
    # end add_starting_chord
    
    def add_ending_chord_distribution(self, c):
        self.ending = self.ending.toarray()
        self.ending += c
        self.ending = sparse.csr_matrix( self.ending )
    # end add_ending_chord
    
    def add_chord_distribution(self, c):
        self.chords_distribution = self.chords_distribution.toarray()
        self.chords_distribution += c
        self.chords_distribution = sparse.csr_matrix( self.chords_distribution )
    # end add_chord_distribution
    
    def debug_print(self, filename='hmm_debug.txt'):
        file_object = open(filename, 'w')
        file_object.write( '=========================================== \n')
        file_object.write( '=================DISTRIBUTIONS============= \n')
        file_object.write( '=========================================== \n')
        tmp_distr = self.chords_distribution.toarray().squeeze()
        idxs = np.argsort( tmp_distr )[::-1]
        i = 0
        while tmp_distr[idxs[i]] > 0:
            file_object.write( repr(self.all_states_np[idxs[i]]) + ': ' + '{:.4f}'.format(tmp_distr[idxs[i]]) + '\n')
            i += 1
        file_object.write( '=========================================== \n')
        file_object.write( '=================TRANSITIONS=============== \n')
        file_object.write( '=========================================== \n')
        # print non-zero transitions
        tmp_trans = self.transition_matrix.toarray()
        # sort_idxs = np.unravel_index(np.argsort(tmp_trans), tmp_trans.shape)
        sort_idxs = np.dstack(np.unravel_index(np.argsort(tmp_trans.ravel())[::-1], tmp_trans.shape))
        row = sort_idxs[0][:,0]
        col = sort_idxs[0][:,1]
        i = 0
        while tmp_trans[ row[i], col[i] ] > 0:
            file_object.write( repr(self.all_states_np[row[i]]) + ' -> ' + repr(self.all_states_np[col[i]]) + ': ' + '{:.4f}'.format(tmp_trans[row[i], col[i]]) + '\n')
            i += 1
        '''
        for i in range(tmp_trans.shape[0]):
            for j in range(tmp_trans.shape[1]):
                if tmp_trans[i,j] > 0:
                    file_object.write( repr(self.all_states_np[i]) + ' -> ' + repr(self.all_states_np[j]) + ': ' + '{:.4f}'.format(tmp_trans[i, j]) + '\n')
        '''
        file_object.write( '=========================================== \n')
        file_object.write( '==================MELODIES================= \n')
        file_object.write( '=========================================== \n')
        tmp_mel = self.melody_per_chord.toarray()
        for i in range(tmp_mel.shape[0]):
            if np.sum(tmp_mel[i,:]) > 0:
                file_object.write( repr(self.all_states_np[i]) + ': ' + repr( ['{:.2f}'.format(tmp_mel[i, j]) for j in range(12)] ) + '\n')
        file_object.close()
    # end debug_print
    
    def build_from_features(self, f, dshape=(840,1), tshape=(840,840), mshape=(840,12)):
        dsize = np.prod(dshape)
        tsize = np.prod(tshape)
        # msize = np.prod(mshape)
        self.chords_distribution = sparse.csr_matrix( f[:dsize] )
        self.transition_matrix = sparse.csr_matrix( np.reshape( f[dsize:(dsize+tsize)], tshape ) )
        self.melody_per_chord = sparse.csr_matrix( np.reshape( f[(dsize+tsize):], mshape ) )
    # end build_from_features
    
    def make_group_support(self):
        # matrix for group transitions
        self.group_support = np.zeros( self.transition_matrix.shape )
        # dictionary with key repr( (root_value , group_id ) )
        # and value a list with the indexes of all chords within the group
        self.groups_dictionary = {}
        # temporary matrix for making group support
        tmp_support = np.zeros( self.transition_matrix.shape )
        if len(self.all_chord_states) == 0:
            self.initialize_chord_states()
        # matrix for facilitating (root_value , group_id ) chord group identification
        self.group_idx_per_state = np.zeros( ( len(self.all_chord_states) , 2 ) )
        for i in range( len(self.all_chord_states) ):
            s = self.all_chord_states[i]
            # get (root_value , group_id ) representation
            rt = self.chord_state2root_type_group(s)
            r = rt[0]
            t = rt[1]
            self.group_idx_per_state[i,0] = r
            self.group_idx_per_state[i,1] = t
            # append to dictionary
            if repr(rt) not in self.groups_dictionary.keys():
                self.groups_dictionary[repr(rt)] = [i]
            else:
                self.groups_dictionary[repr(rt)].append(i)
        # make rows of group transitions matrix
        for i in range( self.transition_matrix.shape[0] ):
            idxs = np.logical_and( self.group_idx_per_state[:,0] ==self.group_idx_per_state[i,0] , self.group_idx_per_state[:,1] ==self.group_idx_per_state[i,1] )
            tmp_support[:,i] = np.reshape(np.sum( self.transition_matrix[:,idxs] , axis=1 ), self.group_support[:,i].shape)
        # make columns of group transitions matrix
        for i in range( self.transition_matrix.shape[0] ):
             idxs = np.logical_and( self.group_idx_per_state[:,0] ==self.group_idx_per_state[i,0] , self.group_idx_per_state[:,1] ==self.group_idx_per_state[i,1] )
             self.group_support[i,:] = np.reshape(np.sum( tmp_support[idxs,:] , axis=0 ), self.group_support[i,:].shape)
        # normalize
        for i in range( self.group_support.shape[0] ):
            if np.sum( self.group_support[i,:] ) != 0:
                self.group_support[i,:] /= np.sum( self.group_support[i,:] )
    # end make_group_support
# end ChameleonHMM

class Chord(ChameleonContext):
    def __init__(self, chord_in, piece_tonality=None):
        #print('Chord - chord_in: ', chord_in)
        at_split = chord_in.split('@')
        self.chord_symbol = at_split[0]
        comma_split = at_split[1].split(',')
        self.onset_in_measure = float(comma_split[0])
        self.onset_in_chart = None # TODO: __GIANNOS__ assign in chart
        # symbolic root
        root_idx = 1
        if len(self.chord_symbol) > 1 and self.chord_symbol[1] in self.accidental_symbols:
            root_idx = 2
        self.symbolic_root = self.chord_symbol[:root_idx]
        # get bass
        has_nine = False
        if '/9' in self.chord_symbol:
            has_nine = True
        bass_split = self.chord_symbol[root_idx:].split('/')
        # TODO: fix polychords
        if has_nine:
            self.symbolic_type = ('/').join(bass_split[:2])
        else:    
            self.symbolic_type = bass_split[0]
        if self.symbolic_type == '':
            self.symbolic_type = ' '
        self.pc_set = self.type2pc[ self.symbolic_type ]
        # TODO:
        # get numeric root - check ChameleonContext: root2ind
        self.numeric_root = self.root2int[ self.symbolic_root ]
        self.numeric_type = np.array( 
            self.type2pc[ self.symbolic_type ]['extended_type'] )
        # get pcp
        self.pcp = np.zeros(12).astype(np.float32)
        self.pcp[ np.mod(self.numeric_root + self.numeric_type , 12) ] = 1
        self.pitch_collection = np.mod(np.array(self.pc_set['extended_type']) + self.numeric_root, 12)
        self.gct = ng.GCT_sum_all_from_root( self.pitch_collection )
        
        s = list(combinations(self.numeric_type, 2))
        # __@GIANNOS__ OLD only ascending intervals are generated, is it correct?
        # e.g. only (0,4)->4-0=4 is generated, not (4,0)->0-4=8
        self.interval_vector = np.zeros(12)
        for i in s:
            interval = (i[1]-i[0])%12
            self.interval_vector[interval] += 1
        self.bass_symbol = ''
        if (len( bass_split ) > 1 and not has_nine) or (len( bass_split ) > 2 and has_nine):
            if has_nine:
                self.bass_symbol = bass_split[2]
            else:
                self.bass_symbol = bass_split[1]
            # get bass pitch class
            self.bass_pitch_class = self.root2int[ self.bass_symbol ]
            self.pcp[ self.bass_pitch_class ] = 1
        self.melody_information = None
        if piece_tonality is not None:
            self.piece_tonality = piece_tonality
            self.relative_root = {
                'piece_tonality': (self.numeric_root -self.piece_tonality['root'])%12,
                'estimated_tonality': None
            }
            self.chord_state = self.chord2state(tonality='piece_tonality')
            self.state_np = np.fromstring( self.chord_state[1:-1].replace(' ', '') , dtype=int, sep=',' )
        # discuss polychords...
        # constraint information
        self.isSectionLast = False
        self.isSectionFirst = False
        self.isBarQuadrupleLast = False
        self.isBarOctupleLast = False
        self.isSectionPenultimate = False
    # end __init__

    def set_tonalities(self, piece_tonality=None, estimated_tonality=None, states_tonality='piece_tonality'):
        # print('Chord - set_tonalities')
        if piece_tonality is not None:
            self.piece_tonality = piece_tonality
            if not hasattr(self, 'relative_root'):
                self.relative_root = {
                    'piece_tonality': (self.numeric_root -self.piece_tonality['root'])%12,
                }
            else:
                self.relative_root['piece_tonality'] = (self.numeric_root -self.piece_tonality['root'])%12
        if estimated_tonality is not None:
            self.estimated_tonality = estimated_tonality
            if not hasattr(self, 'relative_root'):
                self.relative_root = {
                'estimated_tonality': (self.numeric_root -self.estimated_tonality['root'])%12
            }
            else:
                self.relative_root['estimated_tonality'] = (self.numeric_root -self.estimated_tonality['root'])%12
        self.chord_state = self.chord2state(tonality=states_tonality)
        self.state_np = np.fromstring( self.chord_state.replace(' ', '').replace('[', '').replace(']', '') , dtype=int, sep=',' )
        # get piece and estimated tonality-relative pitch class set
        self.rpcp = {
            'piece_tonality': np.zeros(12).astype(np.float32),
            'estimated_tonality': np.zeros(12).astype(np.float32)
        }
        self.rpcp['piece_tonality'][ np.mod(self.relative_root['piece_tonality'] + self.numeric_type, 12) ] = 1
        self.rpcp['estimated_tonality'][ np.mod(self.relative_root['estimated_tonality'] + self.numeric_type, 12) ] = 1
        # get GCT
        self.gct_piece_tonality = ng.GCT_in_key(self.pitch_collection, self.piece_tonality['root'])
        self.gct_estimated_tonality = ng.GCT_in_key(self.pitch_collection, self.estimated_tonality['root'])
        if (self.melody_information is None):
            self.melody_information = self.rpcp[states_tonality] # assign default or Chord class here
        else:
            # tune melody to tonality
            self.melody_information  = np.roll( self.melody_information, -self.piece_tonality['root'] )
            # if no melody exist under the chord, fill it with chord info
            if np.sum(self.melody_information) == 0:
                self.melody_information = self.rpcp[states_tonality]
            else:
                self.melody_information = self.melody_information/np.sum(self.melody_information)
                # the strategy below is very narrowing
                # self.melody_information = .5*self.melody_information/np.sum(self.melody_information) + .5*self.rpcp[states_tonality]
        # if bass
        # get bass PIECE tonality-relative pitch class
        # get bass ESTIMATED tonality-relative pitch class
    # end set_tonalities

    def set_default_melody_info_with_tonality( self, t ):
        # TODO: __GIANNOS__ self.melody_information here
        pass
    # end set_default_melody_info_with_tonality
# end Chord

class Measure:
    # purpose: make it easier to unfold chart
    def __init__(self, measure_in):
        self.time_signature = measure_in.split(',')[0]
        self.make_chords( measure_in )
        self.make_melody_information( measure_in )
        if len(self.melody_onsets) > 0:
            self.assign_melody_to_chord()
            # self.assign_melody_to_chord( measure_in )
        # TODO:
        # get position in section
        # get position in chart
        # get has repeat start
        # get has repeat end
        # get has volta X start
        # get if it has time signature change
        # get time signature(s)
        # get if it has section change
        # get if it has style change
    # end __init__
    
    def make_chords(self, measure_in):
        # print('Measure - make_chords')
        chords_split = measure_in.split('chord~')
        self.chords = []
        for c in chords_split[1:]:
            #print(c)
            self.chords.append( Chord( c ) )
    # end make_chords

    def make_melody_information(self, measure_in):
        # get numerator for ignoring "four-and"
        ts_num = int(self.time_signature.split('/')[0])
        melody_split = measure_in.split('melody~[')
        self.melody_information = []
        self.melody_onsets = []
        for mel in melody_split[1:]:
            pitches = mel.split(',end]')[0]
            pitches_split = pitches.split('pitch~')
            for p in pitches_split[1:]:
                comma_split = p.split(',')[0]
                at_split = comma_split.split('@')
                # get tmp pitch and onset, and decide whether it's going to be
                # included, based on the "four-and" exclusion principle
                tmp_pitch = int(at_split[0])
                if '/' in at_split[1]: # case for fractional values in melody like in tuplets, e.g. 2/3
                    a, b = at_split[1].split('/')
                    tmp_onset = float(int(a) / int(b))
                else:
                    tmp_onset = float(at_split[1])
                # four-and exception
                if tmp_onset < ts_num - 0.5:
                    self.melody_information.append( tmp_pitch ) # pitch information per measure
                    self.melody_onsets.append( tmp_onset )
            # MIDI pitches into pcp distribution
            self.melody_pcp = np.zeros(12).astype(np.float32) 
            pitch_class, counts = np.unique(np.mod(self.melody_information,12), return_counts = True)
            for i in range(len(pitch_class)):
                self.melody_pcp[pitch_class[i]] = counts[i]
    # end make_melody_information
            
    def assign_melody_to_chord(self):  # Doesn't account for held durations
        self.melody_per_chord = []
        self.melody_pcp_per_chord = []
        onsets = np.array(self.melody_onsets)
        for ch in reversed(self.chords): # start from last chord
            chord_melody_information = []
            onset_location = np.where( ch.onset_in_measure <= onsets)[0] # maybe >= AND !reversed
            for o in onset_location:
                chord_melody_information.append( self.melody_information[o] )
            self.melody_per_chord.append( chord_melody_information )
            chord_melody_pcp = np.zeros(12).astype(np.float32) 
            pitch_class, counts = np.unique(np.mod(chord_melody_information,12), return_counts = True)
            for i in range(len(pitch_class)):
                chord_melody_pcp[pitch_class[i]] = counts[i]
            self.melody_pcp_per_chord.append( chord_melody_pcp )
            onsets = np.delete(onsets, onset_location) # remove the assigned onsets
        self.melody_per_chord.reverse()
        self.melody_pcp_per_chord.reverse()
        for i,chord in enumerate(self.chords):
            chord.melody_information = self.melody_pcp_per_chord[i]
    # def update_chord_positions(self):
    #     # print('TODO: update position_in_piece for chords')
    # # end update_chord_positions
# end Measure

class ChordTransition(ChameleonContext):
    def __init__(self, first_chord=None, second_chord=None):
        self.first_chord = first_chord
        self.second_chord = second_chord
        self.occurrences = 1
        self.label = self.first_chord.chord_state + '_' + self.second_chord.chord_state
        # TODO:
        # keep information from chord transitions that are relevant to blending
        # Blending information is available after tonality is made known
        if hasattr(first_chord, 'state_np') and hasattr(second_chord, 'state_np'):
            self.make_blending_properties()
    # end __init__

    def make_blending_properties(self):
        self.properties_list = ['from_chord_np', 'to_chord_np', 'from_rpc', 'to_rpc', 'dic_has_0', 'dic_has_1', 'dic_has_N1', 'asc_semitone_to_root', 'desc_semitone_to_root', 'semitone_to_root']
        # remember to retrive object property from string of attribute as:
        # attr = getattr( obj, STR_ATTR )
        c1_np = self.first_chord.state_np
        c2_np = self.second_chord.state_np
        self.from_chord_np = {
            'property': c1_np,
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'chord_name',
            'necessary': True,
        }
        self.to_chord_np = {
            'property': c2_np,
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'chord_name',
            'necessary': True
        }
        self.from_rpc = {
            'property': np.mod( c1_np[0]+c1_np[1:], 12 ),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'subset_match',
            'necessary': True
        }
        self.to_rpc = {
            'property': np.mod( c2_np[0]+c2_np[1:], 12 ),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'subset_match',
            'necessary': True,
        }
        self.dic_has_0 = {
            'property': self.compute_dic_value( c1_np, c2_np, 0 ),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'boolean',
            'necessary': False,
        }
        self.dic_has_1 = {
            'property': self.compute_dic_value( c1_np, c2_np, 1 ),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'boolean',
            'necessary': False,
        }
        self.dic_has_N1 = {
            'property': self.compute_dic_value( c1_np, c2_np, -1 ),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'boolean',
            'necessary': False,
        }
        self.asc_semitone_to_root = {
            'property': (11 in c1_np) and (0 in c2_np),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'boolean',
            'necessary': False,
        }
        self.desc_semitone_to_root = {
            'property': (1 in c1_np) and (0 in c2_np),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'boolean',
            'necessary': False,
        }
        self.semitone_to_root = {
            'property': ( (1 in c1_np) and (0 in c2_np) ) or ( (11 in c1_np) and (0 in c2_np) ),
            'priority_idiom': 0,
            'priority_other': 0,
            'priority': 0,
            'matching': 'boolean',
            'necessary': False,
        }
        self.blending_score = 0
# end ChordTransition

class Section(ChameleonContext):
    def __init__(self, section_in, piece_tonality):
        # meta data
        self.symbol = section_in[0]
        self.style = ''
        style_idx = section_in.find('style~')
        if style_idx != -1:
            style_split = section_in.split('style~')
            comma_split = style_split[1].split(',')
            self.style = comma_split[0]
        # content
        self.make_measures( section_in )
        # possibly need to extract_pcp HERE
        # possibly need to compute_tonality HERE
        # and put the following in a function called by Chart
        # possibly need to assign_section_tonality_to_chords HERE
        self.make_chords()
        self.make_pcp()
        self.piece_tonality = piece_tonality
        self.estimated_tonality = self.tonality_from_pcp( self.pcp )
        self.rpcp = {
            'estimated_tonality': np.roll( self.pcp, -self.estimated_tonality['root'] ),
            'piece_tonality': np.roll( self.pcp, -self.piece_tonality['root'] )
        }
        self.assign_tonalities_to_chords()
        self.make_chord_transitions()
        self.make_stats()
        #print(section_in)
        # keep cadences
    # end __init__
    
    def make_measures(self, section_in):
        # print('Section - make_measures')
        measures_split = section_in.split('bar~')
        self.measures = []
        for m in measures_split[1:]:
            #print('measure: ', m)
            self.measures.append( Measure( m ) )
    # end make_measures
    
    def make_chords(self):
        # print( 'Section - make chords' )
        self.chords = []
        for i,m in enumerate(self.measures):
            for j,c in enumerate(m.chords):
                if i%4 == 0 and j==len(m.chords)-1:
                    c.isBarQuadrupleLast = True
                if i%8 == 0 and j==len(m.chords)-1:
                    c.isBarOctupleLast = True
                self.chords.append( c )
        if len( self.chords ) > 0:
            self.chords[0].isSectionFirst = True
            self.chords[-1].isSectionLast = True
        if len( self.chords ) > 1:
            self.chords[0].isSectionPenultimate = True
        self.number_of_chords = len(self.chords)
    # end make_chords
    
    def make_pcp(self):
        # print('Section - make pcp')
        self.pcp = np.zeros(12).astype(np.float32)
        for c in self.chords:
            self.pcp += c.pcp
        if np.sum(self.pcp) != 0:
            self.pcp /= np.sum(self.pcp)
    # end make_pcp
    
    def assign_tonalities_to_chords(self):
        # print('Section - assign_tonalities_to_chords')
        for c in self.chords:
            c.set_tonalities(piece_tonality=self.piece_tonality,
                             estimated_tonality=self.estimated_tonality)
    # end assign_tonalities_to_chords
    
    def make_chord_transitions(self):
        # print('Section - make_chord_transitions')
        self.chord_transitions = []
        if len( self.chords ) > 1:
            for i in range( len( self.chords ) - 1 ):
                prv = self.chords[i]
                nxt = self.chords[i+1]
                self.chord_transitions.append( ChordTransition( 
                    first_chord=prv, second_chord=nxt ) )
    # end make_chord_transitions
    
    def make_stats(self):
        # print('Sections - make_stats')
        self.chords_distribution = np.zeros( len(self.all_chord_states) ).astype(np.float32)
        self.chord_transition_matrix = np.zeros( (len(self.all_chord_states), len(self.all_chord_states) ) ).astype(np.float32)
        # makes both chord distribution and transition matrix
        self.chords_distribution[ self.all_chord_states.index( self.chords[0].chord_state ) ] += 1
        for t in self.chord_transitions:
            self.chords_distribution[ self.all_chord_states.index( t.second_chord.chord_state ) ] += 1
            self.chord_transition_matrix[ 
                self.all_chord_states.index( t.first_chord.chord_state ),
                self.all_chord_states.index( t.second_chord.chord_state )] += 1
        # normalize
        if np.sum( self.chords_distribution ) != 0:
            self.chords_distribution /= np.sum( self.chords_distribution )
        for i in range(self.chord_transition_matrix.shape[0]):
            if np.sum( self.chord_transition_matrix[i,:] ) != 0:
                self.chord_transition_matrix[i,:] /= np.sum( self.chord_transition_matrix[i,:] )
        self.chords_distribution = sparse.csr_matrix( self.chords_distribution )
        self.chord_transition_matrix = sparse.csr_matrix( self.chord_transition_matrix )
    # end make_stats
    
    def process_section(self):
        self.extract_pcp()
        self.compute_tonality()
    # end process_section
    
    def get_features(self, chords_distribution=True, chord_transition_matrix=True, rpcp='estimated_tonality'):
        f = np.array([])
        if chords_distribution:
            f = np.r_[ f , self.chords_distribution.toarray().astype(np.float32).reshape(len(self.all_chord_states)) ]
        if chord_transition_matrix:
            t = self.chord_transition_matrix.toarray().astype(np.float32)
            f = np.r_[ f , t.reshape(len(self.all_chord_states)**2) ]
        if rpcp is not None:
            f = np.r_[ f , self.rpcp[rpcp] ]
        return sparse.csr_matrix(f)
    # end get_features
# end Section

class Chart(ChameleonContext):
    def __init__(self, struct_in):
        if len( self.all_chord_states ) == 0:
            self.initialize_chord_states()
        # meta data
        self.unfolded_string = struct_in['unfolded_string']
        self.string = struct_in['string']
        self.piece_name = struct_in['appearing_name']
        self.key = struct_in['original_key']
        self.tonality = self.tonality_from_symbol( struct_in['tonality'] )
        self.make_sections()
        self.make_stats()        
        # do we need to keep:
        # chords with their time in chart (if we happen to need harmonic rhythm)
        self.make_chords()
        self.make_constraints()
        self.make_melody_information()
        self.make_transitions()
        # TODO: self.make_starting_ending_information()
        self.hmm = ChameleonHMM()
        self.hmm.add_melody_information_with_chords( self.chords )
        self.hmm.add_transition_information( self.chord_transition_matrix.toarray() )
        self.hmm.add_chord_distribution( self.chords_distribution.toarray() )
        # TODO: add chord distribution
    # end __init__
    
    def make_sections(self):
        # print('Chart - make_sections')
        # split sections
        sections_split = self.unfolded_string.split('section~')
        self.sections = []
        for s in sections_split[min(1, len(sections_split)-1):]:
            #print('making section: ', s)
            self.sections.append( Section( s, self.tonality ) )
            # print('self.sections: ', self.sections)
    # end make_sections
    
    def make_stats(self):
        # make transitions matrix from all sections and get total number of chords
        self.number_of_chords = 0
        self.chords_distribution = np.zeros( len(self.all_chord_states) ).astype(np.float32)
        self.chord_transition_matrix = np.zeros( (len(self.all_chord_states), len(self.all_chord_states) ) ).astype(np.float32)
        for s in self.sections:
            self.number_of_chords += s.number_of_chords
            self.chords_distribution += s.number_of_chords*s.chords_distribution.toarray().squeeze()
            self.chord_transition_matrix += s.number_of_chords*s.chord_transition_matrix.toarray().squeeze()
        # normalize
        if np.sum( self.chords_distribution ) != 0:
            self.chords_distribution /= np.sum( self.chords_distribution )
        for i in range(self.chord_transition_matrix.shape[0]):
            if np.sum( self.chord_transition_matrix[i,:] ) != 0:
                self.chord_transition_matrix[i,:] /= np.sum( self.chord_transition_matrix[i,:] )
        self.chords_distribution = sparse.csr_matrix( self.chords_distribution )
        self.chord_transition_matrix = sparse.csr_matrix( self.chord_transition_matrix )
    # end make_stats
    
    def make_stats_old(self):
        self.number_of_chords = 0
        # gather chord_distribution info
        chord_distr_sum = 0
        testnormalization = 0     
        for s in self.sections:
            chord_distr_sum += s.number_of_chords
            self.number_of_chords += s.number_of_chords
        for s in self.sections:
            s.cx = sparse.coo_matrix(s.chords_distribution)
            s.s0 = s.cx.tocsr()
            for i,j,v in zip(s.cx.row, s.cx.col, s.cx.data): 
                s.s0[i,j] = (v * len(s.chords))  
        sumarr = self.sections[0].s0           
        for i in range(1, len(self.sections), 1):
            sumarr += self.sections[i].s0
        self.chords_distribution_all = sumarr
        k = sparse.coo_matrix(self.chords_distribution_all)
        k.k0 = k.tocsr()
        rowsum = np.zeros(np.shape(k.k0)[0])
        for i,j,v in zip(k.row, k.col, k.data):      
            rowsum[i] = k.k0[i].sum()   
        for i,j,v in zip(k.row, k.col, k.data):
            k.k0[i,j] = v / rowsum[i]  
        self.chords_distribution_all = k.k0
        
        #gather chord_transition_matrix info
        chord_trans_sum = 0        
        for p in self.sections:
            p.cx = sparse.coo_matrix(p.chord_transition_matrix)
            p.p0 = p.cx.tocsr()
            chord_trans_sum += len(p.chord_transitions)
        for p in self.sections:   
            for i,j,v in zip(p.cx.row, p.cx.col, p.cx.data):               
                p.p0[i,j] = (v * len(p.chord_transitions))   
        sumarrtr = self.sections[0].p0 
        for i in range(1, len(self.sections), 1):    
            sumarrtr += self.sections[i].p0       
        self.chords_transition_matrix_all = sumarrtr
        t = sparse.coo_matrix(self.chords_transition_matrix_all)
        t.t0 = t.tocsr()
        rowsum = np.zeros(np.shape(t.t0)[0])
        for i,j,v in zip(t.row, t.col, t.data):      
            rowsum[i] = t.t0[i].sum()   
        for i,j,v in zip(t.row, t.col, t.data):
            t.t0[i,j] = v / rowsum[i]  
        self.chords_transition_matrix_all = t.t0
        #print(self.sections[0].chords[5].chord_symbol)
    # end make_stats

    def make_chords(self):
        # TODO: __GIANNOS__ add .onset_in_chart information for chords
        # gather all chords in one array
        self.chords = []
        for s in range(0, len(self.sections), 1):    
            # print(s)
            for i in range(0, len(self.sections[s].chords), 1):  
                self.chords.append(self.sections[s].chords[i])
                # add onset_in_chart information here
                # add melody_information here (since chart tonality information is required)
                # self.chords[-1].set_default_melody_info_with_tonality( self.tonality )
    # end make_chords
    
    def make_constraints(self):
        self.constraints = -1*np.ones(len(self.chords))
        for i, c in enumerate(self.chords):
            if c.isSectionLast or c.isSectionFirst:
                self.constraints[i] = self.chord2idx[c.chord_state]
    # end make_constraints
    
    def get_all_chords_idxs(self):
        if len( self.all_chord_states ) == 0:
            self.initialize_chord_states()
        idxs = np.zeros(len(self.chords))
        for i, c in enumerate(self.chords):
            idxs[i] = self.chord2idx[c.chord_state]
        return idxs.astype(int)
    # end get_all_chords_idxs
    
    def make_melody_information(self, tonality='piece_tonality'):
        self.melody_information = np.zeros( ( 12 , len(self.chords) ) )
        for i, c in enumerate(self.chords):
            # print('c.melody_information: ', c.melody_information)
            # print('c.melody_information[tonality]: ', c.melody_information[tonality])
            # self.melody_information[:,i] = c.melody_information[tonality]
            self.melody_information[:,i] = c.melody_information
    # end make_melody_information
    
    def make_transitions(self):
        # gather all transitions in one array
        self.chord_transitions = {}
        for s in range(0, len(self.sections), 1):    
            # print(s)
            for i in range(0, len(self.sections[s].chord_transitions), 1):
                tmp_trans = self.sections[s].chord_transitions[i]
                if tmp_trans.label not in self.chord_transitions.keys():
                    self.chord_transitions[tmp_trans.label] = tmp_trans
                else:
                    self.chord_transitions[tmp_trans.label].occurrences += 1
        # sorted
        self.chord_transitions = {k:v for k,v in sorted(self.chord_transitions.items(), key=lambda x: x[1].occurrences, reverse=True)}
    # end make_chords

    def get_features(self, separated=True):
        d = self.hmm.chords_distribution.toarray().astype(np.float32)
        t = self.hmm.transition_matrix.toarray().astype(np.float32)
        m = self.hmm.melody_per_chord.toarray().astype(np.float32)
        if separated:
            f = {}
            f['chords_distribution'] = d
            f['transition_matrix'] = t
            f['melody_per_chord'] = m
            return f
        else:
            return np.c_[ d.reshape((1,d.size)) , t.reshape((1,t.size)), m.reshape((1,m.size)) ]
    # end get_features
    
    def get_features_old(self, chords_distribution_all=True, chords_transition_matrix_all=True):
        f = np.array([])
        if chords_distribution_all:
            f = np.r_[ f , self.chords_distribution_all.toarray().astype(np.float32).reshape(len(self.all_chord_states)) ]
        if chords_transition_matrix_all:
            t = self.chords_transition_matrix_all.toarray().astype(np.float32)
            f = np.r_[ f , t.reshape(len(self.all_chord_states)**2) ]
        return sparse.csr_matrix(f)  
    # end get_features
# end Chart


# this code was in support cHMM
'''
                else:
                    print('HMM zero probability in constraint encoundered for t = ', t)
                    print('applying support to previous step...')
                    for j in range(0, markov.shape[0]):
                        tmp_trans_prob = support[:,j]
                        # it needs to reach the constraint
                        constraint_prob = support[ j, constraints[t] ]
                        delta[j,t-1] = np.max( np.multiply(delta[:,t-2], tmp_trans_prob)*obs[j,t-1]*constraint_prob )
                        psi[j,t-1] = np.argmax( np.multiply(delta[:,t-2], tmp_trans_prob)*obs[j,t-1]*constraint_prob )
                    if np.sum(delta[:,t-1]) != 0:
                        delta[:,t-1] = delta[:,t-1]/np.sum(delta[:,t-1])
                        print('support worked OK, as expected')
                    else:
                        print('support DIDNT work, smoothing')
                        tmp_trans_prob = np.ones( support[:,j].size )/support[:,j].size
                        # it needs to reach the constraint
                        constraint_prob = support[ j, constraints[t] ] + 0.0000001
                        for j in range(0, markov.shape[0]):
                            delta[j,t-1] = np.max( np.multiply(delta[:,t-2] + 0.0000001, tmp_trans_prob)*obs[j,t-1]*constraint_prob )
                            psi[j,t-1] = np.argmax( np.multiply(delta[:,t-2], tmp_trans_prob)*obs[j,t-1]*constraint_prob )
                        if np.sum(delta[:,t-1]) != 0:
                            delta[:,t-1] = delta[:,t-1]/np.sum(delta[:,t-1])
                    # no need to check if previous was a constraint, there would be all one-hot
                    j = int(constraints[t])
                    # tmp_trans_prob = np.zeros( markov[:,j].size )
                    # tmp_trans_prob[j] = 1
                    tmp_trans_prob = markov[:,j]
                    if np.sum(tmp_trans_prob) == 0:
                        print('instant support for constraint')
                        tmp_trans_prob = support[:,j]
                        if np.sum(tmp_trans_prob) == 0:
                            print('smoothening instant support for constraint')
                            tmp_trans_prob = np.ones(support[:,j].size)/support[:,j].size
                    tmp_trans_prob = tmp_trans_prob/np.sum(tmp_trans_prob)
                    delta[j,t] = np.max( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t]+0.00000001 )
                    psi[j,t] = np.argmax( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t]+0.00000001 )
                    if np.sum(delta[:,t]) != 0:
                        delta[:,t] = delta[:,t]/np.sum(delta[:,t])
                    else:
                        print('SUPPORT BEFORE CONSTRAINT NOT WORKING - smoothing')
                        print( 'np.max(delta[:,t-1]): ', np.max(delta[:,t-1]) )
                        print( 'np.argmax(delta[:,t-1]): ', np.argmax(delta[:,t-1]) )
                        print( 'np.sum(delta[:,t-1]): ', np.sum(delta[:,t-1]) )
                        tmp_trans_prob = np.ones( support[:,j].size )/support[:,j].size
                        for j in range(0, markov.shape[0]):
                            delta[j,t] = np.max( np.multiply(delta[:,t-1] + 0.0000001, tmp_trans_prob)*obs[j,t] )
                            psi[j,t] = np.argmax( np.multiply(delta[:,t-1], tmp_trans_prob)*obs[j,t] )
                        if np.sum(delta[:,t]) != 0:
                            delta[:,t] = delta[:,t]/np.sum(delta[:,t])
                        else:
                            print('----------- now it shouldnt be zero ------------- somethings wrong')
'''