#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 15:29:05 2022

@author: kvelenis & max
"""
import pandas as pd
import re
import copy
import json
import math
import chardet
import sys
import os
from tabulate import tabulate
import numpy as np

original_stdout = sys.stdout

# %% Function that converts kern to chart 

# load ts_groupings
f = open('../data/json_files/chord_types_mapping_web.json')
types2fonts = json.load(f)
f.close()
fonts2types = {v: k for k, v in types2fonts.items()}

f = open('../data/json_files/accidental_symbols_mapping.json')
acc2fonts = json.load(f)
f.close()
fonts2acc = {v: k for k, v in acc2fonts.items()}

def kern2py(file_name):
    # load kern file & create pandas dataframe
    names = ['Bass', 'Kick-Snare', 'Hihat',
            'Piano-F-Clef', 'empty', 'Piano-G-Clef', 'Chords']
    # df = pd.read_csv("kern/A_BEAUTIFUL_FRIENDSHIP_2.krn", sep='\t', names=names)
    df = pd.read_csv(file_name, sep='\t', names=names)

    # find time signature TODO: find time signature by bar
    initial_time_signature = '4/4'
    starMdf = df[ np.logical_and( df.iloc[:,0].str.contains('\*M') , ~df.iloc[:,0].str.contains('\*MM') ) ]
    if starMdf.size > 0:
        starMdf = df[ np.logical_and( df.iloc[:,0].str.contains('\*M') , ~df.iloc[:,0].str.contains('\*MM') ) ]
        initial_time_signature = starMdf.iloc[0,0].replace('*M', '')
        # print('initial_time_signature:', initial_time_signature )

    # find where each measure starts based on "=" symbol
    df_measure_start = df.loc[df['Bass'].str.contains("=")]

    # find title
    titledf = df[df['Bass'].str.contains("!!!OTL: Jazz Standard Title")]

    # title = titledf.iloc[0, 0].replace('!!!OTL: ', '')

    # create chart variable
    chart = {}
    chart["bars"] = []

    measures = []
    measures_copy_last_column = []

    # function that convert kern absolute note values to chart absolute note values


    def note_duration(note):
        result = float
        if "." in note:
            i = re.findall('[0-9]+', note)

            if int(i[0]) == 1:
                result = 6
            elif int(i[0]) == 2:
                result = 3
            elif int(i[0]) == 4:
                result = 1.5
            elif int(i[0]) == 8:
                result = 0.75
            elif int(i[0]) == 16:
                result = 0.375
            elif int(i[0]) == 32:
                result = 0.1875
        elif int(note) == 1:
            result = 4
        elif int(note) == 2:
            result = 2
        elif int(note) == 4:
            result = 1
        elif int(note) == 6:
            result = 0.666
        elif int(note) == 8:
            result = 0.5
        elif int(note) == 12:
            result = 0.333
        elif int(note) == 16:
            result = 0.25
        elif int(note) == 32:
            result = 0.125
        return result


    # create dataframe collection divided by measure
    for i in range(len(df_measure_start.index)-1):
        measures.append(
            df.iloc[df_measure_start.iloc[i].name:df_measure_start.iloc[(i+1)].name])
        measures_copy_last_column.append(
            df.iloc[df_measure_start.iloc[i].name:df_measure_start.iloc[(i+1)].name, -1])
        measures_copy_last_column[i] = measures_copy_last_column[i].iloc[1:]
    # create deep copy
    measures_copy = []
    measures_copy = copy.deepcopy(measures)

    # drop chord column
    for i in range(len(measures_copy)):
        measures_copy[i] = measures_copy[i].iloc[:, :-1]

    # loop to find style, tempo, replace all kern note values with chart note values and make all other nan values equal to zero
    for i in range(len(measures_copy)):

        for y in range(len(measures_copy[i])):

            for x in range(len(measures_copy[i].columns)):

                if isinstance(measures_copy[i].iloc[y, x], str):
                    if "!LO:TX:a:t=[" in measures_copy[i].iloc[y, x]:
                        tempo = re.findall(
                            '[0-9]+', measures_copy[i].iloc[y, x])[0]
                    if "!LO:TX:a:t=" in measures_copy[i].iloc[y, x]:
                        style = measures_copy[i].iloc[y,
                                                    x].replace('!LO:TX:a:t=', '')
                    if True in [char.isdigit() for char in measures_copy[i].iloc[y, x]]:
                        if "=" in measures_copy[i].iloc[y, x] or "!LO" in measures_copy[i].iloc[y, x]:
                            measures_copy[i] = measures_copy[i].replace(
                                measures_copy[i].iloc[y, x], 0)
                            break
                        elif "." in measures_copy[i].iloc[y, x] and len(measures_copy[i].iloc[y, x]) > 2:
                            measures_copy[i] = measures_copy[i].replace(measures_copy[i].iloc[y, x], note_duration(
                                (measures_copy[i].iloc[y, x].split('.')[0])+"."))
                        elif not "." in measures_copy[i].iloc[y, x]:
                            measures_copy[i] = measures_copy[i].replace(measures_copy[i].iloc[y, x], note_duration(
                                re.findall('[0-9]+', measures_copy[i].iloc[y, x])[0]))
                    else:
                        measures_copy[i] = measures_copy[i].replace(
                            measures_copy[i].iloc[y, x], 0)

    # sum all column, find the lowest, assign it to a list, keep only the values that carries a chord an append it to chart variable
    dfcumsum = []
    measures_chart_ready = []
    measures_chart_ready_for_gjt = []
    for i in range(len(measures_copy)):
        dfcumsum.append(measures_copy[i].iloc[1:, :].cumsum().min(axis=1))
        dfcumsum[i] = dfcumsum[i].iloc[:].shift(1)
        measures_chart_ready.append(pd.concat(
            [dfcumsum[i], measures_copy_last_column[i]], axis=1).reindex(dfcumsum[i].index))
        # chart["bars"].append(measures_chart_ready[i])


    measures_chart_ready[0].iloc[0, 1] = "*"
    measures_chart_ready_for_gjt = copy.deepcopy(measures_chart_ready)
    # print("measures_chart_ready:", measures_chart_ready)
    # print("measures_chart_ready_for_gjt:", measures_chart_ready_for_gjt)
    for i in range(len(measures_chart_ready)):
        for y in range(len(measures_chart_ready[i])):
            # if not len(measures_chart_ready[i].iloc[y, 1]) > 2:
            if measures_chart_ready[i].iloc[y, 1] in ['*', '!', '.', ' ', '']:
                measures_chart_ready_for_gjt[i].drop(
                    [measures_chart_ready[i].index[y]], axis=0, inplace=True)
        chart["bars"].append(measures_chart_ready_for_gjt[i])

    #chart["title"] = title
    chart["style"] = style
    chart["tempo"] = tempo
    return chart, initial_time_signature
# end kern2py

def kern2pyOld(file_name):
    # load kern file & create pandas dataframe
    names=['a', 'b', 'c', 'd', 'e', 'f', 'g']
    df = pd.read_csv(file_name, sep='\t', names=names)
    
    # find where each measure starts based on "=" symbol
    df_measure_start = df.loc[df['a'].str.contains("=")]
    
    # find title
    # titledf = df[df['a'].str.contains("!!!OTL: Jazz Standard Title")]
    titledf = df[df['a'].str.contains("!!!OTL: ")]
    title = titledf.iloc[0,0].replace('!!!OTL: ', '')
    
    #create chart variable
    chart = {}
    chart["bars"] = []
    
    measures = []
    measures_copy_last_column = [];
    
    # function that convert kern absolute note values to chart absolute note values 
    def note_duration(note):
        result = float
        if "." in note:
            i = re.findall('[0-9]+',note);
    
            if int(i[0]) == 1:
                result = 6;
            elif int(i[0]) == 2:
                result = 3;
            elif int(i[0]) == 4:
                result = 1.5;
            elif int(i[0]) == 8:
                result = 0.75;
            elif int(i[0]) == 16:
                result = 0.375;
            elif int(i[0]) == 32:
                result = 0.1875;
        elif int(note) == 1:
            result = 4;
        elif int(note) == 2:
            result = 2;
        elif int(note) == 4:
            result = 1;
        elif int(note) == 6:
            result = 0.666;
        elif int(note) == 8:
            result = 0.5;
        elif int(note) == 12:
            result = 0.333;
        elif int(note) == 16:
            result = 0.25;
        elif int(note) == 32:
            result = 0.125;
        return result;
            
    # create dataframe collection divided by measure
    for i in range(len(df_measure_start.index)-1):
        measures.append(df.iloc[df_measure_start.iloc[i].name:df_measure_start.iloc[(i+1)].name])
        measures_copy_last_column.append(df.iloc[df_measure_start.iloc[i].name:df_measure_start.iloc[(i+1)].name, -1])
        measures_copy_last_column[i] = measures_copy_last_column[i].iloc[1:]
    
    # create deep copy
    measures_copy = []
    measures_copy = copy.deepcopy(measures)
    
    # drop chord column
    for i in range(len(measures_copy)):  
        measures_copy[i] = measures_copy[i].iloc[: , :-1]
    
    # loop to find style, tempo, replace all kern note values with chart note values and make all other nan values equal to zero 
    for i in range(len(measures_copy)):
        # print('measures_copy[i]: ', measures_copy[i])
        for y in range(len(measures_copy[i])):      
            
            for x in range(len(measures_copy[i].columns)):
                # print('measures_copy[i].iloc[y, x]: ', measures_copy[i].iloc[y, x])
                
                if isinstance(measures_copy[i].iloc[y, x], str):
                    if "!LO:TX:a:t=[" in measures_copy[i].iloc[y, x]:
                        tempo = re.findall('[0-9]+', measures_copy[i].iloc[y, x])[0]
                    if "!LO:TX:a:t=" in measures_copy[i].iloc[y, x]:
                        style = measures_copy[i].iloc[y, x].replace('!LO:TX:a:t=', '');
                    if True in [char.isdigit() for char in measures_copy[i].iloc[y, x]]:
                        if "=" in measures_copy[i].iloc[y, x] or "!LO" in measures_copy[i].iloc[y, x]:
                            measures_copy[i] = measures_copy[i].replace(measures_copy[i].iloc[y, x], 0)
                            break;            
                        elif "." in measures_copy[i].iloc[y, x] and len(measures_copy[i].iloc[y, x]) > 3:                     
                            measures_copy[i] = measures_copy[i].replace(measures_copy[i].iloc[y, x], note_duration((measures_copy[i].iloc[y, x].split('.')[0])+"."))
                        elif not "." in measures_copy[i].iloc[y, x]:
                            measures_copy[i] = measures_copy[i].replace(measures_copy[i].iloc[y, x], note_duration(re.findall('[0-9]+', measures_copy[i].iloc[y, x])[0]))
                    else:
                        measures_copy[i] = measures_copy[i].replace(measures_copy[i].iloc[y, x], 0)
    
    # sum all column, find the lowest, assign it to a list, keep only the values that carries a chard an append it to chart variable
    dfcumsum = []
    measures_chart_ready = []
    for i in range(len(measures_copy)):  
        dfcumsum.append(measures_copy[i].iloc[1:,:].cumsum().min(axis=1))
        dfcumsum[i] = dfcumsum[i].iloc[:].shift(1)
        measures_chart_ready.append(pd.concat([dfcumsum[i], measures_copy_last_column[i]], axis=1).reindex(dfcumsum[i].index))
        for y in range(len(measures_chart_ready[i])):      
            
            for x in range(len(measures_chart_ready[i].columns)):
                
                if isinstance(measures_chart_ready[i].iloc[y, x], str):
                    #print(measures_chart_ready[i].iloc[y, x])
                    if "*" in measures_chart_ready[i].iloc[y, x]:
                        # print(measures_chart_ready[i].iloc[y, x])
                        k=y+1
                    if len(measures_chart_ready[i].iloc[y, x]) > 3:
                        m=y
        measures_chart_ready[i] = measures_chart_ready[i].iloc[k:m+1]
        for y in range(len(measures_chart_ready[i])):      
            
            for x in range(len(measures_chart_ready[i].columns)):
                
                if isinstance(measures_chart_ready[i].iloc[y, x], str):
                    if len(measures_chart_ready[i].iloc[y, x]) < 3:
                        measures_chart_ready[i] = measures_chart_ready[i].iloc[0:0]
        chart["bars"].append(measures_chart_ready[i])
    chart["title"] = title
    chart["style"] = style
    chart["tempo"] = tempo
    return chart
# end kern2py

def kern2string(file_name, find_chord_in_line=None):
    p, initial_time_signature = kern2py(file_name)
    # print('p: ', p)
    string = 'section~A'
    string += ',style~' + p['style']
    string += ',tempo~' + p['tempo']
    string += ',tonality~' + 'C' # TODO: tonality
    # get the index of the chord to be substituted
    chord_idx = -1
    chord_found = False
    for b in p['bars']:
        # print('b:')
        # print(b)
        string += ',bar~' + initial_time_signature # TODO: time sig
        for i in range(b.shape[0]):
            t = str( b.iloc[i][0] )
            c = b.iloc[i]['Chords'] # TODO: translate to GJT chord
            # it appears that there is always a space between root and type
            # print('b.iloc[i].name', b.iloc[i].name)
            if (find_chord_in_line is not None) and (chord_found == False):
                # print('increasing chord_idx: ', chord_idx)
                chord_idx += 1
                if abs( find_chord_in_line - b.iloc[i].name ) < 2:
                    # print('FOUND chord_idx: ', chord_idx)
                    chord_found = True
            chord_split = c.split(' ')
            acc_chord = chord_split[0]
            if len(acc_chord) > 1:
                # print('acc_chord:', acc_chord)
                if acc_chord[1] in list(fonts2acc.keys()):
                    acc_chord = acc_chord.replace( acc_chord[1], fonts2acc[ acc_chord[1] ] )
            if len(chord_split) > 1:
                # type other than "major", i.e. no type
                string += ',chord~' + acc_chord + fonts2types[chord_split[1]] + '@' + t
            else:
                string += ',chord~' + acc_chord + '@' + t
            # string += ',chord~' + c + '@' + t
    string += ',end'
    return string, chord_idx

def csv2kern(filename):
    
    names = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    names_grid = ['Bass', 'Kick-Snare', 'Hihat', 'Piano-F-Clef', 'empty', 'Piano-G-Clef', 'Chords']
    df_proto = pd.read_csv("kern_init.krn", sep='\t', names=names)
    df_proto = df_proto.iloc[0:16]

    
    df_measure_grid = pd.read_csv(
            "kern_measure_grid_empty.krn", sep='\t', names=names_grid)
    
    with open(filename, 'rb') as rawdata:
        result = chardet.detect(rawdata.read(100000))
    
    
    #FOR ONLINE INTEGRATION UNCOMMENT THE FOLOWING:
# =============================================================================
#     result = chardet.detect( str.encode( filename.getvalue() ) )
# =============================================================================
    


    #FOR ONLINE INTEGRATION COMMENT OUT THE FOLOWING:
    if result["encoding"] == "utf-16":
        df = pd.read_csv(filename, sep='\;', encoding=result["encoding"])
        for i in range(len(df.columns)-1):
            df.iloc[:, i] = df.iloc[:, i].str.replace(" ", "")
    else:
        df = pd.read_csv(filename, sep='\;', encoding=result["encoding"])
    
    #FOR ONLINE INTEGRATION UNCOMMENT THE FOLOWING:
# =============================================================================
#     if result["encoding"] == "utf-16":
#         df = pd.read_csv(filename, sep='\,', encoding=result["encoding"])
#         for i in range(len(df.columns)-1):
#             df.iloc[:, i] = df.iloc[:, i].str.replace(" ", "")
#     else:
#         df = pd.read_csv(filename, sep='\, ', encoding=result["encoding"])
# =============================================================================


    #Load json files for for mappings, accidendal symbols, midi to kern notes, kern notes duration
    f = open('json/csv_to_kern_fonts_mapping.json')
    fonts_mapping = json.load(f)
    
    f = open('json/csv_to_kern_accidental_symbol_mapping.json')
    accidental_symbols_mapping = json.load(f)
    
    f = open('json/csv_to_kern_midi_to_kern_notes.json')
    miditokern = json.load(f)
    
    f = open('json/csv_to_kern_kern_note_duration_dictionary.json')
    note_duration_dictionary = json.load(f)
    
    f = open('json/csv_to_kern_pause_position.json')
    pause_position_dictionary = json.load(f)
    
    

    df_measure_start = df.loc[df.iloc[:, 0].str.contains("Bar")]

    global_rhythm = re.findall(r'\d+', df.columns[2])

    global_style = df.columns[1].replace(' ', '')

    global_tempo = df.columns[4].replace(' ', '')

    song_title = 'test'

    global_tonality = df.columns[0]

    kern_song_title_part_1 = "!!!system-decoration: \\{(s1,s2)\\}s3,s4\\" + "\n" + "!!!OTL: " + song_title + "\n" + \
        "**kern\t**kern\t**kern\t**kern\t**mxhm\n*part3\t*part2\t*part1\t*part1\t*part1\n*staff4\t*staff3\t*staff2\t*staff1\t*\n*I'Contrabass'\t*I'Drumset'\t*'IPiano'\t*\t*\n*I'Cb.\t*I'D. Set\t*I'Pno.\t*\t*\n*clefF4\t*clefX\t*clefF4\t*clefG2\t*\n*k[b-e-a-]	*k[]\t*k[b-e-a-]\t*k[b-e-a-]\t*"

    kern_song_top_altered = "*"+global_tonality+":\t"+"*"+global_tonality+":\t"+"*"+global_tonality+":\t"+"*"+global_tonality+":\t*" + \
        global_tonality+":\n*M"+global_rhythm[0]+"/4\t*M"+global_rhythm[0] + \
        "/4\t*M"+global_rhythm[0]+"/4\t*M"+global_rhythm[0]+"/4\t*"+ "\n*MM"+global_tempo.split('.')[0]+"\t*MM"+global_tempo.split('.')[0] + "\t*MM"+global_tempo.split('.')[0]+"\t*MM"+ global_tempo.split('.')[0]+"\t*" + "\n*SS"+global_style+"\t*SS"+global_style + "\t*SS"+global_style+"\t*SS"+ global_style +"\t*"
    
    kern_song_first_measure = "=1\t=1\t=1\t=1\t=1\n*\t*^\t*^\t*\t*"

    kern_song_title_part = kern_song_title_part_1 + "\n" + \
        kern_song_top_altered + "\n" + kern_song_first_measure

    def find_measure_rythm(measure):
        if global_rhythm[0] == re.findall(r'\d+', measure.columns[2])[0]:
            return int(global_rhythm[0])


    def quantizeNotes(note):
        if not pd.isna(note):
            myList = [0.25, 0.333, 0.5, 0.666, 0.75, 1]

            return min(myList, key=lambda x: abs(x-note))
        else:
            return None
        
    def quantizeDupleNotes(note):
        if not pd.isna(note):
            myList = [0.25, 0.5, 0.75, 1]

            return min(myList, key=lambda x: abs(x-note))
        else:
            return None
    
    def quantizeTripleNotes(note):
        if not pd.isna(note):
            myList = [0.333, 0.666]

            return min(myList, key=lambda x: abs(x-note))
        else:
            return None
    
    def sum_numeric_values_from_df(df):
        """
        Converts the values in a specified column of a pandas DataFrame to numeric type,
        filters out NaN values from the column, calculates the sum of the remaining
        numeric values in the column, and returns the sum.
    
        Args:
            df (pandas.DataFrame): The pandas DataFrame to process.
            column_name (str): The name of the column to process.
    
        Returns:
            float: The sum of the remaining numeric values in the column.
        """
        # convert the values in the specified column to numeric type
        df = df.apply(pd.to_numeric, errors='coerce')

        # filter out NaN values from all columns
        df = df.dropna()
    
        # calculate the sum of the remaining numeric values in all columns
        sum_values = df.sum().sum()
    
        return sum_values
        
    
    def note_duration(note):
        if not pd.isna(note):

            result = str

            if int(note) == 4:
                result = "1"
            elif int(note) == 3:
                result = "2."
            elif int(note) == 2:
                result = "2"
            elif int(note) == 1:
                result = '4'
            elif float(note) == 0.750:
                result = "8."
            elif float(note) == 0.666:
                result = "6"
            elif float(note) == 0.5:
                result = '8'
            elif float(note) == 0.333:
                result = "12"
            elif float(note) == 0.25:
                result = "16"
            elif float(note) == 0.125:
                result = "32"
            return result
        else:
            return float('NaN')


    indexes_in_quarter_notes = []


    def find_quantized_indexes(durationIndex):

        for i in range(len(durationIndex)):

            if float(durationIndex.iloc[i]).is_integer():
                indexes_in_quarter_notes.append(durationIndex.index[i])

        return indexes_in_quarter_notes


    def find_chord_font_from_symbolic_type(chord_symbol):
        accidental_symbols = ['-', 'b', '#']
        root_idx = 1
        if len(chord_symbol) > 1 and chord_symbol[1] in accidental_symbols:
            root_idx = 2
        symbolic_root = chord_symbol[:root_idx]
        # get bass
        has_nine = False
        if '/9' in chord_symbol:
            has_nine = True
        bass_split = chord_symbol[root_idx:].split('/')

        # TODO: fix polychords
        if has_nine:
            symbolic_type = ('/').join(bass_split[:2])
        else:
            symbolic_type = bass_split[0]
        if symbolic_type == '':
            symbolic_type = ' '

        if root_idx == 1:
            chord_symbol_for_kern = chord_symbol[:root_idx] + " " + \
                fonts_mapping[symbolic_type]
        else:

            chord_symbol_for_kern = chord_symbol[:1] + accidental_symbols_mapping[chord_symbol[1]] + " " + \
                fonts_mapping[symbolic_type]

        return chord_symbol_for_kern


    measures = []
    
    for i in range(len(df_measure_start.index)):
        if i < len( df_measure_start.index )-1:
            measures.append(df.iloc[df_measure_start.iloc[i].name:df_measure_start.iloc[(i+1)].name])
        else:
            measures.append(df.iloc[df_measure_start.iloc[i].name:-1])
    
    def set_measure_rhythm(measure):

        if global_rhythm[0] == re.findall(r'\d+', measure.columns[2])[0]:
            return int(global_rhythm[0])

    def set_measure_style(measure):
        m = ["", True]
        m[0] = measure.iloc[0, 1].replace(" ", "")
        if m[0] != global_style:
            m[1] = True
        else:
            m[1] = False
        return m


    def set_measure_tempo(measure):
        m = ["", True]
        m[0] = measure.iloc[0, 4]
        if m[0] != float(global_tempo):
            m[1] = True
        else:
            m[1] = False
        return m


    def set_measure_tonality(measure):
        m = measure.iloc[0, 3].replace(" ", "")
        return m


    class Measure:
        def __init__(self, measure, measure_count, df_measure_grid):
            # print('measure:', measure)
            
            self.df_measure_grid_notes = copy.deepcopy(df_measure_grid)
            self.kern_grid = copy.deepcopy(df_measure_grid)
            self.kern_grid_notes = copy.deepcopy(self.df_measure_grid_notes)
            self.kern_grid_merge = copy.deepcopy(df_measure_grid)
            self.measure_raw = measure.iloc[:, :]
            # __max__
            # grid for swing and even
            self.even_grid = np.array([0.0, 0.25, 0.333, 0.5, 0.666, 0.75, 1.0, 1.25, 1.333, 1.5, 1.666, 1.75, 2.0, 2.25, 2.333, 2.5, 2.666, 2.75, 3.0, 3.25, 3.333, 3.5, 3.666, 3.75])
            # TODO: adjust off-beats for swing
            self.swing_grid = np.array([0.0, 0.25, 0.333, 0.5, 0.666, 0.75, 1.0, 1.25, 1.333, 1.5, 1.666, 1.75, 2.0, 2.25, 2.333, 2.5, 2.666, 2.75, 3.0, 3.25, 3.333, 3.5, 3.666, 3.75])
            measure_header_string = measure.iloc[0].to_string()
            
            self.time_signature = set_measure_rhythm(measure)
            # self.style = comma_split[1]
            self.style = set_measure_style(measure)
            # self.tonality = comma_split[0]
            self.tonality = set_measure_tonality(measure)
            # self.tempo = comma_split[-1]
            self.tempo = set_measure_tempo(measure)

            if self.style[1] == True or measure_count == 0:
                self.style_change = pd.DataFrame(
                    [["!", "!", "!", "!", "!", "!LO:TX:a:t="+str(self.style[0]), "!"]], columns=names_grid)
                

            if self.tempo[1] == True or measure_count == 0:
                self.tempo_change = pd.DataFrame(
                    [["!", "!", "!", "!", "!", "!LO:TX:a:t=[quarter]="+str(self.tempo[0]), "!"]], columns=names_grid)

            # find all durations & notes
            
            duplets_list = [0.25, 0.5, 0.75, 1.25, 1.5, 1.75, 2.25, 2.5, 2.75, 3.25, 3.5, 3,75]
            triplets_list = [0.333, 0.666, 1.333, 1.666, 2.333, 2.666, 3.333, 3.666]
            
            idx_for_duplets_list = [1,3,5,7,9,11,13,15,17,19,21,23]
            idx_for_triplets_list = [2,4,8,10,14,16,20,22]
            idx_quarter_list = [0,6,12,18]
            
            duplets = True
            
            for y in range(len(self.measure_raw)-1,-1,-1):
                #print(y)
                with open('debug_log.txt', 'a') as f:
                    print('self.measure_raw.iloc[y, 0]: ', self.measure_raw.iloc[y, 0], file=f)
                if self.measure_raw.iloc[y, 0] == "Bass":

                    note_onset = float(
                        self.measure_raw.iloc[y, 2]) - measure_count*self.time_signature

                    for i in range(len(self.kern_grid)):

                        if note_onset == float(self.kern_grid.iloc[i, 4]):
                            self.kern_grid.iloc[i, 0] = quantizeNotes(
                                float(self.measure_raw.iloc[y, 3]))
                            self.kern_grid_notes.iloc[i,
                                                    0] = miditokern[self.measure_raw.iloc[y, 1]]
                            break

                elif self.measure_raw.iloc[y, 0] == "Drums":
                    # Load Kick-Snare
                    if int(self.measure_raw.iloc[y, 1]) == 36 or int(self.measure_raw.iloc[y, 1]) == 40:
                        note_onset = float(
                            self.measure_raw.iloc[y, 2]) - measure_count*self.time_signature
                                              
                        for i in range(len(self.kern_grid)):
                            
                            if (math.floor(note_onset * 1000) / 1000) == float(self.kern_grid.iloc[i, 4]):
                                
                                if i in idx_for_duplets_list:
                                    #print(float(self.kern_grid.iloc[i, 4]))
                                    self.kern_grid.iloc[i, 1] = quantizeDupleNotes(float(self.measure_raw.iloc[y, 3]))
                                    
                                elif i in idx_for_triplets_list: 
                                    #print(float(self.kern_grid.iloc[i, 4]))
                                    self.kern_grid.iloc[i, 1] = quantizeTripleNotes(float(self.measure_raw.iloc[y, 3]))
                                elif i in idx_quarter_list and sum_numeric_values_from_df(self.kern_grid.iloc[i:i+5, 2])%0.333 == 0:
                                    self.kern_grid.iloc[i, 1] = quantizeTripleNotes(float(self.measure_raw.iloc[y, 3]))
                                    
                                else:
                                    self.kern_grid.iloc[i, 1] = quantizeDupleNotes(float(self.measure_raw.iloc[y, 3]))
                                    
                                    
                                    
                                if int(self.measure_raw.iloc[y, 1]) == 36:
                                    self.kern_grid_notes.iloc[i, 1] = "Rf"+'\\'
                                elif int(self.measure_raw.iloc[y, 1]) == 40:
                                    self.kern_grid_notes.iloc[i, 1] = "Rcc"+'\\'
                                break
                            #print(self.kern_grid.iloc[10, 1])
# =============================================================================
#                         note_onset = float(self.measure_raw.iloc[y, 2]) - measure_count * self.time_signature
#                         print(round(note_onset, 3), self.measure_raw.iloc[y, 1])
#                         i, quantized_onset = self.find_nearest( self.even_grid, note_onset )
#                         if int(self.measure_raw.iloc[y, 1]) == 36:
#                             self.kern_grid_notes.iloc[i, 1] = "Rf"+'\\'
#                             self.kern_grid.iloc[i, 1] = quantizeNotes(
#                                      float(self.measure_raw.iloc[y, 3]))
#                         elif int(self.measure_raw.iloc[y, 1]) == 40:
#                             self.kern_grid_notes.iloc[i, 1] = "Rcc"+'\\'
#                             self.kern_grid.iloc[i, 1] = quantizeNotes(
#                                      float(self.measure_raw.iloc[y, 3]))
# =============================================================================
                        
                    # Load Hi-Hats
                    elif int(self.measure_raw.iloc[y, 1]) == 59 or int(self.measure_raw.iloc[y, 1]) == 44:
# =============================================================================
#                         note_onset = float(self.measure_raw.iloc[y, 2]) - measure_count * self.time_signature
#                         i, quantized_onset = self.find_nearest( self.even_grid, note_onset )
#                         self.kern_grid_notes.iloc[i, 2] = "Ree/"
#                         self.kern_grid.iloc[i, 2] = quantizeNotes(
#                                      float(self.measure_raw.iloc[y, 3]))
# =============================================================================
                        note_onset = float(
                            self.measure_raw.iloc[y, 2]) - measure_count*self.time_signature
                        we_quantize_in_duplets = True
                        for i in range(len(self.kern_grid)):
                            #print(i)
                            if (math.floor(note_onset * 1000) / 1000) == float(self.kern_grid.iloc[i, 4]):
                                
                                        
                                if i in idx_for_duplets_list:
                                    #print(float(self.kern_grid.iloc[i, 4]))
                                    self.kern_grid.iloc[i, 2] = quantizeDupleNotes(float(self.measure_raw.iloc[y, 3]))
                                    self.kern_grid_notes.iloc[i, 2] = "Ree/"
                                elif i in idx_for_triplets_list: 
                                    #print(float(self.kern_grid.iloc[i, 4]))
                                    self.kern_grid.iloc[i, 2] = quantizeTripleNotes(float(self.measure_raw.iloc[y, 3]))
                                    self.kern_grid_notes.iloc[i, 2] = "Ree/"
                                elif i in idx_quarter_list and sum_numeric_values_from_df(self.kern_grid.iloc[i:i+5, 2])%0.333 == 0:
                                    self.kern_grid.iloc[i, 2] = quantizeTripleNotes(float(self.measure_raw.iloc[y, 3]))
                                    self.kern_grid_notes.iloc[i, 2] = "Ree/"
                                else:
                                    self.kern_grid.iloc[i, 2] = quantizeDupleNotes(float(self.measure_raw.iloc[y, 3]))
                                    self.kern_grid_notes.iloc[i, 2] = "Ree/"
                                    
                                
                               
                                    
                                    #(self.kern_grid.iloc[i, 2], i, duplets)
                                
                                #print()
                                break
                            
    # =============================================================================
    #                 else:
    #                     self.kern_grid.iloc[i,2] = quantizeNotes(float(self.measure_raw.iloc[y,3]))
    #                     self.kern_grid_notes.iloc[i,2] = "r";
    #                     break;
    # =============================================================================

                elif self.measure_raw.iloc[y, 0] == "Piano":

                    if int(self.measure_raw.iloc[y, 1]) < 60:

                        note_onset = float(
                            self.measure_raw.iloc[y, 2]) - measure_count*self.time_signature

                        for i in range(len(self.kern_grid)):

                            if note_onset == float(self.kern_grid.iloc[i, 4]):
                                self.kern_grid.iloc[i, 3] = quantizeNotes(
                                    float(self.measure_raw.iloc[y, 3]))
                                if self.kern_grid_notes.iloc[i, 3] == '.':
                                    self.kern_grid_notes.iloc[i,
                                                            3] = miditokern[self.measure_raw.iloc[y, 1]]

                                else:
                                    self.kern_grid_notes.iloc[i, 3] = str(
                                        self.kern_grid_notes.iloc[i, 3]) + ' ' + miditokern[self.measure_raw.iloc[y, 1]]
                                break

                    elif int(self.measure_raw.iloc[y, 1]) >= 60:

                        note_onset = float(
                            self.measure_raw.iloc[y, 2]) - measure_count*self.time_signature

                        for i in range(len(self.kern_grid)):

                            if note_onset == float(self.kern_grid.iloc[i, 4]):
                                self.kern_grid.iloc[i, 5] = quantizeNotes(
                                    float(self.measure_raw.iloc[y, 3]))
                                if self.kern_grid_notes.iloc[i, 5] == '.':
                                    self.kern_grid_notes.iloc[i,
                                                            5] = miditokern[self.measure_raw.iloc[y, 1]]
                                else:
                                    self.kern_grid_notes.iloc[i, 5] = str(
                                        self.kern_grid_notes.iloc[i, 5]) + ' ' + miditokern[self.measure_raw.iloc[y, 1]]
                                break

                elif self.measure_raw.iloc[y, 0] == "Chord":
                    note_onset = float(self.measure_raw.iloc[y, 3]) - measure_count * self.time_signature
                    i, quantized_onset = self.find_nearest( self.even_grid, note_onset )
                    with open('debug_log.txt', 'a') as f:
                        print('note_onset - Chords: ', note_onset, file=f)
                        print('quantized_onset: ', quantized_onset, file=f)
                    self.kern_grid.iloc[i, 6] = ""
                    self.kern_grid_notes.iloc[i, 6] = find_chord_font_from_symbolic_type(str(self.measure_raw.iloc[y, 1]))
                    
                    
            #Beautify kern file extinguishing useless pauses:     
            for y in range(len(self.kern_grid.columns)-1):
                if y == 4:
                    continue
                for d in range(0, len(self.kern_grid), 6):
                    
                    if sum_numeric_values_from_df(self.kern_grid.iloc[d:d+5, y]) == self.kern_grid.iloc[d, y]:
                        for i in range(d, d+5):
                            if i == d:
                                self.kern_grid.iloc[i, y] = 1
                            else:
                                self.kern_grid.iloc[i, y] = "."
                                self.kern_grid_notes.iloc[i, y] = "."
                        
                    
                    
            self.kern_grid = self.kern_grid.replace(
                to_replace=["."], value=float('nan'))
            self.kern_grid_notes = self.kern_grid_notes.replace(
                to_replace=["."], value=float('nan'))
            #print(self.kern_grid_notes)
            y = 0
            k = 0
            pause_position = ""
            for i in range(len(self.kern_grid)):
                for y in range(len(self.kern_grid.columns)-1):

                    # Assign pause position to each instrument
                    
                    pause_position = pause_position_dictionary[str(y)]
                    

                    if self.kern_grid.iloc[0+k:5+k, y].sum() == 0:
                        self.kern_grid.iloc[k, y] = 1
                        self.kern_grid_notes.iloc[k, y] = "r" + pause_position
                    
                    #if measure_count == 0 :
                        #print(self.kern_grid)
                        
                    
                    if self.kern_grid.iloc[0+k:5+k, y].sum() != 1:
                        if self.kern_grid.iloc[0+k:5+k, y].sum() % (0.250) == 0:
                            if self.kern_grid.iloc[0+k:5+k, y].sum() == 0.250:

                                if math.isnan(self.kern_grid.iloc[k, y]):
                                    self.kern_grid.iloc[k, y] = 0.250
                                    self.kern_grid_notes.iloc[k,
                                                            y] = "r" + pause_position
                                if math.isnan(self.kern_grid.iloc[k+1, y]):
                                    self.kern_grid.iloc[k+1, y] = 0.250
                                    self.kern_grid_notes.iloc[k+1,
                                                            y] = "r" + pause_position
                                if math.isnan(self.kern_grid.iloc[k+1, y]):
                                    self.kern_grid.iloc[k+3, y] = 0.250
                                    self.kern_grid_notes.iloc[k+3,
                                                            y] = "r" + pause_position
                                if math.isnan(self.kern_grid.iloc[k+1, y]):
                                    self.kern_grid.iloc[k+5, y] = 0.250
                                    self.kern_grid_notes.iloc[k+5,
                                                            y] = "r" + pause_position
                                
                            elif self.kern_grid.iloc[0+k:5+k, y].sum() == 0.500:
                                if math.isnan(self.kern_grid.iloc[k+0, y]) and self.kern_grid.iloc[k+1, y] != 0.250:
                                    self.kern_grid.iloc[k+0, y] = 0.500
                                    self.kern_grid_notes.iloc[k,
                                                            y] = "r" + pause_position
                                if math.isnan(self.kern_grid.iloc[k+3, y]) and self.kern_grid.iloc[k+5, y] != 0.250:
                                    self.kern_grid.iloc[k+3, y] = 0.500
                                    self.kern_grid_notes.iloc[k+3,
                                                            y] = "r" + pause_position
                                    
                                
                            elif self.kern_grid.iloc[0+k:5+k, y].sum() == 0.750:
                                if self.kern_grid.iloc[k, y] == 0.750:
                                    self.kern_grid.iloc[k+5, y] = 0.250
                                    self.kern_grid_notes.iloc[k+5,
                                                            y] = "r" + pause_position
                                elif self.kern_grid.iloc[k+1, y] == 0.750:
                                    self.kern_grid.iloc[k, y] = 0.250
                                    self.kern_grid_notes.iloc[k+5,
                                                            y] = "r" + pause_position
                                else:
                                    if math.isnan(self.kern_grid.iloc[k, y]):
                                        self.kern_grid.iloc[k, y] = 0.250
                                        self.kern_grid_notes.iloc[k,
                                                                y] = "r" + pause_position
                                    if math.isnan(self.kern_grid.iloc[k+1, y]):
                                        self.kern_grid.iloc[k+1, y] = 0.250
                                        self.kern_grid_notes.iloc[k+1,
                                                                y] = "r" + pause_position
                                    if math.isnan(self.kern_grid.iloc[k+1, y]):
                                        self.kern_grid.iloc[k+3, y] = 0.250
                                        self.kern_grid_notes.iloc[k+3,
                                                                y] = "r" + pause_position
                                    if math.isnan(self.kern_grid.iloc[k+1, y]):
                                        self.kern_grid.iloc[k+5, y] = 0.250
                                        self.kern_grid_notes.iloc[k+5,
                                                                y] = "r" + pause_position
                        
                            
                        elif self.kern_grid.iloc[0+k:5+k, y].sum() % (0.333) == 0:
                            if self.kern_grid.iloc[0+k:5+k, y].sum() == 0.333:

                                if math.isnan(self.kern_grid.iloc[k, y]):
                                    self.kern_grid.iloc[k, y] = 0.333
                                    self.kern_grid_notes.iloc[k,
                                                            y] = "r" + pause_position
                                if math.isnan(self.kern_grid.iloc[k+2, y]):
                                    self.kern_grid.iloc[k+2, y] = 0.333
                                    self.kern_grid_notes.iloc[k+2,
                                                            y] = "r" + pause_position
                                if math.isnan(self.kern_grid.iloc[k+4, y]):
                                    self.kern_grid.iloc[k+4, y] = 0.333
                                    self.kern_grid_notes.iloc[k+4,
                                                            y] = "r" + pause_position

                            elif self.kern_grid.iloc[0+k:5+k, y].sum() == 0.666:
                                if self.kern_grid.iloc[k, y] == 0.666:
                                    self.kern_grid.iloc[k+4, y] = 0.333
                                    self.kern_grid_notes.iloc[k+4,
                                                            y] = "r" + pause_position
                                elif self.kern_grid.iloc[k+2, y] == 0.666:
                                    self.kern_grid.iloc[k, y] = 0.333
                                    self.kern_grid_notes.iloc[k,
                                                            y] = "r" + pause_position
                                else:
                                    if math.isnan(self.kern_grid.iloc[k, y]) and self.kern_grid.iloc[k, y] != 0.333:
                                        self.kern_grid.iloc[k, y] = 0.333
                                        self.kern_grid_notes.iloc[k,
                                                                y] = "r" + pause_position
                                    if math.isnan(self.kern_grid.iloc[k+2, y]) and self.kern_grid.iloc[k+2, y] != 0.333:
                                        self.kern_grid.iloc[k+2, y] = 0.333
                                        self.kern_grid_notes.iloc[k+2,
                                                                y] = "r" + pause_position

                    if i > 5 and i <= 11:
                        k = 6

                    elif i > 11 and i <= 17:
                        k = 12

                    elif i > 17 and i <= 23:
                        k = 18
            
            for i in range(len(self.kern_grid)):
                for y in range(len(self.kern_grid.columns)-1):
                    #self.kern_grid.iloc[i,y] = 'x'
                    self.kern_grid.iloc[i, y] = note_duration(
                        round(self.kern_grid.iloc[i, y], 3))
            for i in range(len(self.kern_grid)):
                if i == 0:
                    self.kern_grid.iloc[i, 4] = "1ryy"
                    self.kern_grid_notes.iloc[i, 4] = ""
                else:
                    self.kern_grid.iloc[i, 4] = "."
                    self.kern_grid_notes.iloc[i, 4] = "."

            self.kern_grid.fillna(".", inplace=True)
            self.kern_grid_notes.fillna(".", inplace=True)


# =============================================================================
#             #Beautify kern file extinguishing useless pauses:     
#             for y in range(len(self.kern_grid.columns)-1):
#                 if y == 4 or y==2:
#                     continue
#                 for d in range(0, len(self.kern_grid), 6):
#                     contained_pause_df = self.kern_grid_notes.iloc[d:d+6, y].str.contains("r")
#                     contained_dots_df = self.kern_grid_notes.iloc[d:d+6, y].str.contains(re.escape("."))
#                     for i in range(d, d+6):
#                         if contained_pause_df.iloc[0] == False and not (contained_pause_df.iloc[:]).value_counts()[False] <= 1:
#                             print(contained_pause_df.iloc[:])
#                             if i == d:
#                                 self.kern_grid.iloc[i, y] = "4"
#                             else:
#                                 self.kern_grid.iloc[i, y] = "."
#                                 self.kern_grid_notes.iloc[i, y] = "."
# =============================================================================
                            # print(self.kern_grid.iloc[i, y],self.kern_grid_notes.iloc[i, y])

            
            for i in range(len(self.kern_grid)):
                for y in range(len(self.kern_grid.columns)):
                    if self.kern_grid.iloc[i, y] != ".":
                        self.kern_grid_merge.iloc[i, y] = str(
                            self.kern_grid.iloc[i, y]) + str(self.kern_grid_notes.iloc[i, y])
                    else:
                        self.kern_grid_merge.iloc[i, y] = "."

            # Add top of each measure
            if measure_count < len(measures) and not measure_count == 0:
                if self.style[1] == True and self.tempo[1] == True:
                    df_measurebegining_part_one = pd.DataFrame([["="+str(measure_count+1), "="+str(measure_count+1), "="+str(measure_count+1), "="+str(
                        measure_count+1), "="+str(measure_count+1), "="+str(measure_count+1), "="+str(measure_count+1)]], columns=names_grid)
                    df_measurebegining_part_two = pd.DataFrame(
                        [["*", "*head:regular", "*head:x", "*", "*", "*", "*"]], columns=names_grid)
                    df_measureending = pd.concat(
                        [df_measurebegining_part_one, df_measurebegining_part_two])
                    df_measureending = pd.concat(
                        [df_measureending, self.tempo_change])
                    df_measureending = pd.concat(
                        [df_measureending, self.style_change])
                elif self.style[1] == True and self.tempo[1] == False:
                    df_measurebegining_part_one = pd.DataFrame([["="+str(measure_count+1), "="+str(measure_count+1), "="+str(measure_count+1), "="+str(
                        measure_count+1), "="+str(measure_count+1), "="+str(measure_count+1), "="+str(measure_count+1)]], columns=names_grid)
                    df_measurebegining_part_two = pd.DataFrame(
                        [["*", "*head:regular", "*head:x", "*", "*", "*", "*"]], columns=names_grid)
                    df_measureending = pd.concat(
                        [df_measurebegining_part_one, df_measurebegining_part_two])
                    df_measureending = pd.concat(
                        [df_measureending, self.style_change])
                elif self.style[1] == False and self.tempo[1] == True:
                    df_measurebegining_part_one = pd.DataFrame([["="+str(measure_count+1), "="+str(measure_count+1), "="+str(measure_count+1), "="+str(
                        measure_count+1), "="+str(measure_count+1), "="+str(measure_count+1), "="+str(measure_count+1)]], columns=names_grid)
                    df_measurebegining_part_two = pd.DataFrame(
                        [["*", "*head:regular", "*head:x", "*", "*", "*", "*"]], columns=names_grid)
                    df_measureending = pd.concat(
                        [df_measurebegining_part_one, df_measurebegining_part_two])
                    df_measureending = pd.concat(
                        [df_measureending, self.tempo_change])
                else:
                    df_measurebegining_part_one = pd.DataFrame([["="+str(measure_count+1), "="+str(measure_count+1), "="+str(measure_count+1), "="+str(
                        measure_count+1), "="+str(measure_count+1), "="+str(measure_count+1), "="+str(measure_count+1)]], columns=names_grid)
                    df_measurebegining_part_two = pd.DataFrame(
                        [["*", "*head:regular", "*head:x", "*", "*", "*", "*"]], columns=names_grid)
                    df_measureending = pd.concat(
                        [df_measurebegining_part_one, df_measurebegining_part_two])
            if measure_count == 0:
                df_measurebegining_part_two = pd.DataFrame(
                    [["*", "*head:regular", "*head:x", "*", "*", "*", "*"]], columns=names_grid)
                self.tempo_change = pd.concat([df_measurebegining_part_two,self.tempo_change])
                self.kern_grid_merge = pd.concat(
                    [self.style_change, self.kern_grid_merge])
                self.kern_grid_merge = pd.concat(
                    [self.tempo_change, self.kern_grid_merge])
               
            if not measure_count == 0:
                self.kern_grid_merge = pd.concat(
                    [df_measureending, self.kern_grid_merge])
        # end __init__
        def find_nearest(self, array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return idx, array[idx]
        # end __find_nearest__


    df_list = []

    for i in range(len(measures)):

        df_list.append(Measure(measures[i], i, df_measure_grid).kern_grid_merge)

    df_proto = pd.concat(df_list, ignore_index=True)

    # Write to txt file
    if os.path.exists("demofile.txt"): 
        os.remove('xgboost.txt')
    df_proto.to_csv('xgboost.txt', header=False, index=False,
                    sep='\t', mode='a', na_rep='')

    # Pre-appendbeginning of kern file
    with open('xgboost.txt', "r+") as f:
        old = f.read()  # read everything in the file
        f.seek(0)  # rewind
        f.write(kern_song_title_part + "\n" + old)  # write the new line before

    # Append ending of kern file
    trackending = "==\t==\t==\t==\t==\t==\t==\n*-\t*-\t*-\t*-\t*-\t*-\t*-\n!!!system-decoration: {(s1,s2)}s3,s4e"
    
    out_string = df_proto.to_csv(index=False, header=False, sep='\t')
    
    return kern_song_title_part + '\n' + out_string + '\n' + trackending

csv2kern("../data/csvs/A_CHILD_IS_BORN_r~1_h~1.csv")
