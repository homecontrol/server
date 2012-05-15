from BaseHTTPServer import BaseHTTPRequestHandler

class HCHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        
        self.send_response(200)
        self.send_header("Content-type", 'text/html')
        self.end_headers()
        self.wfile.write("<h1>Hallo Welt!</h1>"); 