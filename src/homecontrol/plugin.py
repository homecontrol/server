import logging as log

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