from flask import Flask, request
import json
import os
import csv

api = Flask(__name__)

datapath = '/Users/max/repos/gjt_web/GJTWeb/executable/generated_csvs'

fileslist = os.listdir( datapath )

# print('fileslist: ', fileslist)

def getSongFromCSVFile( f ):
    print('datapath + os.sep + f: ', datapath + os.sep + f)
    r = []
    with open( datapath + os.sep + f , newline='\n', encoding='utf-16') as csvfile:
        songreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in songreader:
            # print( ','.join( row ) )
            print( row )
            r.append( row )
    return r
# end getSongFromCSVFile


@api.route('/songslist', methods=['GET'])
def get_songslist():
    # example run: http://localhost:5000/songslist
    return json.dumps(fileslist)
# end songslist

@api.route('/songcsv', methods=['GET'])
def get_songcsv():
    # example run: http://localhost:5000/songcsv?index=10
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

if __name__ == '__main__':
    api.run()