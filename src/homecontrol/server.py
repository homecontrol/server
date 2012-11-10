import os, sqlite3, imp, logging as log
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn
from apscheduler.scheduler import Scheduler

class Server(ThreadingMixIn, HTTPServer):

    def __init__(self, server_address, request_handler):
        HTTPServer.__init__(self, server_address, request_handler)
        
        self.config = None
        self.devices = []
        self.plugins = {}
        self.document_root = None
        self.sql = None
        
        self.scheduler = Scheduler()
        self.scheduler.start() 
    
    def sql_connect(self, path):
        
        if path[0] != "/": 
            path = "%s/%s" % (os.path.dirname(os.path.realpath(__file__)), path)
            
        self.sql = sqlite3.connect(path, check_same_thread = False)
        
        # Enable foreign key support
        self.sql.cursor().execute("PRAGMA foreign_keys = ON;")
        
    def set_config(self, config):
        self.config = config

    def add_device(self, device):
        self.devices.append(device)

    def add_devices(self, devices):
        self.devices.extend(devices)
        
    def load_plugins(self, plugin_dir):
        
        if not os.path.isdir(plugin_dir):
            raise Exception("Plugin directory \"%s\" does not exist!" % plugin_dir)
        
        plugins = os.listdir(plugin_dir)
        plugins.sort()
        for plugin_name in plugins:
            
            if not os.path.isdir(plugin_dir + os.sep + plugin_name): 
                continue
            
            self.load_plugin(plugin_name, plugin_dir + os.sep + plugin_name)
        
        
    def load_plugin(self, plugin_name, plugin_dir):
        
        try:
            plugin_class = plugin_name.title()
            plugin_path = plugin_dir + os.sep + plugin_name + ".py"
            plugin_module = imp.load_source(plugin_name, plugin_path)
            # TODO: Use compiled modules.
            #module = imp.load_compiled(module_name, module_bin)
                
            if not hasattr(plugin_module, plugin_class):
                raise NotImplementedError("Plugin class \"%s\" missing in \"%s\"" % (plugin_class, plugin_path))
                
            log.debug("Load plugin \"%s\", directory \"%s\"" %  (plugin_name, plugin_dir))
            self.plugins[plugin_name] = getattr(plugin_module, plugin_class)(self)

        except Exception, e:                
                log.error("Could not load plugin \"%s\", error: %s" % (plugin_name, str(e)))
        
    def set_document_root(self, document_root):
        self.document_root = document_root
        
    def stop(self):
        
        self.scheduler.shutdown(wait=False)
        self.server_close()