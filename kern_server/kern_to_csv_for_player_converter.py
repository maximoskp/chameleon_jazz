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
import numpy as np


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
        
        # Open the file in read mode
        with open('json/kern_note_duration_dictionary.json', 'r') as myfile:
            # Load the data from the file using json.load() method
            note_duration_dictionary = json.load(myfile)
        
        # Open the file in read mode
        with open('json/kern_note_duration_kern_to_csv_dictionary.json', 'r') as myfile:
            # Load the data from the file using json.load() method
            note_duration_kern_to_csv_dictionary = json.load(myfile)
        
        orchestra_instruments = ['Violin', 'Viola', 'Cello', 'Double Bass', 'Harp', 'Flute', 'Piccolo', 'Oboe', 'English Horn', 'Clarinet', 'Bass Clarinet', 'Bassoon', 'Contrabassoon', 'Trumpet', 'French Horn', 'Trombone', 'Bass Trombone', 'Tuba', 'Timpani', 'Percussion']

        
        column_names = ['Contrabass', 'Drums_Snare_Kick',
                        'Drums_hihat', 'Piano_1', 'Blank', 'Piano_2', 'Chords']
        
        starting_df = pd.read_csv(file, sep='\t', names=column_names)
        
        df_measure_grid = pd.read_csv(
                "kern_measure_grid_empty.krn", sep='\t', names=column_names)
        
        df_measure_grid_for_single_inst = pd.read_csv(
                    "kern_measure_grid_empty_for_sinlge_ins.krn", sep='\t', names=["a"])
        
        
        def keep_first_lines(long_string, num_lines):
            lines = long_string.split('\n')[:num_lines]
            short_string = '\n'.join(lines)
            return short_string
        
        
        def count_tabs(string):
            
            # Split the string into lines
            lines = string.split("\n")
            line_idx = 1
            tab_found = False
            while not tab_found and line_idx < len(lines):
                # Get the corresponding line before the end
                third_line = lines[len(lines)-line_idx]
                if "\t" in third_line or "  " in third_line:
                    tab_found = True
                    break
                else:
                    line_idx += 1
            if not tab_found:
                print('ERROR: no tab found while scanning kern')

            # Count the number of tab characters in the third line

            num_tabs = len(third_line.split("\t")) - 1
            if num_tabs == 0:
                num_tabs = len(third_line.split("  ")) - 1
            if num_tabs == 0:
                print("ERROR: num_tabs is still zero")
            return num_tabs
        
        
        def count_instruments(string_to_count_character):
            # Split the string into lines using the newline character '\n'
            lines = string_to_count_character.split('\n')
            
            # Loop over the lines until the first line containing '*I' is found
            for line in lines:
                if '*I' in line:
                    # Count the number of occurrences of '*I' in the line
                    
                    fields = line.split('\t')
                    new_list = [s.replace('\'', '').replace('"', '').replace('*I', '') for s in fields]
                    ins_list = [s for s in new_list if s.isalpha()]                    
                    break
                else:
                    ins_list = ['Piano']
            if len(ins_list) == 0:
                ins_list = ['Piano']

            return len(ins_list), ins_list
        
        inst_count, inst_list = count_instruments(data)
        num_columns = count_tabs(data) + 1

        if len(inst_list) < 3 and not len(inst_list) == 0 and num_columns == len(inst_list):
            column_names = inst_list
        elif len(inst_list) < 3 and not len(inst_list) == 0 and not num_columns == len(inst_list):
            column_names = [inst_list[0], "Blank"]
        elif len(inst_list) == 3:
            column_names = ['Contrabass', 'Drums_Snare_Kick',
                        'Drums_hihat', 'Piano_1', 'Blank', 'Piano_2', 'Chords']
        else:
            if num_columns < 2:
                string_to_be_searched_for_instrument = keep_first_lines(data, 10)
                for instrument in orchestra_instruments:
                    if instrument in string_to_be_searched_for_instrument:
                        instrument_name = instrument
                        break
                    else:
                        instrument_name = "Piano"
                column_names = ["Instrument", "Blank"]
                
            else:    
                column_names = ['Contrabass', 'Drums_Snare_Kick',
                            'Drums_hihat', 'Piano_1', 'Blank', 'Piano_2', 'Chords']
            
               
        # Find the first meter
        def word_search(key, d):
            
            lines = d.split('\n')  # reading the lines of the files in order
            
            for number, line in enumerate(lines, 1):
                if key in line:  # searching for the keyword in file
                    # returning the line number if the keyword
                    
                    start_line = number
                    break
            return start_line
        
        def keep_lines_until(data, keyword, column_names):
            lines = []
            for line in data.splitlines():
                lines.append(line)
                if keyword in line:
                    break
            first_lines = StringIO('\n'.join(lines))  
            df = pd.read_csv(first_lines, sep='\t', names=column_names)
            return df
        
        def get_dataframe(data, keyword, column_names):
            start_line = data.find(keyword) - 1
            last_line = data.count('\n')
            testline = data[start_line:]
            testline = StringIO(testline)
            df = pd.read_csv(testline, sep='\t', names=column_names)
        
            return df
        
        df_song_meta_kern = keep_lines_until(data, keyword="=1", column_names=column_names)       
        df = get_dataframe(data, keyword = "=1", column_names=column_names)
        
        # Split the DataFrame into a list of dataframes, where each dataframe contains the data for one measure
        
        df.fillna('')
        df_measure_start = df.loc[df.iloc[:, 0].str.contains('\=\d+|==', regex=True)]
        
        measures = []
        
        for i in range(len(df_measure_start.index)-1):
            
            measures.append(df.iloc[df_measure_start.iloc[i].name:df_measure_start.iloc[(i+1)].name])
  
        def get_global_tempo(starting_df):
            pattern_for_tempo = re.escape('*MM')
            first_occurrence_tempo = starting_df.iloc[:, 0].str.contains(pattern_for_tempo)
        
            global_tempo = str(120)
            for i in range(len(first_occurrence_tempo)):
                if first_occurrence_tempo.iloc[i] == True:
                    global_tempo = starting_df.iloc[i, 0].replace('*MM', "")
            if global_tempo == '.0':
                global_tempo = str(120)
                
            return global_tempo
        
        def get_global_style(starting_df):
            pattern_for_style = re.escape('*SS')
            first_occurrence_style = starting_df.iloc[:, 0].str.contains(pattern_for_style)
            global_style = 'Swing'
            for i in range(len(first_occurrence_style)):
                if first_occurrence_style.iloc[i] == True:
                    global_style = starting_df.iloc[i, 0].replace('*SS', "")
            return global_style
        
        def get_global_time_signature(df):
            pattern_for_time_signature = re.escape('*M')
            pattern_for_time_signature2 = re.escape('/')
            first_occurrence_time = df.iloc[:, 0].str.contains(pattern_for_time_signature) & df.iloc[:, 0].str.contains(pattern_for_time_signature2)
            global_time_signature = '4/4'
            for i in range(len(first_occurrence_time)):
                if first_occurrence_time.iloc[i]:
                    global_time_signature = df.iloc[i, 0].replace('*M', "")
                    global_time_signature = global_time_signature.split('/')
                    break
            return global_time_signature
        
        global_tempo = get_global_tempo(df_song_meta_kern)
        global_style = get_global_style(df_song_meta_kern)
        global_time_signature = get_global_time_signature(df_song_meta_kern)

        
        def split_df(df_input):
            # Filter out rows containing "r"
            
            df_input.fillna('.', inplace=True)
            mask = df_input.str.contains('!!|LO', case=False)
            
            df_input = df_input[~mask]

            df_input = df_input.fillna('')
            df_input = df_input.astype(str)

            # Split the data column into two dataframes
            # Extract numbers and characters
            
            df_numbers = df_input.str.extract('(\d+\.?\d*)', expand=False)
            df_rest = df_input.str.replace('(\d+\.?\d*)', '', regex=True)
            
            df_chars = df_rest.str.extract('([aAbBcCdDeEfFgG# \-]+)', expand=False, flags=re.IGNORECASE)
        
            df_numbers = df_numbers.fillna('')
            df_chars = df_chars.fillna('')

            
            return df_numbers, df_chars
        
        def find_row_starting_with_number(df):
            found = False
            for col in df.columns:
                for index, value in df[col].items():
                    if str(value)[0].isdigit() or str(value)[0] == '(':
                        #print(f"Row {index} in column '{col}' starts with a number.")
                        return index
                if found:
                    break
            return index
        
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
        
        def get_note_onsets(durations):
            grid = [0.0, 0.25, 0.333, 0.5, 0.666, 0.75, 1.0, 1.25, 1.333, 1.5, 1.666, 1.75, 2.0, 2.25, 2.333, 2.5, 2.666, 2.75, 3.0, 3.25, 3.333, 3.5, 3.666, 3.75]
            onsets = []
            current_onset = 0.0
           
            for duration in durations:
                # Check if the note duration fits within the remaining space of the current grid segment
                
                find_nearest(grid, duration)
                onsets.append(find_nearest(grid, current_onset))
                current_onset += duration
                
            return onsets
        
        def find_nearest(array, value):
           array = np.asarray(array)
           idx = (np.abs(array - value)).argmin()
           return array[idx]
        
        def sort_arrays(array, key):
            return sorted(array, key=lambda x: x[key])
        
        class MeasureforCSV:
        
            def __init__(self, measure, measure_count, df_measure_grid, df_measure_grid_for_single_inst):
                print(measure)
                if len(inst_list) == 0 or len(inst_list) == 2 or len(inst_list) > 4 or (measure.columns[0] == 'Piano' and len(inst_list) == 1):
                    return
                self.df_measure_grid = df_measure_grid
                self.df_measure_grid = self.df_measure_grid['Blank']
                
                self.df_measure_grid_for_single_inst = df_measure_grid_for_single_inst

                # TODO: If we create rythm & tempo change the following line should change
                
                self.measure = measure.reset_index(drop=True)
                #print(find_row_starting_with_number(self.measure),self.measure)
                self.measure = measure[find_row_starting_with_number(self.measure):]
                self.measure = self.measure.reset_index(drop=True)  
                num_blank_rows = 1
                self.measure_tempo = global_tempo         
                self.measure_style = global_style
        
        
        
                self.measure_start_line = ["Bar~" + str(measure_count) +
                                           "@" + str(measure_count * int(global_time_signature[0])), self.measure_style[0], str(global_time_signature[0]) + "/" +str(global_time_signature[1]), "A", self.measure_tempo]
            
                self.measure_player_grid = []
                self.measure_player_grid.append(self.measure_start_line)

                #Create CSV for single instrument
                 #%%
                
                if len(inst_list) == 1:
                    
                    #Check for polyphony
                    
                    for y in range(len(self.measure.columns)):
                        if self.measure.columns[y] == "Blank":
                             continue
                        
                        a,b = split_df(self.measure.iloc[:, y])                    
                        self.measure_note_duration_list = []
                        for i in range(len(a)):  
                            
                            self.measure_note_duration_list.append(note_duration_kern_to_csv_dictionary[a.iloc[i]])
                            
                        self.measure_note_duration_list = [float(x) for x in self.measure_note_duration_list]                        
                        self.note_onsets_list = get_note_onsets(self.measure_note_duration_list)
                        self.note_pitch_list = b.values.tolist()                        
                    
                        for i in range(len(a)):
                            note_duration_part = str(int(self.measure_note_duration_list[i]))                        
                            note_pitch = pitch_dictionary.get(self.note_pitch_list[i])
                            note_duration_part = self.measure_note_duration_list[i]
                            note_onset = self.note_onsets_list[i]
                            instrument = self.measure.columns[y]
                                                                                                          
                            if valid_note_for_player_CSV(instrument, note_pitch, note_duration_part, note_onset, random.randint(60, 80), measure_count):
                                            self.measure_player_grid.append(valid_note_for_player_CSV(instrument, note_pitch, note_duration_part, note_onset, random.randint(60, 80), measure_count))

                                        
                #%%                    
                else:
                    
                    #Create CSV for JGT instruments (Piano, Drums, Bass)
                    for i in range(len(self.measure)-num_blank_rows):
                        for y in range(len(self.measure.columns)):
                            #print(self.measure, self.measure.iloc[:, 0])
                            if y== 0 or y == 1 or y == 2 or y == 3 or y == 5:
                                
                                index = 0
                                for x in range(len(str(self.measure.iloc[i, y]))):
                                    if str(self.measure.iloc[i, y])[x].isalpha():
                                        index = x
                                        break
                                                                     
                                # Split the string based on the index of the letter
                                note_duration_part = str(self.measure.iloc[i, y])[:index]
                                note_pitch = str(self.measure.iloc[i, y])[index:]                               
                                note_duration_part = note_duration_kern_to_csv_dictionary.get(note_duration_part, float('nan'))
                                note_onset = self.df_measure_grid_for_single_inst.iloc[i, 0]                               
                                instrument = instrument_dictionary.get(str(y))                               
                                if instrument == "Piano": print(self.measure_start_line, str(self.measure.iloc[i, y])[:index], note_pitch)
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
                            
                            
                self.measure_player_grid[1:] = sorted(self.measure_player_grid[1:], key=lambda x: float(x[2]))                           
        data = []

        for i in range(len(measures)):
            
            data.append(MeasureforCSV(measures[i], i, df_measure_grid, df_measure_grid_for_single_inst).measure_player_grid)
               
        reduced_list = [item for sublist in data for item in sublist]
        
        kern2csv4playerString = ''
        
        for lst in data:
            kern2csv4playerStringByMeasure = '\n'.join([', '.join(map(str, inner_lst)) for inner_lst in lst])
            kern2csv4playerString += kern2csv4playerStringByMeasure + "\n"

        # make array
        arr = []
        for nl in kern2csv4playerString.split('\n'):
            l = []
            for c in nl.split(', '):
                l.append( c )
            arr.append(l)
        with open('debug_log.txt', 'w') as f:
            print('kern2csv4playerString: ', kern2csv4playerString, file=f)
        return kern2csv4playerString, arr

# =============================================================================
# #FOR ONLINE INTEGRATION COMMENT OUT THE FOLLOWING:
# file = "kern_files/a_blues_basic_guitar_voicings.krn"
# with open(file, 'r') as f:
#     data = f.read()
#     kern2csv4playerString, b = kern2csv4player_converter( StringIO(data), data)
#     print(b)
# =============================================================================