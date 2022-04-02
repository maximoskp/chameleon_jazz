from flask import Flask, request
import json
import os
import csv
import sys

api = Flask(__name__)

# datapath = '/Users/max/repos/gjt_web/GJTWeb/executable/generated_csvs'

if len(sys.argv) > 1:
    datapath = sys.argv[1]
else:
    sys.exit('ERROR: no path to CSV files was given as as argument')

if len(sys.argv) > 1:
    datapath = sys.argv[1]
    print('datapath: ', datapath)

fileslist = os.listdir( datapath )

# print('fileslist: ', fileslist)

def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def getSongFromCSVFile( f ):
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


@api.route('/songslist', methods=['GET'])
def get_songslist():
    # example run: http://localhost:5000/songslist
    return json.dumps(fileslist)
# end songslist

@api.route('/songcsv', methods=['GET'])
def get_songcsv():
    # example run: http://localhost:5000/songcsv?index=10?
    # keywords should be:
    # 'index': NUMBER
    # 'name': NAME
    args = request.args
    argkeys = args.keys()
    resp = {}
    print('args: ', args)
    for k in argkeys:
        if k == 'index':
            n = int(args[k])
            if n < 0 or n > len(fileslist):
                print('ERROR: ' + str(n) + ' exceeds limits')
            else:
                resp[fileslist[n]] = getSongFromCSVFile( fileslist[ n ] )
        if k == 'name':
            n = args[k]
            print('n: ', n)
            if n not in fileslist:
                print('ERROR: ' + n + ' not in song names')
            else:
                resp[n] = getSongFromCSVFile( n )
        if k != 'index' and k != 'name':
            print('ERROR: arguments named \'index\' and \'name\' are only available')
    # print(resp)
    return json.dumps(resp)
# end get_songcsv

@api.route('/songcsvcomplex', methods=['GET'])
def get_songcsvcomplex():
    # example run: http://localhost:5000/songcsvcomplex?name="NAME_WITH_UNDERSCORES"&r=3&h=3
    # keywords should be:
    # 'index': NUMBER
    # 'name': NAME
    args = request.args
    argkeys = args.keys()
    resp = {}
    print('args: ', args)
    propername = ''
    for k in argkeys:
        if k == 'name':
            propername = args[k] + propername
        if k == 'r':
            if '_h~' in propername:
                tmp_split = propername.split('_h~')
                propername = '_h~'.join( [tmp_split[0] + '_r~' + args[k] , tmp_split[1]] )
            else:
                propername = propername + '_r~' + args[k]
        if k == 'h':
            propername = propername + '_h~' + args[k]
        if k != 'r' and k != 'name' and k != 'h':
            print('ERROR: arguments named \'index\' and \'name\' are only available')
    propername += '.csv'
    if propername not in fileslist:
        print('ERROR: ' + propername + ' not in song names')
    else:
        resp[propername] = getSongFromCSVFile( propername )
    # print(resp)
    return json.dumps(resp)
# end get_songcsv

if __name__ == '__main__':
    # api.run()
    api.run(host='0.0.0.0', port=5000, debug=True)