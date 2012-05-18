from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading

class HCServer(ThreadingMixIn, HTTPServer):

    config = None
    devices = []

    def set_config(self, config):
        self.config = config

    def add_device(self, device):
        self.devices.append(device)

    def add_devices(self, devices):
        self.devices.extend(devices)