from datetime import datetime
import pathlib
import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from socketserver import ThreadingMixIn
import urllib.parse
import mimetypes
import socket
import json
from threading import Thread


# def socket_server(host, port):
#     with socket.socket() as s:
#         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         s.bind((host, port))
#         s.listen(1)
#         conn, addr = s.accept()
#         print(f"Connected by {addr}")
#         with conn:
#             while True:
#                 data = conn.recv(1024)
#                 print(f'From client: {data}')
#                 if not data:
#                     break
#                 conn.send(data.upper())

class HttpHandler(BaseHTTPRequestHandler):
    data = {}

    def __init__(self, request: bytes, client_address: tuple[str, int], server: socketserver.BaseServer):
        super().__init__(request, client_address, server)

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        print(data_dict)
        # Using timestamp as the key in the JSON data
        self.data[timestamp] = data_dict

        # Writing data to JSON file
        with open('storage/data.json', 'w') as json_file:
            json.dump(self.data, json_file, indent=2)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def _set_response(self):
        pass


# def run(server_class=HTTPServer, handler_class=HttpHandler):
#     server_address = ('', 3000)
#     http = server_class(server_address, handler_class)
#     try:
#         http.serve_forever()
#     except KeyboardInterrupt:
#         http.server_close()


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass


if __name__ == '__main__':
    httpd = ThreadingHTTPServer(('localhost', 3000), HttpHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
    # run()
