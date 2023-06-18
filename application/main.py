import pathlib
import urllib.parse
from urllib.parse import parse_qs
import mimetypes
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import socket
from datetime import datetime

BASE_DIR = pathlib.Path()
STORAGE_DIR = BASE_DIR / 'storage'

data_file = STORAGE_DIR / 'data.json'
if not data_file.exists():
    # Створюємо новий файл зі списком
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump([], f)

data_list = []

html = """"
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Document</title>
</head>
<body>
<h1>Hello World</h1>
<div class="test">Test</div>
</body>
</html>

"""


class HTTPHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = parse_qs(post_data)
        entry = {}
        for key, value in parsed_data.items():
            entry[key] = value[0]

        data_list.append(entry)  # Исправленная строка

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes('Data received and stored successfully!', 'utf-8'))

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case '/':
                self.send_html('index.html')
            case '/contact':
                self.send_html('message.html')
            case '/blog':
                self.send_html('blog.html')
            case _:

                file = BASE_DIR / route.path[1:]
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html('404.html', 404)

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as f:
            self.wfile.write(f.read())
        # self.wfile.write(f.read())

    def send_static(self, filename, status_code=200):
        self.send_response(status_code)
        mime_type, *rest = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header('Content-Type', mime_type)
        else:
            self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as f:
            self.wfile.write(f.read())
        # self.wfile.write(f.read())


def run(server=HTTPServer, handler=HTTPHandler):
    address = ('', 3000)
    http_server = server(address, handler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


class SocketServer(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        UDP_IP = 'localhost'
        UDP_PORT = 5000

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind((UDP_IP, UDP_PORT))
            print('Socket server started on {}:{}'.format(UDP_IP, UDP_PORT))
            while True:
                data, addr = server_socket.recvfrom(1024)
                try:
                    payload = json.loads(data)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    with open(STORAGE_DIR.joinpath('data.json'), 'a', encoding='utf-8') as fd:
                        fd.write(json.dumps({timestamp: payload}) + '\n')
                except json.JSONDecodeError:
                    print('Invalid JSON data received')


def run(server=HTTPServer, handler=HTTPHandler):
    http_address = ('', 3000)
    http_server = server(http_address, handler)

    socket_server = SocketServer()
    socket_server.start()

    try:
        http_server.serve_forever()    except KeyboardInterrupt:
        http_server.server_close()
        socket_server.join()


if __name__ == '__main__':
    run()
