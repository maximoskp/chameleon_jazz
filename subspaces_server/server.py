from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import pickle
import json
import os
import csv
import sys
if sys.version_info >= (3,8):
    import pickle
else:
    import pickle5 as pickle
sys.path.append('..' + os.sep +'0_data_preparation')
import CJ_ChartClasses as ccc
with open('../data/all_structs.pickle', 'rb') as handle:
    all_structs = pickle.load(handle)
with open('../data/stylesHMM.pickle', 'rb') as handle:
    stylesHMM = pickle.load(handle)


api = Flask(__name__)
CORS(api)

cors = CORS(api, resources={r"/api/*": {"origins": "*"}})

#datapath = '/Users/konstantinosvelenis/Documents/repos/visualization_server/chameleon_jazz-dev/visualisation_server/generated_csvs'

# fileslist = os.listdir( datapath )

def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

@api.route("/")
def index():
    return render_template("index.html")

# def getSongFromCSVFile( f ):
#     print('datapath + os.sep + f: ', datapath + os.sep + f)
#     resp = []
#     with open( datapath + os.sep + f , newline='\n', encoding='utf-16') as csvfile:
#         songreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
#         for row in songreader:
#             # print( ','.join( row ) )
#             # print( row )
#             row_elements = row[0].split(',')
#             tmp_arr = []
#             for r in row_elements:
#                 if r[0] == ' ' and len(r) > 1:
#                     r = r[1:]
#                 if r.isdigit():
#                     tmp_arr.append( int(r) )
#                 else:
#                     if is_number(r):
#                         tmp_arr.append( float(r) )
#                     else:
#                         tmp_arr.append( r )
#             resp.append( tmp_arr )

#     return resp
# # end getSongFromCSVFile

# def getTempoFromCSVFile( f ):
#     print('datapath + os.sep + f: ', datapath + os.sep + f)
#     resp = []
#     with open( datapath + os.sep + f , newline='\n', encoding='utf-16') as csvfile:
#         songreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
#         for row in songreader:
#             # print( ','.join( row ) )
#             # print( row )
#             row_elements = row[0].split(',')
#             tmp_arr = []
#             for r in row_elements:
#                 if r[0] == ' ' and len(r) > 1:
#                     r = r[1:]
#                 if r.isdigit():
#                     tmp_arr.append( int(r) )
#                 else:
#                     if is_number(r):
#                         tmp_arr.append( float(r) )
#                     else:
#                         tmp_arr.append( r )
#             resp.append( tmp_arr )
#         resp = resp[0]
#     return resp
print(all_structs[0])
@api.route('/all_structs', methods=['GET'])
def get_lstm_tsne_neutral_data():
    # example run: http://localhost:5000/lstm_tsne_3D_neutral
    all_structs = all_structs.tolist()
    
    return jsonify(all_structs)
# end lstm_tsne_3D_neutral

@api.route('/stylesHMM', methods=['GET'])
def get_lstm_tsne_tonalities_data():
    # example run: http://localhost:5000/lstm_tsne_3D_tonalities
    stylesHMM = stylesHMM.tolist()
    return jsonify(stylesHMM)
# end lstm_tsne_3D_tonalities

@api.route('/songslist', methods=['GET'])
def get_songslist():
    # example run: http://localhost:5000/songslist
    return jsonify(fileslist)
# end songslist

@api.route('/nameslist', methods=['GET'])
def get_nameslist():
    # example run: http://localhost:5000/nameslist
    #return render_template("", nameslist=nameslist)
    return jsonify(nameslist)
    #return json.dumps(nameslist)
# end nameslist

@api.route('/infostructure', methods=['GET'])
def get_infostructure():
    return jsonify(chart_info_structs)

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
    return jsonify(resp)
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
    return jsonify(resp)
# end get_songcsv

@api.route('/songtempo', methods=['GET'])
def get_songtempo():
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
        resp[propername] = getTempoFromCSVFile( propername )
    # print(resp)
    return jsonify(resp)
# end get_songcsv

# for visualisation

@api.route('/visualizenn', methods=['GET'])
def get_visualizenn():
    # example run: http://localhost:5000/visualizenn?name1="NAME_WITH_UNDERSCORES"&name2="NAME_WITH_UNDERSCORES"
    # keywords should be:
    # 'index': NUMBER
    # 'name': NAME
    args = request.args
    argkeys = args.keys()
    resp = {}
    print('args: ', args)
    name1 = None
    name2 = None
    for k in argkeys:
        if k == 'name1':
            name1 = args[k].replace('_', ' ')
        if k == 'name2':
            name2 = args[k].replace('_', ' ')
    if name1 is not None and name2 is not None:
        hh, c, z = ssm.nn_shaping( name1, name2  )
        resp = {
            'hh': hh.tolist(),
            'c': c.tolist(),
            'z': z.tolist(),
            'info':{
                'hh': 'x and y coordinates',
                'c': 'R and B color values - G is a zero column',
                'z': 'z coordinate'
            }
        }
    print('resp: ', resp)
    return jsonify(resp)
