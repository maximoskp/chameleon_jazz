from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
import csv
import sys
from io import StringIO
import kern_converters as kcv
import reharmonization_functions as rhf
from urllib.parse import urlparse, quote

# FRONTEND_HOST = None

# if len(sys.argv) > 1:
#     FRONTEND_HOST = sys.argv[1]
# else:
#     sys.exit('WARNING: no acceptable FRONTEND_HOST is given as argument')

f = open('../data/json_files/chord_types_mapping_web.json')
types2fonts = json.load(f)
f.close()

api = Flask(__name__)
CORS(api)

cors = CORS(api, resources={r"/api/*": {"origins": "*"}})

@api.route('/sending_kern', methods=['GET','POST'])
def get_sending_kern():
    # example run: https://maxim.mus.auth.gr:6001/sending_kern?line=17&column=8&chord=Cm&kernfile=lalala
    # print('request:', request.args)
    print('kernfile:', request.args['kernfile'])
    kernfile = request.args['kernfile']
    # print('line:', request.args['line'])
    line = int(request.args['line'])
    # print('column:', request.args['column'])
    column = int(request.args['column'])
    # print('current:', request.args['current'])
    current = request.args['current']
    # print('root:', request.args['root'])
    # print('accidental:', request.args['accidental'])
    # print('variation:', request.args['variation'])
    print('reharmonize:', request.args['reharmonize'])
    reharmonize = request.args['reharmonize']
    print('reharmonize:', reharmonize)
    linesplit = kernfile.split('\n')
    columnsplit = linesplit[line-1].split('\t')
    # print('text position:', columnsplit[column-1])
    if reharmonize == 'true':
        # newchord = 'Dm'
        before_str = kcv.kern2string( StringIO(kernfile) )
        chord_idx = 1
        print('before_str:', before_str)
        mod_piece = rhf.substitute_chord_by_string( before_str, chord_idx )
        mod_string = mod_piece['string']
        print('mod_piece:', mod_piece)
        # get new chord from gjt string:
        chordsplit = mod_string.split('chord~')
        atplit = chordsplit[chord_idx+1].split('@')
        newchord = atplit[0]
        print('newchord - suggest:', 'x'+newchord+'x')
        # transform chord to kern fonts chord
        # check if flat / sharp
        if len(newchord) > 1:
            idx4space = 1
            if newchord[1] == 'b' or newchord[1] == '#':
                idx4space = 2
            if len(newchord) > idx4space:
                print('replacing for idx4space: ', idx4space)
                newchord = newchord.replace( newchord[idx4space:], ' ' + types2fonts[ newchord[idx4space] ] )
            else:
                print('no need to convert type - idx4space: ', idx4space)
        else:
            print('no need to convert type - len <= 1')
    else:
        newchord = request.args['root']
        if request.args['accidental'] != 'null':
            newchord += request.args['accidental']
        newchord += ' ' + request.args['variation']
        print('newchord - edit:', 'x'+newchord+'x')
    # newchord = 'C'
    print('newchord:', newchord)
    columnsplit[column-1] = newchord
    newline = '\t'.join(columnsplit)
    linesplit[line-1] = newline
    newkern = '\n'.join(linesplit)
    print('newkern:', newkern)
    new_gjt_string = kcv.kern2string( StringIO(newkern) )
    print('new_gjt_string:', new_gjt_string)
    # http://helen.mus.auth.gr:5000/get_csv_from_string?string=new_gjt_string
    response = requests.get("http://helen.mus.auth.gr:5000/get_csv_from_string?string=" + quote(new_gjt_string))
    song = response.json()
    print('csv: ', song['csv_string'])
    test_kern = kcv.csv2kern( StringIO( song['csv_string'] ) )
    print('test_kern:', test_kern)
    # print('newkern:', newkern)
    resp = {'new': test_kern, 'newchord': newchord}
    print('resp:', resp)
    # return json.dumps(resp)
    return jsonify(resp)
# end get_check_get

# TESTS ==================================
@api.route('/test_static_kern', methods=['GET','POST'])
def test_static_kern():
    # example run: http://155.207.188.7:6001/test_static_kern?filename=A_BEAUTIFUL_FRIENDSHIP.krn
    print(request.args)
    filepath = 'data/krn/' + request.args['filename']
    print('filepath: ' + filepath)
    f = open( filepath )
    data = f.read()
    f.close()
    resp = {'new': data}
    return json.dumps(resp)
# end get_check_get

@api.route('/test_static_kern2string', methods=['GET','POST'])
def test_static_kern2string():
    # example run: http://155.207.188.7:6001/test_static_kern2string?filename=A_BEAUTIFUL_FRIENDSHIP.krn
    print(request.args)
    filepath = 'data/krn/' + request.args['filename']
    s = kcv.kern2string( filepath )
    resp = {'string': s}
    return json.dumps(resp)
# end get_check_get

# TESTS ==================================

'''
# for tackling CORS etc
if FRONTEND_HOST is not None:
    @api.after_request
    def after_request(response):
        """!
        @brief Add necessary info to headers. Useful for preventing CORS permission errors.
        """
        response.headers.add("Access-Control-Allow-Origin", FRONTEND_HOST)
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response
    # end after_request

'''

# HOSTNAME_WHITELIST = [
#     # "http://localhost:3000",
#     # "https://test.com",
#     # "https://www.test.com",
#     "https://musicolab.hmu.gr/"
# ]
# # api = create_app()
# @api.after_request
# def after_request(response):
#     """!
#     @brief Add necessary info to headers. Useful for preventing CORS permission errors.
#     """
#     parsed_uri = urlparse(request.referrer)
#     url = "{uri.scheme}://{uri.netloc}".format(uri=parsed_uri)
#     if url in HOSTNAME_WHITELIST:
#         response.headers.add("Access-Control-Allow-Origin", url)
#         response.headers.add("Access-Control-Allow-Credentials", "true")
#         response.headers.add(
#             "Access-Control-Allow-Headers", "Content-Type,Authorization"
#         )
#         response.headers.add(
#             "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
#         )
#     return response

if __name__ == '__main__':
    # api.run()
    api.run(ssl_context=('/home/maximos/Documents/SSL_certificates/server.crt', '/home/maximos/Documents/SSL_certificates/server.key'), host='0.0.0.0', port=6001, debug=True)
    # api.run(ssl_context=('/etc/letsencrypt/live/maxim.mus.auth.gr/fullchain.pem', '/etc/letsencrypt/live/maxim.mus.auth.gr/privkey.pem'), host='0.0.0.0', port=6001, debug=True)
