from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading

class HCServer(ThreadingMixIn, HTTPServer):

    config = None

    def set_config(self, config):
        self.config = config