# end get_visualizenn

@api.route('/visualizedistr', methods=['GET'])
def get_visualizedistr():
    # example run: http://localhost:5000/visualizedistr?name1="NAME_WITH_UNDERSCORES"&name2="NAME_WITH_UNDERSCORES"
    # keywords should be:
    # 'index': NUMBER
    # 'name': NAME
    args = request.args
    argkeys = args.keys()
    resp = {}
    print('args: ', args)
    name1 = None
    name2 = None
    for k in argkeys:
        if k == 'name1':
            name1 = args[k].replace('_', ' ')
        if k == 'name2':
            name2 = args[k].replace('_', ' ')
    if name1 is not None and name2 is not None:
        hh, c, z = ssm.distr_shaping( name1, name2  )
        resp = {
            'hh': hh.tolist(),
            'c': c.tolist(),
            'z': z.tolist(),
            'info':{
                'hh': 'x and y coordinates',
                'c': 'R and B color values - G is a zero column',
                'z': 'z coordinate'
            }
        }
    # print(resp)
    return jsonify(resp)
# end get_visualizedistr

@api.route('/visualizetrans', methods=['GET'])
def get_visualizetrans():
    # example run: http://localhost:5000/visualizetrans?name1="NAME_WITH_UNDERSCORES"&name2="NAME_WITH_UNDERSCORES"
    # keywords should be:
    # 'index': NUMBER
    # 'name': NAME
    args = request.args
    argkeys = args.keys()
    resp = {}
    print('args: ', args)
    name1 = None
    name2 = None
    for k in argkeys:
        if k == 'name1':
            name1 = args[k].replace('_', ' ')
        if k == 'name2':
            name2 = args[k].replace('_', ' ')
    if name1 is not None and name2 is not None:
        hh, c, z = ssm.trans_shaping( name1, name2  )
        resp = {
            'hh': hh.tolist(),
            'c': c.tolist(),
            'z': z.tolist(),
            'info':{
                'hh': 'x and y coordinates',
                'c': 'R and B color values - G is a zero column',
                'z': 'z coordinate'
            }
        }
    # print(resp)
    return jsonify(resp)
# end get_visualizetrans

@api.route('/clusters_lstm_3D_tonalities', methods=['GET'])
def get_clusters_lstm_3D_tonalities():
    clusters_lstm_3D_tonalities = clusters_lstm_3D_tonalities_raw;
    return jsonify(clusters_lstm_3D_tonalities);

@api.route('/clusters_lstm_3D_neutral', methods=['GET'])
def get_clusters_lstm_3D_neutral():
    clusters_lstm_3D_neutral = clusters_lstm_3D_neutral_raw;
    return jsonify(clusters_lstm_3D_neutral);

# # for tackling CORS etc
#FRONTEND_HOST = "http://155.207.188.7:1234"
#@api.after_request
#def after_request(response):
#    """!
#    @brief Add necessary info to headers. Useful for preventing CORS permission errors.
#    """
#    response.headers.add("Access-Control-Allow-Origin", FRONTEND_HOST)
#    response.headers.add("Access-Control-Allow-Credentials", "true")
#    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
#    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
#    return response
 # end after_request

'''
HOSTNAME_WHITELIST = [
    "http://localhost:3000",
    "https://test.com",
    "https://www.test.com",
]
app = create_app()
@app.after_request
def after_request(response):
    """!
    @brief Add necessary info to headers. Useful for preventing CORS permission errors.
    """
    parsed_uri = urlparse(request.referrer)
    url = "{uri.scheme}://{uri.netloc}".format(uri=parsed_uri)
    if url in HOSTNAME_WHITELIST:
        response.headers.add("Access-Control-Allow-Origin", url)
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
    return response
'''

if __name__ == '__main__':
    # api.run()
    # api.run(host='0.0.0.0', port=5000, debug=True)
    api.run(ssl_context=('/home/maximos/Documents/SSL_certificates/server.crt', '/home/maximos/Documents/SSL_certificates/server.key'), host='0.0.0.0', port=5000, debug=True)
