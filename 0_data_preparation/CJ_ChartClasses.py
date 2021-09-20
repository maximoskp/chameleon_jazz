#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 1 2021

@author: maximoskaliakatsos-papakostas
"""

import numpy as np
import os
import json

class ChameleonContext:
    # static scope for chord dictionary and initiall (0s) transition matrix
    with open('..' + os.sep + 'data' + os.sep + 'Lexikon' + os.sep + 'type2pcs_dictionary.json') as json_file:
        type2pc = json.load(json_file)
    type_names = list(type2pc.keys())
    type_names.sort()
    type2index = { k : i for i,k in enumerate(type_names) }
    index2type = { i : k for i,k in enumerate(type_names) }
    accidental_symbols = ['-', 'b', '#']
    # TODO: construct root2int for numerical roots
    # TODO: construct a global transition matrix with 0s
# end ChameleonContext

class Chord(ChameleonContext):
    def __init__(self, chord_in):
        print('Chord - chord_in: ', chord_in)
        at_split = chord_in.split('@')
        self.chord_symbol = at_split[0]
        comma_split = at_split[1].split(',')
        self.onset_in_measure = float(comma_split[0])
        # symbolic root
        root_idx = 1
        if self.chord_symbol[1] in self.accidental_symbols:
            root_idx = 2
        self.symbolic_root = self.chord_symbol[:root_idx]
        # get bass
        bass_split = self.chord_symbol[root_idx:].split('/')
        # TODO: fix polychords
        self.symbolic_type = bass_split[0]
        if self.symbolic_type == '':
            self.symbolic_type == ' '
        self.pc_set = self.type2pc[ self.symbolic_type ]
        self.bass_symbol = ''
        if len( bass_split ) > 1:
            self.bass_symbol = bass_split[1]
        # TODO:
        # get numeric root - check ChameleonContext: root2ind
        # get numeric root relative to PIECE tonality
        # get numeric root relative to COMPUTED tonality
        # get symbolic type
        # get PIECE tonality-relative pitch class set
        # get COMPUTED tonality-relative pitch class set
        # get GCT
        # get position in section
        # get position in piece
        # get bass symbol
        # get bass pitch class
        # get bass PIECE tonality-relative pitch class
        # get bass COMPUTED tonality-relative pitch class
        # discuss polychords...
    # end __init__

    def get_root_from_chord_symbol(self):
        print('get_root_from_chord_symbol')
    # end get_root_from_chord_symbol

    def get_type_from_chord_symbol(self):
        print('get_type_from_chord_symbol')
    # end get_type_from_chord_symbol

    def neutralise_for_tonality(self, tonality=None):
        if tonality == None:
            print('Chord - neutralise_for_tonality: tonality should not be None')
            return
        else:
            print('TODO: set chord_symbol_in_tonality and root_number_in_tonality')
    # end neutralise_for_tonality
# end Chord

class Measure:
    # purpose: make it easier to unfold chart
    def __init__(self, measure_in):
        self.time_signature = measure_in.split(',')[0]
        self.make_chords( measure_in )
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
        print('Measure - make_chords')
        chords_split = measure_in.split('chord~')
        self.chords = []
        for c in chords_split[1:]:
            self.chords.append( Chord( c ) )
    # end make_chords        
    
    def update_chord_positions(self):
        print('TODO: update position_in_piece for chords')
    # end update_chord_positions
# end Measure

class ChordTransition:
    def __init__(self, first_chord=None, second_chord=None):
        self.first_chord = first_chord
        self.second_chord = second_chord
        # TODO:
        # keep information from chord transitions that are relevant to blending
    # end __init__
# end ChordTransition

class Section:
    def __init__(self, section_in):
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
        self.make_chord_transitions()
        self.make_transition_matrix()
    # end __init__
    
    def make_measures(self, section_in):
        print('Section - make_measures')
        measures_split = section_in.split('bar~')
        self.measures = []
        for m in measures_split[1:]:
            print('measure: ', m)
            self.measures.append( Measure( m ) )
    # end make_measures
    
    def make_chords(self):
        print( 'Section - make chords' )
        self.chords = []
        for m in self.measures:
            for c in m.chords:
                self.chords.append( c )
    # end make_chords
    
    def make_chord_transitions(self):
        print('Section - make_chord_transitions')
        self.chord_transitions = []
        if len( self.chords ) > 1:
            for i in range( len( self.chords ) - 1 ):
                prv = self.chords[i]
                nxt = self.chords[i+1]
                self.chord_transitions.append( ChordTransition( 
                    first_chord=prv, second_chord=nxt ) )
    # end make_chord_transitions
    
    def make_transition_matrix(self):
        print('Sections - make_transition_matrix')
    # end make_transition_matrix
    
    def extract_pcp(self):
        print('extract_pcp')
        # TODO: collect pcp from each chord
        # assign value to self.pcp
    # end extract_pcp
    
    def compute_tonality(self):
        print('compute_tonality')
        # TODO: employ Krumhansl
        # assign value to self.computed_tonality
    # end compute_tonality
    
    def assign_section_tonality_to_chords(self):
        print('assign_section_tonality_to_chords')
    # end assign_section_tonality_to_chords
    
    def process_section(self):
        self.extract_pcp()
        self.compute_tonality()
    # end process_section
# end Section

class Chart(ChameleonContext):
    def __init__(self, struct_in):
        # meta data
        self.unfolded_string = struct_in['unfolded_string']
        self.piece_name = struct_in['appearing_name']
        self.tonality = struct_in['tonality']
        self.make_sections()
        # do we need to keep:
        # chords?
        # tonalities (computed) per section?
    # end __init__
    
    def make_sections(self):
        print('Chart - make_sections')
        # split sections
        sections_split = self.unfolded_string.split('section~')
        self.sections = []
        for s in sections_split[1:]:
            print('making section: ', s)
            self.sections.append( Section( s ) )
            print('self.sections: ', self.sections)
    # end make_sections
    
    def assign_chart_tonality_to_chords(self):
        print('assign_chart_tonality_to_chords')
    # end assign_chart_tonality_to_chords
# end Chart