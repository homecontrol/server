import logging as log, os
from BaseHTTPServer import BaseHTTPRequestHandler
from genshi.template.base import TemplateSyntaxError
from genshi.template.loader import TemplateNotFound
from macpath import realpath

class HCHandler(BaseHTTPRequestHandler):
    
    plugin = None
    
    def send_response(self, code, message=None):
        
        if code != 200:
            if self.plugin is not None:
                log.warn("[%s]: %s" % (self.plugin.name, message))
            else: log.warn(message)
            
        return BaseHTTPRequestHandler.send_response(self, code, message)
    
    def get_plugin_name(self):
        
        if self.path == None or self.path == "/":
            return "index" # Default plugin

        return self.path[1:].split("/")[0]
    
    def get_plugin_path(self):
        """ Returns relative plugin path.
        
        The plugin path is relativ to the appropriate plugin. 
        Example: For the path /index/foo/bar, the plugin is "index" and the 
        plugin path will be "/foo/bar".
        
        Returns:
            The appropriate plugin path.
        """
        
        token = self.path[1:].split("/")
        return "/" + "/".join(token[1:])
    
    def invoke_plugin_method(self):
        """ Invokes plugin method.
        
        Tries to determine an appropriate plugin method to invoke from the current
        request path.
        
        Example: 
            For the path /index/foo/bar, the plugin is "index", the method is 
            "foo" and "bar" is the first argument.
        
        Returns:
            False if the no method could be determined from the current request
            path or the given plugin does not have such a method. Returns true 
            if the method could be called successfully. 
        """
        
        if self.plugin == None:
            return False
        
        token = self.path[1:].split("/")
        if len(token) < 2: return False

        plugin_name = token[0]        
        method_name = token[1]
        args = token[2:]
        
        if not hasattr(self.plugin, method_name):
            return False

        method = getattr(self.plugin, method_name)
        if not callable(method):
            return False
        
        method(self, *args)
        return True
    
    def get_content_type(self):
        
        if self.path.endswith("png"): 
            return "image/png"
        
        if self.path.endswith("gif"): 
            return "image/gif"
        
        if self.path.endswith("css"): 
            return "text/css"
        
        if self.path.endswith("js"): 
            return "application/javascript"
        
        return None
    
    def get_abs_path(self):
        """ Returns absolute path.
        
        Prepends the document root to the the absolute path. Further it is 
        checked whether the real path is still within the document root for security 
        issues.
        
        Returns:
            None if the absolute path is outside the document root in this case
            a 403 permission denied error will be replied. Otherwise the absolute
            filesystem path will be returned.
        """        
        
        path = os.path.realpath(self.server.document_root + os.sep + 
                                "plugins" + os.sep + self.path)
        
        if path[:len(self.server.document_root)] != self.server.document_root:
            self.send_response(403, "Permission denied for resource \"%s\"" % path)
            return None
        
        return path
    
    def do_GET(self):
        
        content_type = self.get_content_type()
        abs_path = self.get_abs_path()
        
        if content_type != None:

            try:
                
                fd = open(abs_path, "rb")
                self.send_response(200) 
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(fd.read())
                fd.close()
                
            except IOError, e:

                self.send_response(404, "File \"%s\" not found." % abs_path) 
            
            return
        
        plugin_name = self.get_plugin_name()
        plugin_path = self.get_plugin_path()
        
        if plugin_name not in self.server.plugins:
            self.send_response(404, "Plugin \"%s\" not found." % plugin_name)
            return
            
        self.plugin = self.server.plugins[plugin_name]        

        try:
            
            if self.invoke_plugin_method() == True:
                return

            if self.plugin.handle_get(self, plugin_path) == True:
                return
            
            self.send_response(404, "No handler found for path \"%s\"" % plugin_path)
            
        except TemplateSyntaxError, e:
            self.plugin.log_error("Template error: %s" % e)
            
        except TemplateNotFound, e:
            self.plugin.log_error("Template error: %s" % e)