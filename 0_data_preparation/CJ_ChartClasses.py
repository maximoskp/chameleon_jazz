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
    chord2idx = {}
    idx2chord = {}
    idx2chordnp = {}
    all_chord_states = []
    all_states_np = []
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

    def initialize_chord_states(self):
        # self.all_chord_states = []
        # self.all_states_np = []
        for i in range(12):
            for v in self.type2pc.values():
                tmp_chord_state = self.chord2state(numeric_root=i, numeric_type=v['extended_type'], tonality= "piece_tonality" )
                self.all_chord_states.append( tmp_chord_state )
                self.all_states_np.append( np.fromstring( tmp_chord_state.replace(' ', '').replace('[', '').replace(']', '') , dtype=int, sep=',' ) )
        for i in range( len(self.all_chord_states) ):
            self.chord2idx[self.all_chord_states[i]] = i
            self.idx2chord[i] = self.all_chord_states[i]
            self.idx2chordnp[i] = self.all_states_np[i]
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
# end ChameleonContext

class ChameleonHMM(ChameleonContext):
    def __init__(self):
        # rows: 840, columns: 12
        self.melody_per_chord = sparse.csr_matrix( np.zeros( (len(self.all_chord_states), 12) ) )
        # 840x840
        self.transition_matrix = sparse.csr_matrix( np.zeros( (len(self.all_chord_states), len(self.all_chord_states)) ) )
    # end init

    def add_melody_per_chord_information(self, chords):
        self.melody_per_chord = self.melody_per_chord.toarray()
        for chord in chords:
            idx = self.chord2idx[ chord.chord_state ]
            self.melody_per_chord[idx,:] += chord.melody_information['piece_tonality']
        for i in range( self.melody_per_chord.shape[0] ):
            if np.sum( self.melody_per_chord[i,:] ) != 0:
                self.melody_per_chord[i,:] /= np.sum( self.melody_per_chord[i,:] )
        self.melody_per_chord = sparse.csr_matrix( self.melody_per_chord )
    # end add_melody_per_chord_information

    def add_transition_information(self, t):
        self.transition_matrix = self.transition_matrix.toarray()
        self.transition_matrix += t
        for i in range(self.transition_matrix.shape[0]):
            if np.sum( self.transition_matrix[i,:] ) != 0:
                self.transition_matrix[i,:] /= np.sum( self.transition_matrix[i,:] )
        self.transition_matrix = sparse.csr_matrix( self.transition_matrix )
    # end add_transition_information
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
        if len( bass_split ) > 1:
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
            self.melody_information = self.rpcp # assign default or Chord class here          
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
            self.assign_melody_to_chord( measure_in )
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
        melody_split = measure_in.split('melody~[')
        self.melody_information = []
        self.melody_onsets = []
        for mel in melody_split[1:]:
            pitches = mel.split(',end]')[0]
            pitches_split = pitches.split('pitch~')
            for p in pitches_split[1:]:
                comma_split = p.split(',')[0]
                at_split = comma_split.split('@')
                self.melody_information.append( int(at_split[0]) ) # pitch information per measure
                if '/' in at_split[1]: # case for fractional values in melody like in tuplets, e.g. 2/3
                    a, b = at_split[1].split('/')
                    self.melody_onsets.append( float(int(a) / int(b)) )
                else:
                    self.melody_onsets.append( float(at_split[1]) )
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
        self.piece_name = struct_in['appearing_name']
        self.key = struct_in['original_key']
        self.tonality = self.tonality_from_symbol( struct_in['tonality'] )
        self.make_sections()
        self.make_stats()        
        # do we need to keep:
        # chords with their time in chart (if we happen to need harmonic rhythm)
        self.make_chords()
        self.make_transitions()
        self.hmm = ChameleonHMM()
        self.hmm.add_melody_per_chord_information( self.chords )
        self.hmm.add_transition_information( self.chords_transition_matrix_all.toarray() )
        print( '----------------------------------------------' )
        print(self.hmm.melody_per_chord)
        print( '----------------------------------------------' )
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
        # gather chord_distribution info
        chord_distr_sum = 0
        testnormalization = 0     
        for s in self.sections:
            chord_distr_sum += len(s.chords)
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