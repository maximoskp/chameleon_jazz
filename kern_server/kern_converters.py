#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 15:29:05 2022

@author: kvelenis & max
"""

import pandas as pd
import re
import copy

# %% Function that converts kern to chart 
    
def kern2py(file_name):
    
    # load kern file & create pandas dataframe
    names=['a', 'b', 'c', 'd', 'e', 'f', 'g']
    df = pd.read_csv(file_name, sep='\t', names=names)
    
    # find where each measure starts based on "=" symbol
    df_measure_start = df.loc[df['a'].str.contains("=")]
    
    # find title
    titledf = df[df['a'].str.contains("!!!OTL: Jazz Standard Title")]
    title = titledf.iloc[0,0].replace('!!!OTL: ', '');
    
    #create chart variable
    chart = {}
    chart["bars"] = []
    
    measures = []
    measures_copy_last_column = [];
    
    # function that convert kern absolute note values to chart absolute note values 
    def note_duration(note):
        result = float;
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
          
        for y in range(len(measures_copy[i])):      
            
            for x in range(len(measures_copy[i].columns)):
                
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
        dfcumsum.append(measures_copy[i].iloc[1:,:].cumsum().min(axis=1));
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
    string = 'section~A'
    string += ',style~' + p['style']
    string += ',tempo~' + p['tempo']
    string += ',tonality~' + 'C' # TODO: tonality
    for b in p['bars']:
        string += ',bar~' + '4/4' # TODO: time sig
        for i in range(b.shape[0]):
            t = str( b.iloc[i][0] )
            c = b.iloc[i]['g'] # TODO: translate to GJT chord
            string += ',chord~' + c + '@' + t
    string += ',end'
    return string