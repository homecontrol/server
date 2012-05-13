import os, sys, select, argparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

__version__ = "0.1"

class Server(BaseHTTPRequestHandler):
    
    def do_GET(self):
        
        self.send_response(200)
        self.send_header("Content-type", 'text/html')
        self.end_headers()
        self.wfile.write("<h1>Hallo Welt!</h1>");
        
    def serve_forever(self, poll_interval=0.5):

        self.__is_shut_down.clear()
        try:
            while not self.__shutdown_request:

                r, w, e = select.select([self], [], [], poll_interval)
                if self in r:
                    self._handle_request_noblock()
        finally:
            self.__shutdown_request = False
            self.__is_shut_down.set()        
        
def main(argv):
    
    parser = argparse.ArgumentParser(description="HomeControl Server V%s" % __version__)
    parser.add_argument("-p", "--port", type=int, 
                        help="TCP/IP port to bind server or to connect to via "
                             "command line, default is 4000");

    args = parser.parse_args()

    print args
    sys.exit(0)

    port = int(options.port)
    server = HTTPServer(('', port), Server)
    server.serve_forever()
    sys.exit(0)
    
if __name__ == "__main__":
    main(sys.argv)