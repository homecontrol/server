from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

class HCServer(ThreadingMixIn, HTTPServer):

    config = None
    devices = []
    plugins = {}
    document_root = None

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