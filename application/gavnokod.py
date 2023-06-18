from http.server import BaseHTTPRequestHandler, HTTPServer

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Hello, World!")

def run_server():
    host = '127.0.0.1'
    port = 8080
    server = HTTPServer((host, port), MyServer)
    print('Server running on {}:{}'.format(host, port))
    server.serve_forever()

run_server()
