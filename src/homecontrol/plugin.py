import logging as log, json, os
from homecontrol.handler import Handler
from homecontrol.common import JSONEncoder
from genshi.template.base import TemplateSyntaxError
from genshi.template.loader import TemplateNotFound

class Plugin(object):

    def __init__(self, server):
        self.server = server
        self.name = self.__module__
        self.template = None
        
    def sql(self):
        
        if self.server.sql == None:
            raise Exception("Server not connected to SQL database.")
        
        return self.server.sql.cursor()
    
    def sql_commit(self):
        
        if self.server.sql == None:
            raise Exception("Server not connected to SQL database.")        
        
        self.server.sql.commit()
        
    def handle_request(self, handler, method, path=None, args={}, data=None):
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
            
    def handle_request(self, handler, method = "GET", path = None, args = {}):
        """ Request handling for plugin methods.
        
         For proper plugin's object invocation, we assert that the following constraints:
        
            1. The plugin file is located in the "plugins" folder and its name is equal to the folder name expect the *.py extension.
            2. The plugin's name is equal to the class name except that the class name is camel cased.
        
        See Handler.handle_request() for more information.
        
        Example:
        
            This is the basic invocation of a plugin's object method with <id>:
            
                http://localhost:4000/<plugin_class>/<method>/<id>
                
            The <id> is optional in order to invoke static methods:
            
                http://localhost:4000/<plugin_class>/<static_method>
                
            Methods arguments can be specified as follows:
            
                http://localhost:4000/<plugin_class>/<method>/<id>?<arg1>=<val1>&<param2>=<val2>
                
            This will define arguments "arg1" and "arg2" of the invoked methods.
        
        Args:
            handler: Request handler handling this http request.
            method: The request method which is either "GET" or "POST".
            path: The extracted request path, see self.get_request_path()
            args: Optional dict with arguments parsed from URL.
        """
        
        token = path.split(os.sep)[1:]
        obj_id = None
        
        if len(token) == 3:
            obj_id = Handler.get_obj_id(path)
            token.pop();
        
        if len(token) != 2: 
            return False
        
        try:

            opt_args = opt_args = {"handler": handler, "sql": self.sql()}
            if handler.invoke_method(path="/%s" % "/".join(token), plugin=self, obj_id=obj_id, args=args, opt_args=opt_args):
                return True
        
        except TemplateSyntaxError, e:
            log.error("Template error: %s" % e)
            
        except TemplateNotFound, e:
            log.error("Template error: %s" % e)
            
        return False