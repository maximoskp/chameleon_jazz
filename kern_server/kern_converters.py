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

    # sum all column, find the lowest, assign it to a list, keep only the values that carries a chard an append it to chart variable
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
    return chart
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

def kern2string(file_name):
    p = kern2py(file_name)
    # print('p: ', p)
    string = 'section~A'
    string += ',style~' + p['style']
    string += ',tempo~' + p['tempo']
    string += ',tonality~' + 'C' # TODO: tonality
    for b in p['bars']:
        # print('b:', b)
        string += ',bar~' + '4/4' # TODO: time sig
        for i in range(b.shape[0]):
            t = str( b.iloc[i][0] )
            c = b.iloc[i]['Chords'] # TODO: translate to GJT chord
            # it appears that there is always a space between root and type
            # print(c)
            chord_split = c.split(' ')
            acc_chord = chord_split[0]
            if len(acc_chord) > 1:
                # print('acc_chord:', acc_chord)
                acc_chord = acc_chord.replace( acc_chord[1], fonts2acc[ acc_chord[1] ] )
            if len(chord_split) > 1:
                # type other than "major", i.e. no type
                string += ',chord~' + acc_chord + fonts2types[chord_split[1]] + '@' + t
            else:
                string += ',chord~' + acc_chord + '@' + t
            # string += ',chord~' + c + '@' + t
    string += ',end'
    return string

