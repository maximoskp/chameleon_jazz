#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 10:20:01 2023

@author: konstantinosvelenis
"""
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
import pandas as pd
import re
import copy
import math
import chardet
import json
import csv
import random


def kern2csv4player_converter(file, data):
    
    with open('debug_player_log.txt', 'w') as f_pl_debug:
        # Open the file in read mode
        with open('json/kern_to_csv_pitch_dictionary.json', 'r') as myfile:
            # Load the data from the file using json.load() method
            pitch_dictionary = json.load(myfile)
        
        # Open the file in read mode
        with open('json/kern_to_csv_instrument_dictionary.json', 'r') as myfile:
            # Load the data from the file using json.load() method
            instrument_dictionary = json.load(myfile)
        
        
        
        # prefix = "kern/"
        # suffix = ".krn"
        # song_name = file[len(prefix):-len(suffix)]
        
        column_names = ['Contrabass', 'Drums_Snare_Kick',
                        'Drums_hihat', 'Piano_1', 'Blank', 'Piano_2', 'Chords']
        
        starting_df = pd.read_csv(file, sep='\t', names=column_names)
        
        # with open(file, 'rb') as rawdata:
        #     result = chardet.detect(rawdata.read(100000))
        
        # if result["encoding"] == "utf-8":
        #     starting_df = pd.read_csv(file, sep='\;', encoding=result["encoding"])
        # elif result["encoding"] == "UTF-16":
        #     starting_df = pd.read_csv(file, sep='\,', encoding=result["encoding"])
        #     for i in range(len(starting_df.columns)-1):
        #         starting_df.iloc[:, i] = starting_df.iloc[:, i].str.replace(" ", "")
        
        # with open(file, 'r') as file:
        #     data = file.read()
        
        
        # Find the first meter
        def word_search(key, d):
            # # opening the file using with to ensure it closes after the block of code is executed
            # with open(filename.name, "r") as file:
            #     lines = file.readlines()  # reading the lines of the files in order
            lines = d.split('\n')  # reading the lines of the files in order
            # using enumerate to map each line of the file to it's line_number
            # print('lines:', lines)
            for number, line in enumerate(lines, 1):
                if key in line:  # searching for the keyword in file
                    # returning the line number if the keyword
                    
                    start_line = number
                    break
            return start_line
        
        
        keyword = "=1"  # user input of the keyword
        start_line = word_search(keyword, data)-1
        
        last_line = data.count('\n')
        
        testline = data.splitlines()[start_line:]
        
        testline = testline[:]
        
        testline = '\n'.join(testline)
        
        testline = StringIO(testline)
        
        
        df = pd.read_csv(testline, sep='\t', names=column_names)
        
        # Split the DataFrame into a list of dataframes, where each dataframe contains the data for one measure
        
        df_measure_start = df.loc[df.iloc[:, 0].str.contains("=")]
        
        measures = []
        for i in range(len(df_measure_start.index)-1):
            measures.append(
                df.iloc[df_measure_start.iloc[i].name:df_measure_start.iloc[(i+1)].name])
        
        
        def note_duration(note):
            if not pd.isna(note):
        
                result = 'None'
        
                if note == "1":
                    result = "4"
                elif note == '2.':
                    result = "3"
                elif note == "2":
                    result = "2"
                elif note == '4':
                    result = '1'
                elif note == '8.':
                    result = "0.750"
                elif note == '6':
                    result = "0.666"
                elif note == '8':
                    result = '0.5'
                elif note == '12':
                    result = "0.333"
                elif note == '16':
                    result = "0.25"
                elif note == '32':
                    result = "0.125"
                return result
            else:
                return float('NaN')
        
        
        # find global_tempo
        pattern_for_tempo = re.escape('*MM')
        # first_occurrence = df["Piano_2"].str.contains("!LO:TX:a:t=\[quarter\]=")
        first_occurrence_tempo = starting_df.iloc[:, 0].str.contains(pattern_for_tempo)
        print('first_occurrence_tempo: ', first_occurrence_tempo, file=f_pl_debug)
        global_tempo = str(120)
        for i in range(len(first_occurrence_tempo)):
            if first_occurrence_tempo.iloc[i] == True:
                global_tempo = starting_df.iloc[i, 0].replace('*MM', "")
        if global_tempo == '.0':
            global_tempo = str(120)
            # print('global_tempo is zero: ', global_tempo, file=f_pl_debug)
            # global_tempo = data.split('*MM')[1].split('\t')[0]
            # print('global_tempo is not zero', global_tempo, file=f_pl_debug)
        print('global_tempo after all: ', global_tempo, file=f_pl_debug)
        # find global_style
        # find global_style
        pattern_for_style = re.escape('*SS')
        first_occurrence_style = starting_df.iloc[:, 0].str.contains(pattern_for_style)
        for i in range(len(first_occurrence_style)):
            if first_occurrence_style.iloc[i] == True:
        
                global_style = starting_df.iloc[i,0].replace(
                    '*SS', "")
        
        # find global_time_signature
        pattern_for_time_signature = re.escape('*M')
        pattern_for_time_signature2 = re.escape('/')
        first_occurrence_time = starting_df.iloc[:, 0].str.contains(pattern_for_time_signature) & starting_df.iloc[:,0].str.contains(pattern_for_time_signature2) 
        for i in range(len(first_occurrence_time)):
            if first_occurrence_time.iloc[i] == True:
                
                global_time_signature = starting_df.iloc[i, 0].replace(
                    '*M', "")
        
                global_time_signature = global_time_signature.split('/')
        
        
        def find_measure_tempo(measure):
            measure_tempo = ["", False]
            first_occurrence = measure["Piano_2"].str.contains(
                "!LO:TX:a:t=\[quarter\]=")
        
            for i in range(len(first_occurrence)):
                
                if first_occurrence.iloc[i] == True:
                
                    measure_tempo[0] = measure["Piano_2"].iloc[i].replace(
                        '!LO:TX:a:t=[quarter]=', "")
                    measure_tempo[1] = True
                    break
                else:
                    measure_tempo[0] = global_tempo
                    measure_tempo[1] = False
            return measure_tempo
        
        
        def find_measure_style(measure):
            measure_style = ["", False]
            first_occurrence = measure["Piano_2"].str.contains(
                "!LO:TX:a:t=")
            
            first_time_passed = False
            for i in range(len(first_occurrence)):
                
                if first_occurrence.iloc[i] == True and first_occurrence.iloc[i+1] == True:
        
                    measure_style[0] = measure["Piano_2"].iloc[i+1].replace(
                        '!LO:TX:a:t=', "")
                    measure_style[1] = True
                    break
                else:
                    measure_style[0] = global_style 
                    measure_style[1] = False
            return measure_style
        
        
        def valid_note_for_player_CSV(instrument, note_pitch,
                                    note_duration_part, note_onset, note_velocity, measure_count):
            if not instrument == "None" and not note_pitch == None and not note_duration_part == "None" and not note_onset == "None":
                valid_row = [instrument, note_pitch, note_onset + measure_count * int(global_time_signature[0]),
                            note_duration_part, note_velocity]
                return valid_row
            else:
                return False
        
        
        class MeasureforCSV:
        
            def __init__(self, measure, measure_count):
                self.df_measure_grid = pd.read_csv(
                    "kern_measure_grid_empty.krn", sep='\t', names=column_names)
                self.df_measure_grid = self.df_measure_grid['Blank']
                # TODO: If we create rythm & tempo change the following line should change
                self.measure = measure[1:]
                self.measure = self.measure.reset_index()
        
                # create a boolean mask indicating where either '!' or '*' or '=' stops occurring
                mask = self.measure['Contrabass'].str.contains(
                    '!|\*|=').cumsum().duplicated(keep='last')
        
                # find the index where the '!' or '*' or '=' character stops occurring
                stop_idx = mask.idxmax()
        
                # define the number of blank rows to add
                num_blank_rows = stop_idx + 1
        
                # create a new DataFrame with the blank values
                new_data = pd.DataFrame({0: [''] * num_blank_rows})
        
                # concatenate the new DataFrame and the original DataFrame
                self.df_measure_grid = pd.concat(
                    [new_data, self.df_measure_grid], ignore_index=True)
        
                self.measure['Blank'] = self.df_measure_grid
                self.measure_tempo = global_tempo # find_measure_tempo(self.measure)
                self.measure_style = [global_style, False] # find_measure_style(self.measure)
        
                # self.measure_start_line = ["Bar~" + str(measure_count) +
                #                         "@" + str(measure_count * int(global_time_signature[0])), self.measure_style[0], str(global_time_signature[0]) + "/" +str(global_time_signature[1]), "A", self.measure_tempo[0]]
                self.measure_start_line = ["Bar~" + str(measure_count) +
                                       "@" + str(measure_count * int(global_time_signature[0])), self.measure_style[0], str(global_time_signature[0]) + "/" +str(global_time_signature[1]), "A", self.measure_tempo]
            
                self.measure_player_grid = []
                self.measure_player_grid.append(self.measure_start_line)
                for i in range(len(self.measure)):
                    for y in range(len(self.measure.columns)):
                        if y == 1 or y == 2 or y == 3 or y == 4 or y == 6:
        
                            index = 0
                            for x in range(len(str(self.measure.iloc[i, y]))):
                                if str(self.measure.iloc[i, y])[x].isalpha():
                                    index = x
                                    break
        
                            # Split the string based on the index of the letter
                            note_duration_part = str(self.measure.iloc[i, y])[:index]
                            note_pitch = str(self.measure.iloc[i, y])[index:]
                            note_duration_part = note_duration(note_duration_part)
                            note_onset = self.measure.iloc[i, 5]
                            instrument = instrument_dictionary.get(str(y))
                            if " " in note_pitch:
                                note_pitch_list = note_pitch.split()
                                
                                for n in range(len(note_pitch_list)):
                                    
                                    note_pitch = pitch_dictionary.get(note_pitch_list[n])
                                    
                                    if valid_note_for_player_CSV(instrument, note_pitch, note_duration_part, note_onset, random.randint(60, 80), measure_count):
                                        self.measure_player_grid.append(valid_note_for_player_CSV(instrument, note_pitch, note_duration_part, note_onset, random.randint(60, 80), measure_count))
                            else:
                                
                                #prepare the note pitch for the drum notes
                                note_pitch = note_pitch.replace("Rf", "CC").replace("Rcc", "EE").replace("Ree", "GG#").replace("\\", "").replace("/", "")
                                
                                note_pitch = pitch_dictionary.get(note_pitch)
                                
                                if valid_note_for_player_CSV(instrument, note_pitch, note_duration_part, note_onset, random.randint(60, 80), measure_count):
                                    self.measure_player_grid.append(valid_note_for_player_CSV(instrument, note_pitch, note_duration_part, note_onset, random.randint(60, 80), measure_count))
                            
                            
        
                            
        data = []
        
        for i in range(len(measures)):
            data.append(MeasureforCSV(measures[i], i).measure_player_grid)
        
        
        reduced_list = [item for sublist in data for item in sublist]
        
        kern2csv4playerString = ''
        
        for lst in data:
            kern2csv4playerStringByMeasure = '\n'.join([', '.join(map(str, inner_lst)) for inner_lst in lst])
            kern2csv4playerString += kern2csv4playerStringByMeasure + "\n"


        print('kern2csv4playerString:', kern2csv4playerString, file=f_pl_debug)
        
        # with open("CSVs_for_player/" + song_name + '.csv', 'w', newline='') as file:
        #     writer = csv.writer(file)
        #     writer.writerows(reduced_list)

        # make array
        arr = []
        for nl in kern2csv4playerString.split('\n'):
            l = []
            for c in nl.split(', '):
                l.append( c )
            arr.append(l)
        return kern2csv4playerString, arr

# kern2csv4playerString = kern2csv4player_converter("kern/A_WEAVER_OF_DREAMS.krn")
