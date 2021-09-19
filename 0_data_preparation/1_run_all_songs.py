#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  1 17:54:54 2020

@author: maximoskaliakatsos-papakostas
"""

import os
import xmlChart2String
import json

# load dictionary to check for m21 chord type incompatibility
with open('..' + os.sep + 'data' + os.sep + 'Lexikon' + os.sep + 'type2pcs_dictionary.json') as json_file:
    type2pcs_dictionary = json.load(json_file)
# get chord names - keys
chord_names = list( type2pcs_dictionary.keys() )

mysongs = {}
songslibrary = {}
# keep a catalogue of chords not found in each piece
pieces_undefined_chords = {}
# keep a catalogue of pieces that don't have tonality annotation
pieces_undefied_tonality = {}

# construct name substitutions dictionary
names_dict = {}
names_txt = open('..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'library_name_symbols.txt', encoding='utf-8')
for line in names_txt.readlines():
    arrow_split = line.split(' -> ')
    if len(arrow_split) > 1:
        tmp_key = arrow_split[0][1:-1]
        tmp_value = arrow_split[1][1:-1]
        if tmp_value[-1] == " " or tmp_value[-1] == "\"":
            tmp_value = tmp_value[:-1]
        names_dict[ tmp_key ] = tmp_value
names_dict_keys = list( names_dict.keys() )

# my songs first
for s in os.listdir( '..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'My_Songs'):
    if s.endswith('.mxl'):
        file_name = '..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'My_Songs' + os.sep + s
        song_string, song_tonality, chords_not_found = xmlChart2String.chart2string( file_name, print_interim=False , chord_names=chord_names )
        # TODO: take piece name from function - score
        piece_name = file_name.split( os.sep )[-1]
        # fix name - remove underscore and extension
        filename, file_extension = os.path.splitext(s)
        final_filename = filename.replace('_', ' ')
        appearing_name = final_filename
        for tmp_key in names_dict_keys:
            if tmp_key in appearing_name:
                print('before: ' + appearing_name)
                appearing_name = appearing_name.replace( tmp_key, names_dict[tmp_key] )
                # try all lowercase <- not good that way
                # appearing_name = appearing_name.replace( tmp_key.lower(), names_dict[tmp_key].lower() )
                print('after: ' + appearing_name)
        tmp_song_key = appearing_name
        while not tmp_song_key[0].isalnum():
            tmp_song_key = tmp_song_key[1:]
        tmp_song_key = tmp_song_key.upper()
        tmp_json = {
            'string': song_string,
            'original_string': song_string,
            'unfolded_string': xmlChart2String.unfold_chart(song_string),
            'tonality': song_tonality,
            'original_key': tmp_song_key,
            'appearing_name': appearing_name,
            'is_favourite': False

        }
        mysongs[ tmp_song_key ] = tmp_json
        # songs.append( tmp_json )
        actual_chords_not_found = []
        for cnf in chords_not_found:
            if '/' not in cnf:
                actual_chords_not_found.append( cnf )
        if len(actual_chords_not_found) > 0:
            pieces_undefined_chords[ piece_name ] = actual_chords_not_found
        if song_tonality == -1:
            pieces_undefied_tonality[ appearing_name ] = tmp_json

# library second
for s in os.listdir('..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'Library'):
    if s.endswith('.mxl'):
        file_name = '..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'Library' + os.sep + s
        song_string, song_tonality, chords_not_found = xmlChart2String.chart2string( file_name, print_interim=False , chord_names=chord_names )
        # TODO: take piece name from function - score
        piece_name = file_name.split( os.sep )[-1]
        # fix name - remove underscore and extension
        filename, file_extension = os.path.splitext(s)
        final_filename = filename.replace('_', ' ')
        appearing_name = final_filename
        for tmp_key in names_dict_keys:
            if tmp_key in appearing_name:
                print('before: ' + appearing_name)
                appearing_name = appearing_name.replace( tmp_key, names_dict[tmp_key] )
                print('after: ' + appearing_name)
        tmp_song_key = appearing_name
        while not tmp_song_key[0].isalnum():
            tmp_song_key = tmp_song_key[1:]
        tmp_song_key = tmp_song_key.upper()
        tmp_json = {
            'string': song_string,
            'original_string': song_string,
            'unfolded_string': xmlChart2String.unfold_chart(song_string),
            'tonality': song_tonality,
            'original_key': tmp_song_key,
            'appearing_name': appearing_name,
            'is_favourite': False
        }
        songslibrary[ tmp_song_key ] = tmp_json
        # songs.append( tmp_json )
        actual_chords_not_found = []
        for cnf in chords_not_found:
            if '/' not in cnf:
                actual_chords_not_found.append( cnf )
        if len(actual_chords_not_found) > 0:
            pieces_undefined_chords[ piece_name ] = actual_chords_not_found
        if song_tonality == -1:
            pieces_undefied_tonality[ appearing_name ] = tmp_json

with open( '..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'mysongs.json', 'w') as f:
    json.dump(mysongs, f)

with open( '..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'songslibrary.json', 'w') as f:
    json.dump(songslibrary, f)

with open( '..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'missing_chords.json', 'w') as f:
    json.dump(pieces_undefined_chords, f)

with open( '..' + os.sep + 'data' + os.sep + 'Songs' + os.sep + 'missing_tonalities.json', 'w') as f:
    json.dump(pieces_undefied_tonality, f)