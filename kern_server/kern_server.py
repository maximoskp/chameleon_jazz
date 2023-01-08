from flask import Flask, request
import json
import os
import csv
import sys
import kern_converters as kcv

FRONTEND_HOST = None

if len(sys.argv) > 1:
    datapath = sys.argv[1]
else:
    sys.exit('WARNING: no acceptable FRONTEND_HOST is given as arguement')


api = Flask(__name__)

@api.route('/sending_kern', methods=['GET','POST'])
def get_sending_kern():
    # example run: http://155.207.188.7:6001/sending_kern?row=17&column=8&chord=Cm&kern=lalala
    print(request.args)
    resp = {'new': 'kern'}
    return json.dumps(resp)
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
    api.run(host='0.0.0.0', port=6001, debug=True)
