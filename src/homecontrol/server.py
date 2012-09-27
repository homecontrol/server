import os, sqlite3
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

class Server(ThreadingMixIn, HTTPServer):

    def __init__(self, server_address, request_handler):
        HTTPServer.__init__(self, server_address, request_handler)
        
        self.config = None
        self.devices = []
        self.plugins = {}
        self.document_root = None
        self.sql = None
    
    def sql_connect(self, path):
        
        if path[0] != "/": 
            path = "%s/%s" % (os.path.dirname(os.path.realpath(__file__)), path)
            
        self.sql = sqlite3.connect(path, check_same_thread = False)
        
    def set_config(self, config):
        self.config = config

    def add_device(self, device):
        self.devices.append(device)

    def add_devices(self, devices):
        self.devices.extend(devices)
        
    def add_plugin(self, name, plugin):
        self.plugins[name] = plugin(self)
        
    def set_document_root(self, document_root):
        self.document_root = document_root
        
    def stop(self):
        self.server_close()