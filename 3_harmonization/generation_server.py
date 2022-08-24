from flask import Flask, request
import json
import numpy as np
import os
import json
import pickle
import sys
sys.path.append('..' + os.sep +'0_data_preparation')
import CJ_ChartClasses as ccc
import copy
from pathlib import Path
import subprocess
import csv
import reharmonization_functions as rhf

# %% load pickle

with open('../data/all_melody_structs.pickle', 'rb') as handle:
    all_structs = pickle.load(handle)

with open('../data/globalHMM.pickle', 'rb') as handle:
    globalHMM = pickle.load(handle)

# load ts_groupings
f = open('../data/json_files/time_signature_groupings.json')
ts_groupings = json.load(f)
f.close()

keys = [s.key for s in all_structs]

api = Flask(__name__)

datapath = 'generated_csvs'
os.makedirs(datapath, exist_ok=True)
gjt_app_path = '../../gjt_web/GJTWeb/executable/'

def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
# end is_number

def getSongFromCSVFile( f ):
    print('datapath: ' + datapath)
    print('f: ' + f)
    print('datapath + os.sep + f: ', datapath + os.sep + f)
    resp = []
    with open( datapath + os.sep + f , newline='\n', encoding='utf-16') as csvfile:
        songreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in songreader:
            # print( ','.join( row ) )
            # print( row )
            row_elements = row[0].split(',')
            tmp_arr = []
            for r in row_elements:
                if r[0] == ' ' and len(r) > 1:
                    r = r[1:]
                if r.isdigit():
                    tmp_arr.append( int(r) )
                else:
                    if is_number(r):
                        tmp_arr.append( float(r) )
                    else:
                        tmp_arr.append( r )
            resp.append( tmp_arr )
    return resp
# end getSongFromCSVFile

def generateFromString(song_string, rhythm_complexity=3, harmonic_complexity=3, song_name='BL test'):
    print('song_string: ' + song_string)
    # keep tempo
    tempo_split = song_string.split('tempo~')
    comma_split = tempo_split[1].split(',')
    tempo = comma_split[0]

    # keep time signature and grouping
    bar_split = song_string.split('bar~')
    comma_split = bar_split[1].split(',')
    ts = comma_split[0]
    # ts = "7/4"
    ts_grouping = ts_groupings[ts][0] + '-4'

    # keep original style
    style_split = song_string.split('style~')
    comma_split = style_split[1].split(',')
    style = comma_split[0]

    # select number of choruses
    chorusesNumber = str(4)

    # select if it starts with head
    startsWithHead = str(0)
    subprocess.call([ gjt_app_path+'GJTWeb', song_string.encode('unicode-escape').decode('utf-8'), rhythm_complexity, harmonic_complexity, chorusesNumber, startsWithHead, tempo, style, ts, ts_grouping, '>>', 'log.txt'])
    home = str(Path.home())
    # new_song_name = song_name.replace(' ', '_')
    # csv_name = 'generated_csvs' + os.sep + new_song_name + '_r~' + str(rhythm_complexity) + '_h~' + str(harmonic_complexity) + '.csv'
    csv_name = 'generated_csvs' + os.sep + song_name
    os.rename(home + os.sep + 'Documents' + os.sep + 'lala.csv', csv_name )
# end generateFromString

@api.route('/songslist', methods=['GET'])
def get_songslist():
    # example run: http://localhost:5000/songslist
    return json.dumps(keys)

@api.route('/songstring', methods=['GET'])
def get_songstring():
    # example run: http://localhost:5000/songstring?index=10
    # keywords should be:
    # 'index': NUMBER
    # 'name': NAME
    args = request.args
    argkeys = args.keys()
    resp = {}
    for k in argkeys:
        if k == 'index':
            n = int(args[k])
            if n < 0 or n > len(keys):
                print('ERROR: ' + str(n) + ' exceeds limits')
            else:
                resp[keys[n]] = all_structs[ n ].string
        if k == 'name':
            n = args[k]
            if n not in keys:
                print('ERROR: ' + n + ' not in song names')
            else:
                resp[n] = all_structs[keys.index(n)].string
        if k != 'index' and k != 'name':
            print('ERROR: arguments named \'index\' and \'name\' are only available')
    print(resp)
    return json.dumps(resp)
# end get_songstring

@api.route('/song', methods=['GET'])
def get_song():
    # example run: http://localhost:5000/song?index=1
    # keywords should be:
    # 'index': NUMBER
    # 'name': NAME
    args = request.args
    argkeys = args.keys()
    resp = {}
    for k in argkeys:
        if k == 'index':
            n = int(args[k])
            if n < 0 or n > len(keys):
                print('ERROR: ' + str(n) + ' exceeds limits')
            else:
                resp[keys[n]] = all_structs[ n ].string
        if k == 'name':
            n = args[k]
            if n not in keys:
                print('ERROR: ' + n + ' not in song names')
            else:
                resp[n] = all_structs[keys.index(n)].string
        if k != 'index' and k != 'name':
            print('ERROR: arguments named \'index\' and \'name\' are only available')
    print(resp)
    return json.dumps(resp)
# end get_song

@api.route('/generatecsv', methods=['GET'])
def get_songcsvcomplex():
    # example run: http://localhost:5000/generatecsv?name="NAME_WITH_UNDERSCORES"&r=3&h=3
    # no double quotes
    # http://127.0.0.1:5000/generatecsv?name=ALL_OF_ME&r=3&h=3
    # keywords should be:
    # 'index': NUMBER
    # 'name': NAME
    args = request.args
    argkeys = args.keys()
    resp = {}
    print('args: ', args)
    propername = ''
    rhythm_complexity = str(3)
    harmonic_complexity = str(3)
    songkey = ''
    for k in argkeys:
        if k == 'name':
            propername = args[k] + propername
            songkey = args[k].replace('_', ' ')
        if k == 'r':
            if '_h~' in propername:
                tmp_split = propername.split('_h~')
                rhythm_complexity = str(args[k])
                propername = '_h~'.join( [tmp_split[0] + '_r~' + args[k] , tmp_split[1]] )
            else:
                propername = propername + '_r~' + args[k]
        if k == 'h':
            harmonic_complexity = str(args[k])
            propername = propername + '_h~' + args[k]
        if k != 'r' and k != 'name' and k != 'h':
            print('ERROR: arguments named \'index\' and \'name\' are only available')
    propername += '.csv'
    print('propername: ', propername)
    print('songkey: -' + songkey + '-' )
    print('keys: ', keys)
    if songkey not in keys:
        print('ERROR: ' + songkey + ' not in song names')
    else:
        generateFromString(all_structs[keys.index(songkey)].string, harmonic_complexity=harmonic_complexity, rhythm_complexity=rhythm_complexity, song_name=propername)
        resp[songkey] = getSongFromCSVFile( propername )
    # print(resp)
    return json.dumps(resp)
# end get_songcsv

if __name__ == '__main__':
    api.run() 