def csv2kern(filename):
    names = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    names_grid = ['Bass', 'Kick-Snare', 'Hihat', 'Piano-F-Clef', 'empty', 'Piano-G-Clef', 'Chords']
    df_proto = pd.read_csv("kern_init.krn", sep='\t', names=names)
    df_proto = df_proto.iloc[0:16]
    # with open(filename, 'rb') as rawdata:
    #     result = chardet.detect(rawdata.read(100000))
    result = chardet.detect( str.encode( filename.getvalue() ) )
    # print('encoding: ', result["encoding"])


    if result["encoding"] == "utf-16":
        df = pd.read_csv(filename, sep='\,', encoding=result["encoding"])
        for i in range(len(df.columns)-1):
            df.iloc[:, i] = df.iloc[:, i].str.replace(" ", "")
    else:
        df = pd.read_csv(filename, sep='\n', encoding=result["encoding"])
    # print('df: ', df)

    df_measure_start = df.loc[df.iloc[:, 0].str.contains("Bar")]

    # TODO find measure rythm
    # print('df.columns: ', df.columns)
    # print('df.columns[0].split(, ): ', df.columns[0].split(', '))
    column_split = df.columns[0].split(', ')
    # print('column_split:', column_split)
    # global_rhythm = re.findall(r'\d+', df.columns[0][2])
    global_rhythm = column_split[2].split('/')
    # print('global_rhythm: ', global_rhythm)

    # print('df_measure_start: ', df_measure_start)
    # global_style = df_measure_start.iloc[0, 1].replace(" ", "")
    global_style = df.columns[0][1].replace(' ', '')

    # global_tempo = df_measure_start.iloc[0, 4]
    global_tempo = df.columns[0][4].replace(' ', '')

    # song_title = file[:len(file) - 12]
    song_title = 'test'
    global_tonality = df.columns[0][0]
    kern_song_title_part_1 = "!!!system-decoration: \\{(s1,s2)\\}s3,s4\\" + "\n" + "!!!OTL: " + song_title + "\n" + \
        "**kern	**kern	**kern	**kern	**mxhm\n*part3	*part2	*part1	*part1	*part1\n*staff4	*staff3	*staff2	*staff1	*\n*I'Contrabass'	*I'Drumset'	*'IPiano'	*	*\n*I'Cb.	*I'D. Set	*I'Pno.	*	*\n*clefF4	*clefX	*clefF4	*clefG2	*\n*k[b-e-a-]	*k[]	*k[b-e-a-]	*k[b-e-a-]	*"
    kern_song_top_altered = "*"+global_tonality+": 	*"+global_tonality+":	*"+global_tonality+":	*"+global_tonality+":	*" + \
        global_tonality+":\n*M"+global_rhythm[0]+"/4	*M"+global_rhythm[0] + \
        "/4	*M"+global_rhythm[0]+"/4	*M"+global_rhythm[0]+"/4	*"
    kern_song_first_measure = "=1	=1	=1	=1	=1\n*	*^	*^	*	*"

    kern_song_title_part = kern_song_title_part_1 + "\n" + \
        kern_song_top_altered + "\n" + kern_song_first_measure

    fonts_mapping = {
        " ": "", "": "", "7": "7", "9": "9", "7b9": "S", "7#9": "s", "7#11": "t", "7b5": "p", "7#5": "q", "9#11": "r", "9b5": "T", "9#5": "n", "9b13": "2", "7#9#5": "M", "7#9b5": "O", "7#9#11": "N", "7b9#11": "P", "7b9b5": "L", "7b9#5": "J", "7b9#9": "K", "7b9b13": "I", "7alt": "?", "13": "U", "13#11": "l", "13b9": "u", "13#9": "o", "replacedby7sus": "A", "deleted": "A", "replacedby7b9sus": "v", "replacedby7aad3sus": "H", "replacedby9sus": "B", "replacedby13sus": "C", "replacedby7b13sus": "w", "m": "a", "m7": "b", "m9": "h", "m11": "i", "\u00f87": "W", "\u00f811": "Y", "\u00f89": "X", "m\u03947": "f", "m\u03949": "g", "o7": "8", "o": ">", "m6": "j", "m6/9": "Z", "mb6": "R", "m13": "3", "m(#5)": "V", "add9": "=", "6": "6", "6/9": "k", "replacedbysus": "4", "replacedby+": "G", "\u03947": "c", "\u03949": "d", "\u03947#11": "x", "\u03947#5": "z", "\u03949#11": "y", "\u03947b5": "1", "\u039413": "e", "7b13": "m", "7#9b13": "0", "11": "Q", "5": "5", "madd9": "%", "7b9sus": "v", "7add3sus": "H", "9sus": "]", "13sus": "<", "7b13sus": "w", "7sus": "[", "+": "@", "sus": "4", "nan": "nan", "/": "nan", "/m": "nan", "/7": "nan", "/\u03947": "nan", "/m7": "nan", "/m\u03947": "nan", "barline": "0", "doublebarline": "1", "repeatStart": "2", "repeatEnd": "3", "accentUpbeat": "h", "accentDownbeat": "i", "samebar": "%", "repeatVersionStart~1": "4", "repeatVersionStart~2": "5", "repeatVersionStart~3": "6", "repeatVersionStart~4": "7", "sharp": "+", "flat": "&", "/A": "a", "/B": "b", "/C": "c", "/D": "d", "/E": "e", "/F": "f", "/G": "g", "/Ab": "h", "/Bb": "i", "/Cb": "j", "/Db": "k", "/Eb": "l", "/Gb": "n", "/A#": "o", "/C#": "q", "/D#": "r", "/F#": "t", "/G#": "u", "section~A": "A", "section~B": "B", "section~C": "C", "section~D": "D", "section~E": "E", "A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F", "G": "G", "2/4": "a", "3/4": "b", "4/4": "c", "5/4": "d", "6/4": "e", "7/4": "f", "8/4": "g", "9/4": "h", "10/4": "i", "11/4": "j", "12/4": "k", "13/4": "l", "14/4": "m", "15/4": "n", "16/4": "o", "17/4": "p"}

    accidental_symbols_mapping = {"-": "", "b": "&", "#": "+"}
    # =============================================================================
    # #fonts_mapping = {
    #     " ": "", "": "", "7": "7", "9": "9", "7b9": "S", "7#9": "s", "7#11": "t", "7b5": "p", "7#5": "q", "9#11": "r", "9b5": "T", "9#5": "n", "9b13": "2", "7#9#5": "M", "7#9b5": "O", "7#9#11": "N", "7b9#11": "P", "7b9b5": "L", "7b9#5": "J", "7b9#9": "K", "7b9b13": "I", "7alt": "F", "13": "U", "13#11": "l", "13b9": "u", "13#9": "o", "replacedby7sus": "A", "deleted": "A", "replacedby7b9sus": "v", "replacedby7aad3sus": "H", "replacedby9sus": "B", "replacedby13sus": "C", "replacedby7b13sus": "w", "m": "a", "m7": "b", "m9": "h", "m11": "i", "\u00f87": "W", "\u00f811": "Y", "\u00f89": "X", "m\u03947": "f", "m\u03949": "g", "o7": "8", "o": "E", "m6": "j", "m6/9": "Z", "mb6": "R", "m13": "3", "m(#5)": "V", "add9": "D", "6": "6", "6/9": "k", "replacedbysus": "4", "replacedby+": "G", "\u03947": "c", "\u03949": "d", "\u03947#11": "x", "\u03947#5": "z", "\u03949#11": "y", "\u03947b5": "1", "\u039413": "e", "7b13": "m", "7#9b13": "0", "11": "Q", "5": "5", "madd9": "%", "7b9sus": "v", "7add3sus": "H", "9sus": "B", "13sus": "C", "7b13sus": "w", "7sus": "A", "+": "G", "sus": "4", "nan": "nan", "/": "nan", "/m": "nan", "/7": "nan", "/\u03947": "nan", "/m7": "nan", "/m\u03947": "nan", "barline": "0", "doublebarline": "1", "repeatStart": "2", "repeatEnd": "3", "accentUpbeat": "h", "accentDownbeat": "i", "samebar": "%", "repeatVersionStart~1": "4", "repeatVersionStart~2": "5", "repeatVersionStart~3": "6", "repeatVersionStart~4": "7", "sharp": "+", "flat": "&", "/A": "a", "/B": "b", "/C": "c", "/D": "d", "/E": "e", "/F": "f", "/G": "g", "/Ab": "h", "/Bb": "i", "/Cb": "j", "/Db": "k", "/Eb": "l", "/Gb": "n", "/A#": "o", "/C#": "q", "/D#": "r", "/F#": "t", "/G#": "u", "section~A": "A", "section~B": "B", "section~C": "C", "section~D": "D", "section~E": "E", "A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F", "G": "G", "2/4": "a", "3/4": "b", "4/4": "c", "5/4": "d", "6/4": "e", "7/4": "f", "8/4": "g", "9/4": "h", "10/4": "i", "11/4": "j", "12/4": "k", "13/4": "l", "14/4": "m", "15/4": "n", "16/4": "o", "17/4": "p"}
    # =============================================================================

    miditokern = {
        '24': "CCC",
        '25': "CCC#",
        '26': "DDD",
        '27': "DDD#",
        '28': "EEE",
        '29': "FFF",
        '30': "FFF#",
        '31': "GGG",
        '32': "GGG#",
        '33': "AAA",
        '34': "AAA#",
        '35': "BBB",
        '36': "CC",
        '37': "CC#",
        '38': "DD",
        '39': "DD#",
        '40': "EE",
        '41': "FF",
        '42': "FF#",
        '43': "GG",
        '44': "GG#",
        '45': "AA",
        '46': "AA#",
        '47': "BB",
        '48': "C",
        '49': "C#",
        '50': "D",
        '51': "D#",
        '52': "E",
        '53': "F",
        '54': "F#",
        '55': "G",
        '56': "G#",
        '57': "A",
        '58': "A#",
        '59': "B",
        '60': "c",
        '61': "c#",
        '62': "d",
        '63': "d#",
        '64': "e",
        '65': "f",
        '66': "f#",
        '67': "g",
        '68': "g#",
        '69': "a",
        '70': "a#",
        '71': "b",
        '72': "cc",
        '73': "cc#",
        '74': "dd",
        '75': "dd#",
        '76': "ee",
        '77': "ff",
        '78': "ff#",
        '79': "gg",
        '80': "gg#",
        '81': "aa",
        '82': "aa#",
        '83': "bb",
        '84': "ccc",
        '85': "ccc#",
        '86': "ddd",
        '87': "ddd#",
        '88': "eee",
        '89': "fff",
        '90': "fff#",
        '91': "ggg",
        '92': "ggg#",
        '93': "aaa",
        '94': "aaa#",
        '95': "bbb",
        '96': "cccc",
        '97': "cccc#",
        '98': "dddd",
        '99': "dddd#",
        '100': "eeee",
        '101': "ffff",
        '102': "ffff#",
        '103': "gggg",
        '104': "gggg#",
        '105': "aaaa",
        '106': "aaaa#",
        '107': "bbbb",
        '108': "cccc",
        '109': "cccc#",
        '110': "dddd",
        '111': "dddd#",
        '112': "eeee",
        '113': "ffff",
        '114': "ffff#",
        '115': "gggg",
        '116': "gggg#",
        '117': "aaaa",
        '118': "aaaa#",
        '119': "bbbb",
        '120': "cccc",
        '121': "cccc#",
        '122': "dddd",
        '123': "dddd#",
        '124': "eeee",
        '125': "ffff",
        '126': "ffff#",
        '127': "gggg"
    }

    utfChordstoKern = {
        'CΔ13': "C maj13",
    }


    def find_measure_rythm(measure):
        if global_rhythm[0] == re.findall(r'\d+', measure.columns[2])[0]:
            return int(global_rhythm[0])


    def quantizeNotes(note):
        if not pd.isna(note):
            myList = [0.25, 0.333, 0.5, 0.666, 0.75, 1]

            return min(myList, key=lambda x: abs(x-note))
        else:
            return None


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
    for i in range(len(df_measure_start.index)-1):
        measures.append(
            df.iloc[df_measure_start.iloc[i].name:df_measure_start.iloc[(i+1)].name])


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
        if m[0] != global_tempo:
            m[1] = True
        else:
            m[1] = False
        return m


    def set_measure_tonality(measure):
        m = measure.iloc[0, 3].replace(" ", "")
        return m


    class Measure:
        def __init__(self, measure, measure_count):
            # print('measure:', measure)
            df_measure_grid = pd.read_csv(
                "kern_measure_grid_empty.krn", sep='\t', names=names_grid)
            df_measure_grid_notes = pd.read_csv(
                "kern_measure_grid_empty.krn", sep='\t', names=names_grid)
            self.kern_grid = df_measure_grid
            self.kern_grid_notes = df_measure_grid_notes
            self.kern_grid_merge = copy.deepcopy(df_measure_grid)
            self.measure_raw = measure.iloc[:, :]
            measure_header_string = measure.iloc[0].to_string()
            # print('measure_header_string:', measure_header_string)
            comma_split = measure_header_string.split(', ')
            self.time_signature = comma_split[2]
            # self.time_signature = set_measure_rhythm(measure)
            self.style = comma_split[1]
            # self.style = set_measure_style(measure)
            self.tonality = comma_split[0]
            # self.tonality = set_measure_tonality(measure)
            self.tempo = comma_split[-1]
            # self.tempo = set_measure_tempo(measure)

            if self.style[1] == True or measure_count == 0:
                self.style_change = pd.DataFrame(
                    [["!", "!", "!", "!", "!", "!LO:TX:a:t="+str(self.style[0]), "!"]], columns=names_grid)
                # print("style_set")

            if self.tempo[1] == True or measure_count == 0:
                self.tempo_change = pd.DataFrame(
                    [["!", "!", "!", "!", "!", "!LO:TX:a:t=[quarter]="+str(self.tempo[0]), "!"]], columns=names_grid)

            # find all durations & notes

            for y in range(len(self.measure_raw)):
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

                            if note_onset == float(self.kern_grid.iloc[i, 4]):
                                self.kern_grid.iloc[i, 1] = quantizeNotes(
                                    float(self.measure_raw.iloc[y, 3]))
                                if int(self.measure_raw.iloc[y, 1]) == 36:
                                    self.kern_grid_notes.iloc[i, 1] = "Rf"+'\\'
                                elif int(self.measure_raw.iloc[y, 1]) == 40:
                                    self.kern_grid_notes.iloc[i, 1] = "Rcc"+'\\'
                                break
                    # Load Hi-Hats
                    elif int(self.measure_raw.iloc[y, 1]) == 59 or int(self.measure_raw.iloc[y, 1]) == 44:
                        note_onset = float(
                            self.measure_raw.iloc[y, 2]) - measure_count*self.time_signature

                        for i in range(len(self.kern_grid)):

                            if note_onset == float(self.kern_grid.iloc[i, 4]):
                                self.kern_grid.iloc[i, 2] = quantizeNotes(
                                    float(self.measure_raw.iloc[y, 3]))
                                self.kern_grid_notes.iloc[i, 2] = "Ree/"
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

                    note_onset = float(
                        self.measure_raw.iloc[y, 3]) - measure_count * self.time_signature

                    for i in range(len(self.kern_grid)):

                        if note_onset == float(self.kern_grid.iloc[i, 4]):
                            self.kern_grid.iloc[i, 6] = ""
                            self.kern_grid_notes.iloc[i, 6] = find_chord_font_from_symbolic_type(str(
                                self.measure_raw.iloc[y, 1]))

                            break

            self.kern_grid = self.kern_grid.replace(
                to_replace=["."], value=float('nan'))
            self.kern_grid_notes = self.kern_grid_notes.replace(
                to_replace=["."], value=float('nan'))

            y = 0
            k = 0
            pause_position = ""
            for i in range(len(self.kern_grid)):
                for y in range(len(self.kern_grid.columns)-1):

                    # Assign pause position to each instrument
                    if y == 0:
                        pause_position = ""
                    elif y == 1:
                        pause_position = "e"
                    elif y == 2:
                        pause_position = "ee"
                    elif y == 3:
                        pause_position = ""
                    elif y == 4:
                        pause_position = ""
                    elif y == 5:
                        pause_position = ""

                    if self.kern_grid.iloc[0+k:5+k, y].sum() == 0:
                        self.kern_grid.iloc[k, y] = 1
                        self.kern_grid_notes.iloc[k, y] = "r" + pause_position

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
                                if math.isnan(self.kern_grid.iloc[k+0, y]) and self.kern_grid.iloc[k+0, y] != 0.250:
                                    self.kern_grid.iloc[k+0, y] = 0.500
                                    self.kern_grid_notes.iloc[k,
                                                            y] = "r" + pause_position
                                if math.isnan(self.kern_grid.iloc[k+3, y]) and self.kern_grid.iloc[k+3, y] != 0.250:
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
                self.kern_grid_merge = pd.concat(
                    [self.style_change, self.kern_grid_merge])
                self.kern_grid_merge = pd.concat(
                    [self.tempo_change, self.kern_grid_merge])
            if not measure_count == 0:
                self.kern_grid_merge = pd.concat(
                    [df_measureending, self.kern_grid_merge])


    df_list = []

    for i in range(len(measures)):

        df_list.append(Measure(measures[i], i).kern_grid_merge)

    df_proto = pd.concat(df_list, ignore_index=True)

    # Write to txt file
    df_proto.to_csv('xgboost.txt', header=False, index=False,
                    sep='\t', mode='a', na_rep='')

    # Pre-appendbeginning of kern file
    with open('xgboost.txt', "r+") as f:
        old = f.read()  # read everything in the file
        f.seek(0)  # rewind
        f.write(kern_song_title_part + "\n" + old)  # write the new line before

    # Append ending of kern file
    trackending = "==	==	==	==	==	==	==\n*-	*-	*-	*-	*-	*-	*-\n!!!system-decoration: {(s1,s2)}s3,s4e"
    # print('kern_song_title_part: \n', kern_song_title_part)
    # print('df_proto.to_string(): \n', df_proto.to_string())
    # return kern_song_title_part + '\n' + '\n' + trackending
    return kern_song_title_part + '\n' + df_proto.to_string() + '\n' + trackending