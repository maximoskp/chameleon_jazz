#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 1 2021

@author: maximoskaliakatsos-papakostas
"""

class Chord:
    def __init__(self, chord_symbol_in):
        # symbolic information
        self.chord_symbol = None
        self.root_symbol = None
        self.type_symbol = None
        self.chord_symbol_in_tonality = None
        # numeric information
        self.pitch_classes = None
        self.root_number = None
        self.root_number_in_tonality = None
        self.type_numeric = None
        # time information
        self.position_in_measure = None
        self.position_in_piece = None
    # end __init__

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
    def __init__(self, is_first=False, style_change=False, section_change=False):
        # chart positional information
        self.onset_in_chart = None
        # repetition information
        self.has_repeat_start = False
        self.has_repeat_end = False
        self.has_volta_1 = False
        self.has_volta_2 = False
        self.has_volta_3 = False
        self.has_volta_4 = False
        # measure "head" information
        self.time_signature = None
        self.time_signature_change = False
        self.style = None
        self.style_change = style_change
        self.section = None
        self.section_change = section_change
        # content information
        self.chords = None # list of chord objects
    # end __init__

    def add_chord(self, c):
        # assumingly, when adding chords in a measure, the measure does not
        # know its own position on chart, so chords cannot know theirs
        if self.chords == None:
            self.chords = [ c ]
        else:
            self.chords.append( c )
    # end add_chord

    def update_chord_positions(self):
        print('TODO: update position_in_piece for chords')
    # end update_chord_positions
# end Measure

class Chart:
    def __init__(self, name=None, tonality=None):
        # meta data
        self.piece_name = name
        self.tonality = tonality
        # content information
        self.measures = None # list of objects
        self.unfolded_measures = None # list of objects
        self.chords = None # list of objects
        self.chord_symbols_list = None # list of chord symbols for debugging
        self.chord_symbols_in_tonality_list = None # list of isolated symbols for Markov table
    # end __init__

    def add_measure(self, m=None):
        # measures added herein do not (necessarily) need to obtain onset_in_chart
        if self.measures == None:
            self.measures = [ m ]
        else:
            self.measures.append( m )
    # end add_measure

    def serialise_measures(self):
        print('serialise_measures')
        # TODO: unfold measures and create unfolded_measures list
        # unfolded measures need to obtain onset_in_chart here
        # TODO: run update_chord_positions for each unfolded measure
        # TODO: construct chords, chord_symbols_list and chord_symbols_in_tonality_list
    # end serialise_measures
# end Chart