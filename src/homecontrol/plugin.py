import logging as log, json
from common import HCEncoder

class HCPlugin(object):
    
    server = None
    name = None
    template = None
    
    def __init__(self, server):
        self.server = server
        self.name = self.__module__
        
    def handle_get(self, handler, path):
        return False
    
    def log_warn(self, msg):
        log.warn("[%s]: %s" % (self.name, msg))
        
    def log_debug(self, msg):
        log.debug("[%s]: %s" % (self.name, msg))
        
    def log_info(self, msg):
        log.info("[%s]: %s" % (self.name, msg))
        
    def log_error(self, msg):
        log.error("[%s]: %s" % (self.name, msg))        
        
    def get_devices(self):
        return self.server.devices
    
    def send_json_response(self, handler, data, code=200):
        """ Creates and sends a JSON response.

        Creates JSON code from the given data and sends it using the 
        given http request handler.

        Args:
            handler: References the handler of the current http request.
            data: Data to be sent as JSON code.            
            code: Defines the response code is send within the http headers, 
                by default, responde code 200 (success) is sent.
        """
        handler.send_response(code)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps(data, cls=HCEncoder))