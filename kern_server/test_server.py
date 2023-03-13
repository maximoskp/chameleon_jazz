from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl


httpd = HTTPServer(('127.0.0.1', 6001), BaseHTTPRequestHandler)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')


httpd.socket = ssl.wrap_socket (httpd.socket, 
        keyfile="/home/maximos/Documents/SSL_certificates/server.key", 
        certfile='/home/maximos/Documents/SSL_certificates/server.crt', server_side=True)

httpd.serve_forever()