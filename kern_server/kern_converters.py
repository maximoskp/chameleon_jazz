#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 15:58:11 2021

@author: max
"""

import pandas as pd
import re
import copy

# %% load kern file & create pandas dataframe
    
def kern2py(file_name):
    names=['a', 'b', 'c', 'd', 'e', 'f', 'g']
    df = pd.read_csv(file_name, sep='\t', names=names)
    
    df_measure_start = df.loc[df['a'].str.contains("=")]
    
    titledf = df[df['a'].str.contains("!!!OTL: Jazz Standard Title")]
    title = titledf.iloc[0,0].replace('!!!OTL: ', '');
    
    chart = {}
    chart["bars"] = []
    
    measures = []
    measures_copy_last_column = [];
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
            
    
    for i in range(len(df_measure_start.index)-1):
        measures.append(df.iloc[df_measure_start.iloc[i].name:df_measure_start.iloc[(i+1)].name])
        measures_copy_last_column.append(df.iloc[df_measure_start.iloc[i].name:df_measure_start.iloc[(i+1)].name, -1])
        measures_copy_last_column[i] = measures_copy_last_column[i].iloc[1:]
    
    measures_copy = []
    measures_copy = copy.deepcopy(measures)
    for i in range(len(measures_copy)):  
        measures_copy[i] = measures_copy[i].iloc[: , :-1]
    
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
                    
    dfcumsum = []
    measures_chart_ready = []
    for i in range(len(measures_copy)):  
        dfcumsum.append(measures_copy[i].iloc[1:,:].cumsum().min(axis=1));
        dfcumsum[i] = dfcumsum[i].iloc[:].shift(1)
        measures_chart_ready.append(pd.concat([dfcumsum[i], measures_copy_last_column[i]], axis=1).reindex(dfcumsum[i].index))
        chart["bars"].append(measures_chart_ready[i])
     
                    
    chart["title"] = title
    chart["style"] = style
    chart["tempo"] = tempo
# end kern2py


