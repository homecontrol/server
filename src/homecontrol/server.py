import sqlite3, os
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

class HCServer(ThreadingMixIn, HTTPServer):

    config = None
    devices = []
    plugins = {}
    document_root = None
    sql = None
    
    def sql_connect(self, db_path):
        
        if db_path[0] != "/": 
            db_path = "%s/%s" % (os.path.dirname(os.path.realpath(__file__)), db_path)        
        
        self.sql = sqlite3.connect(db_path)

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