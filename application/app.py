import pathlib
import urllib.parse
import mimetypes
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = pathlib.Path()

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

        body = self.rfile.read(int(self.headers['Content-Length']))
        body = urllib.parse.unquote_plus(body.decode())
        payload = {key: value for key, value in [el.split('=') for el in body.split('&')]}
        with open(BASE_DIR.joinpath('storage/data.json'), 'w', encoding='utf-8') as fd:
            json.dump(payload, fd, ensure_ascii=False)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

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


if __name__ == '__main__':
    run()
