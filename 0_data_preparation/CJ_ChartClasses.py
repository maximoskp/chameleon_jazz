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
from scipy.sparse import hstack
from scipy.sparse import *



class ChameleonContext:
    # static scope for chord dictionary and initiall (0s) transition matrix
    with open('..' + os.sep + 'data' + os.sep + 'Lexikon' + os.sep + 'type2pcs_dictionary.json') as json_file:
        type2pc = json.load(json_file)
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
        return {'root': self.root2int[s[:root_idx]], 'mode':mode}
    # end tonality_from_symbol
    def make_empty_chords_distribution(self):
        chords_distribution = np.zeros( 12*len(list(self.type2pc.keys())) )
    # end make_empty_chords_distribution
    def get_all_chord_states(self):
        all_chord_states = []
        for i in range(12):
            for v in self.type2pc.values():
                all_chord_states.append( self.chord2state(numeric_root=i, numeric_type=v['extended_type'], tonality= "piece_tonality" ))
        return all_chord_states
    # end get_all_chord_states
# end ChameleonContext

class Chord(ChameleonContext):
    def __init__(self, chord_in):
        #print('Chord - chord_in: ', chord_in)
        at_split = chord_in.split('@')
        self.chord_symbol = at_split[0]
        comma_split = at_split[1].split(',')
        self.onset_in_measure = float(comma_split[0])
        # symbolic root
        root_idx = 1
        if len(self.chord_symbol) > 1 and self.chord_symbol[1] in self.accidental_symbols:
            root_idx = 2
        self.symbolic_root = self.chord_symbol[:root_idx]
        # get bass
        nine_idx = root_idx
        if '/9' in self.chord_symbol:
            nine_idx = self.chord_symbol.find('/9') + 2
        bass_split = self.chord_symbol[nine_idx:].split('/')
        # TODO: fix polychords
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
        ## self.gct = ng.GCT_sum_all_from_root(numeric_type)[0]
        # TODO:
        #print(self.onset_in_measure) 
         
        # get position in section
        # get position in piece            
        s = list(combinations(self.numeric_type, 2))
        # __@GIANNOS__ only ascending intervals are generated, is it correct?
        # e.g. only (0,4)->4-0=4 is generated, not (4,0)->0-4=8
        self.interval_vector = np.zeros(12)
        for i in s:
            interval = (i[1]-i[0])%12
            self.interval_vector[interval] += 1
        self.bass_symbol = ''
        if len( bass_split ) > 1:
            self.bass_symbol = bass_split[1]
            # get bass pitch class
            self.bass_pitch_class = self.root2int[ self.bass_symbol ]
            self.pcp[ self.bass_pitch_class ] = 1
        # discuss polychords...
    # end __init__

    def set_tonalities(self, piece_tonality=None, estimated_tonality=None):
        # print('Chord - set_tonalities')
        self.piece_tonality = piece_tonality
        self.estimated_tonality = estimated_tonality
        # get chord numeric root relative to PIECE and ESTIMATED tonality
        self.relative_root = {
            'piece_tonality': (self.numeric_root -self.piece_tonality['root'])%12,
            'estimated_tonality': (self.numeric_root -self.estimated_tonality['root'])%12
        }
        self.chord_state = self.chord2state(tonality='piece_tonality')
        # get PIECE tonality-relative pitch class set
        # get ESTIMATED tonality-relative pitch class set
        # get GCT
        # __@GIANNOS__ the following two lines don't work:
        '''
        UFuncTypeError: ufunc 'subtract' did not contain a loop with signature 
        matching types (dtype('int64'), dtype('<U1')) -> None
        '''
        # self.gct_piece_tonality = ng.GCT_in_key(self.numeric_type, piece_tonality)
        # self.gct_estimated_tonality = ng.GCT_in_key(self.numeric_type, estimated_tonality)
        # if bass
        # get bass PIECE tonality-relative pitch class
        # get bass ESTIMATED tonality-relative pitch class
    # end set_tonalities
# end Chord

