from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

class HCServer(ThreadingMixIn, HTTPServer):

    config = None
    devices = []

    def set_config(self, config):
        self.config = config

    def add_device(self, device):
        self.devices.append(device)

    def add_devices(self, devices):
        self.devices.extend(devices)
        
    def stop(self):
        self.server_close()