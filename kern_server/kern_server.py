from flask import Flask, request
import json
import os
import csv
import sys

api = Flask(__name__)

@api.route('/sending_kern', methods=['GET'])
def get_sending_kern():
    # example run: http://localhost:6000/get_sending_kern?JSON_INFO
    print(request.args)
    resp = {'new': 'kern'}
    return json.dumps(resp)
# end get_check_get

# # for tackling CORS etc
# FRONTEND_HOST = "http://155.207.188.7:1234"
# @api.after_request
# def after_request(response):
#     """!
#     @brief Add necessary info to headers. Useful for preventing CORS permission errors.
#     """
#     response.headers.add("Access-Control-Allow-Origin", FRONTEND_HOST)
#     response.headers.add("Access-Control-Allow-Credentials", "true")
#     response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
#     response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
#     return response
# # end after_request

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