class Measure:
    # purpose: make it easier to unfold chart
    def __init__(self, measure_in):
        self.time_signature = measure_in.split(',')[0]
        self.make_chords( measure_in )
        #self.chord_potisions(measure_in)
        # self.measure_potisions()
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
    
    #def chord_potisions(self, measure_in):
        #print(measure_in)
        
    
    # def update_chord_positions(self):
    #     # print('TODO: update position_in_piece for chords')
    # # end update_chord_positions
# end Measure

class ChordTransition:
    def __init__(self, first_chord=None, second_chord=None):
        self.first_chord = first_chord
        self.second_chord = second_chord
        # TODO:
        # keep information from chord transitions that are relevant to blending
    # end __init__
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
        for m in self.measures:
            for c in m.chords:
                self.chords.append( c )
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
        self.all_chord_states = self.get_all_chord_states()
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
        # meta data
        self.unfolded_string = struct_in['unfolded_string']
        self.piece_name = struct_in['appearing_name']
        self.key = struct_in['original_key']
        self.tonality = self.tonality_from_symbol( struct_in['tonality'] )
        self.make_sections()
        self.make_stats()        
        # do we need to keep:
        # chords?
        # tonalities (estimated) per section?
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
        self.all_chord_states = self.get_all_chord_states()
        #gather chord_distribution info
        chord_distr_sum = 0
        testnormalization = 0     
        for s in self.sections:
            chord_distr_sum += len(s.chords)
        for s in self.sections:
            s.cx = coo_matrix(s.chords_distribution)
            s.s0 = s.cx.tocsr()
            for i,j,v in zip(s.cx.row, s.cx.col, s.cx.data): 
                s.s0[i,j] = (v * len(s.chords))  
        sumarr = self.sections[0].s0           
        for i in range(1, len(self.sections), 1):    
            sumarr += self.sections[i].s0         
        self.chords_distribution_all = sumarr
        k = coo_matrix(self.chords_distribution_all)
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
            p.cx = coo_matrix(p.chord_transition_matrix)
            p.p0 = p.cx.tocsr()
            chord_trans_sum += len(p.chord_transitions)
        for p in self.sections:   
            for i,j,v in zip(p.cx.row, p.cx.col, p.cx.data):               
                p.p0[i,j] = (v * len(p.chord_transitions))   
        sumarrtr = self.sections[0].p0 
        for i in range(1, len(self.sections), 1):    
            sumarrtr += self.sections[i].p0       
        self.chords_transition_matrix_all = sumarrtr
        t = coo_matrix(self.chords_transition_matrix_all)
        t.t0 = t.tocsr()
        rowsum = np.zeros(np.shape(t.t0)[0])
        for i,j,v in zip(t.row, t.col, t.data):      
            rowsum[i] = t.t0[i].sum()   
        for i,j,v in zip(t.row, t.col, t.data):
            t.t0[i,j] = v / rowsum[i]  
        self.chords_transition_matrix_all = t.t0
        #print(self.sections[0].chords[5].chord_symbol)
        
        #gather chord potision in chart
        self.chord_potision_in_chart = []
        for s in range(0, len(self.sections), 1):    
            # print(s)
            for i in range(0, len(self.sections[s].chords), 1):  
                #if i==len(self.sections[s].chords)
                self.chord_potision_in_chart.append(self.sections[s].chords[i].chord_symbol)
        # print(self.chord_potision_in_chart[5])
    # end make_stats

    def get_features(self, chords_distribution_all=True, chords_transition_matrix_all=True):
        f = np.array([])
        if chords_distribution_all:
            f = np.r_[ f , self.chords_distribution_all.toarray().astype(np.float32).reshape(len(self.all_chord_states)) ]
        if chords_transition_matrix_all:
            t = self.chords_transition_matrix_all.toarray().astype(np.float32)
            f = np.r_[ f , t.reshape(len(self.all_chord_states)**2) ]
        return sparse.csr_matrix(f)  
    # end get_features
# end Chart