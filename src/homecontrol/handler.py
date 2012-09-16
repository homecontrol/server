import logging as log, os, json, urlparse
from BaseHTTPServer import BaseHTTPRequestHandler
from genshi.template.base import TemplateSyntaxError
from genshi.template.loader import TemplateNotFound
from macpath import realpath

class Handler(BaseHTTPRequestHandler):
    
    plugin = None
    
    def send_response(self, code, message=None):
        
        if code != 200:
            if self.plugin is not None:
                log.warn("[%s]: %s" % (self.plugin.name, message))
            else: log.warn(message)
            
        return BaseHTTPRequestHandler.send_response(self, code, message)
        
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

    def get_request_path(self, path = None):
        """ Validates and returns given request path.
        Example: The default handler path (self.path) and the return value for the 
        appropriate requests are as follows:

            Request                  self.path   self.get_request_path
            http://domain/           /           /
            http://domain            /           /
            http://domain/?var       /?var       /
            http://domain/path       /path       /path
            http://domain/path/      /path/      /path
            http://domain/path?var   /path?var   /path
            http://domain/path/?var  /path/?var  /path            

        Args:
            path: If defined, this path is used instead of the current request path.      
            default: Defines default path that is used in case of an empty request path.
            By default, this is "/".
        Returns:
            Given request path with leading slash and without ending slash.
        """
        if path == None:
            path = self.path

        if "?" in path:
            path = path.split("?")[0]

        if len(path) > 1 and path[-1] == "/":
            path = path[:-1]

        return path

    def get_request_args(self, path = None):
        """ Extracts and validates arguments from given request path.
        Args:
            path: If defined, this path is used instead of the current request path.
        Returns:
            Dictionary with arguments determined from current request path.
            Example: http://localhost:4000/plugin/method?name=val&name2=val2 would
            return a dictionary {"name": "val", "name2": "val2"}. Returns an empty
            dictionary if no arguments was specified.
        """
        if path == None:
            path = self.path
        
        if "?" not in path:
            return {}
        
        query = path.split("?")[1]
        return dict(urlparse.parse_qsl(query))
    
    def get_abs_path(self, path = None):
        """ Returns absolute path.
        Prepends the document root to the the absolute path. Further it is 
        checked whether the real path is still within the document root for security 
        issues.
        Args:
            path: If defined, this path is used instead of the current request path.
        Returns:
            None if the absolute path is outside the document root in this case
            a 403 permission denied error will be replied. Otherwise the absolute
            filesystem path will be returned.
        """
        path = os.path.realpath(self.server.document_root + os.sep + 
            "plugins" + os.sep + self.get_request_path(path).replace("/", os.sep))
        
        if path[:len(self.server.document_root)] != self.server.document_root:
            self.send_response(403, "Permission denied for resource \"%s\"" % path)
            return None
        
        return path
    
    def get_plugin(self, path = None):
        """ Returns plugin determined from given request path.
        The plugin name isdetermined by the first directory of the specified path.
        Args:
            path: If defined, this path is used instead of the current request path.
        Returns:
            The appropriate plugin instance on success, otherwise None.
        """
        path = self.get_request_path(path)
        name = path.split("/")[1]

        # Default plugin is the index plugin.
        if len(name) == 0:
            name = "index"
            
        if name not in self.server.plugins:
            return None
        
        return self.server.plugins[name]
            
    def get_plugin_method(self, path = None):
        """ Gets plugin method from given path.
        For example, the plugin for the request path "/index/foo?name=data" is "index"
        and the method is "foo".
        Args:
             path: If defined, this path is used instead of the current request path.
        Returns:
            Returns the callable plugin method on success or None if the given
            plugin does not provide such a method or the method is not callable.
        """
        path = self.get_request_path(path)
        if path == "/": return None

        token = path.split("/")
        if len(token) < 3:
            return None

        name = token[2]
        plugin = self.get_plugin()
        if not hasattr(plugin, name):
            return None

        method = getattr(plugin, name)
        
        if not callable(method):
            return None
        
        return method
    
    def do_POST(self):
        
        len = int(self.headers.getheader('content-length'))
        data = self.rfile.read(len)

        self.handle_request(
            method = "POST", 
            path = self.get_request_path(), 
            args = self.get_request_args(), 
            data = data)
                    
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
                return
                
            except IOError, e:

                self.send_response(404, "File \"%s\" not found." % abs_path)
                return

        self.handle_request(
            method = "POST", 
            path = self.get_request_path(), 
            args = self.get_request_args(),
            data = None)

    def handle_request(self, method = "GET", path = None, args = {}, data = None):

        try:

            path = self.get_request_path(path)            
            plugin = self.get_plugin()

            if plugin == None:
                self.send_response(404, "No plugin found for path \"%s\"" % path)
                return
            
            method = self.get_plugin_method()            
            if method != None:
                
                if data != None: return method(self, data, **args)
                return method(self, **args)
            
            # Make path relative to the plugin.
            if path != None:
                path = "/" + "/".join(path.split("/")[2:])

            if plugin.handle_request(self, method=method, path=path, args=args, data=data):
                return
            
            self.send_response(404, "No handler found for path \"%s\" in plugin \"%s\"" % (path, plugin.name))
            
        except TemplateSyntaxError, e:
            log.error("Template error: %s" % e)
            
        except TemplateNotFound, e:
            log.error("Template error: %s" % e)