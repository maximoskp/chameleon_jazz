#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 1 2021

@author: maximoskaliakatsos-papakostas
"""

import numpy as np

class Chord:
    def __init__(self, chord_in):
        print('Chord - chord_in: ', chord_in)
        at_split = chord_in.split('@')
        self.chord_symbol = at_split[0]
        comma_split = at_split[1].split(',')
        self.onset_in_measure = float(comma_split[0])
        '''
        # symbolic information
        self.chord_symbol = chord_symbol
        self.root_symbol = self.get_root_from_chord_symbol()
        self.type_symbol = None
        self.chord_symbol_in_chart_tonality = None
        self.chord_symbol_in_section_tonality = None
        # numeric information
        self.pitch_classes = None
        self.root_number = None
        self.root_number_in_chart_tonality = None
        self.root_number_in_section_tonality = None
        self.type_numeric = None
        # time information
        self.position_in_measure = None
        self.position_in_piece = None
        # bass chords
        # polychords
        '''
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
        '''
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
        '''
    # end __init__
    
    def make_chords(self, measure_in):
        print('Measure - make_chords')
        chords_split = measure_in.split('chord~')
        self.chords = []
        for c in chords_split[1:]:
            self.chords.append( Chord( c ) )
    # end make_chords

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

class ChordTransition:
    def __init__(self, first_chord=None, second_chord=None):
        self.first_chord_symbol = first_chord.chord_symbol
        self.second_chord_symbol = second_chord.chord_symbol
        self.first_chord = first_chord
        self.first_chord = first_chord
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
        '''
        self.chords = None # list of objects
        self.chord_symbols_list = None # list of chord symbols for debugging
        self.chord_symbols_in_tonality_list = None # list of isolated symbols for Markov table
        self.cadence = None # ChordTransition object
        # computed tonality with Krumhansl
        self.pcp = np.zeros(12)
        self.computed_tonality = None # Krumhansl
        '''
    # end __init__
    
    def make_measures(self, section_in):
        print('Section - make_measures')
        measures_split = section_in.split('bar~')
        self.measures = []
        for m in measures_split[1:]:
            print('measure: ', m)
            self.measures.append( Measure( m ) )
    # end make_measures

    def add_measure(self, m=None):
        # measures added herein do not (necessarily) need to obtain onset_in_chart
        if self.measures == None:
            self.measures = [ m ]
        else:
            self.measures.append( m )
    # end add_measure

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

class Chart:
    def __init__(self, struct_in):
        # meta data
        self.unfolded_string = struct_in['unfolded_string']
        self.piece_name = struct_in['appearing_name']
        self.tonality = struct_in['tonality']
        self.make_sections()
        
        '''
        # content information
        # keep sections as phrases
        self.measures = None # list of objects
        self.unfolded_measures = None # list of objects
        self.chords = None # list of objects
        self.chord_symbols_list = None # list of chord symbols for debugging
        self.chord_symbols_in_tonality_list = None # list of isolated symbols for Markov table
        '''
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

    def make_sections_old(self):
        print('make_sections')
        # TODO: collect unfolded measures in sections
        # for each section after section measures are all collected, process section
    # end make_sections

    def assign_chart_tonality_to_chords(self):
        print('assign_chart_tonality_to_chords')
    # end assign_chart_tonality_to_chords

    def process_chart(self):
        self.serialise_measures()
        self.make_sections()
    # end process_chart
# end Chart