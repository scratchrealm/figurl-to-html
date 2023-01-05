import os
from http.server import HTTPServer, SimpleHTTPRequestHandler


def view_doc(*, file_path: str, port: int, allow_origin: str):
    class CORSRequestHandler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', allow_origin)
            self.send_header('Access-Control-Allow-Methods', 'GET')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            return super(CORSRequestHandler, self).end_headers()

    abs_file_path = os.path.abspath(file_path)
    parent_path = os.path.dirname(abs_file_path)
    fname = os.path.basename(abs_file_path)

    os.chdir(parent_path)
    httpd = HTTPServer(('localhost', port), CORSRequestHandler)
    print(f'https://doc.figurl.org?doc=http://localhost:{port}/{fname}')
    httpd.serve_forever()