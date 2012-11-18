import logging as log, os, sys, json, urlparse, imp, inspect, types
from BaseHTTPServer import BaseHTTPRequestHandler
from macpath import realpath
from homecontrol.common import JSONEncoder

class Handler(BaseHTTPRequestHandler):
    
    def __init__(self, request, client_address, server):
        
        self.server = server
        self.plugin = None
        self.post_data = None
        self.response_sent = False
        
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        
    def get_server(self):
        return self.server
    
    def get_post_data(self):
        return self.post_data    
    
    def send_response(self, message=None, code=200):
        
        if self.response_sent == True:
            return
        
        self.response_sent = True
        return BaseHTTPRequestHandler.send_response(self, code, message)
    
    def send_json_response(self, data, code=200):
        """ Creates and sends a JSON response.

        Creates JSON code from the given data and sends it using the 
        given http request handler.

        Args:
            handler: References the handler of the current http request.
            data: Data to be sent as JSON code.            
            code: Defines the response code is send within the http headers, 
                by default, responde code 200 (success) is sent.
        """
        self.send_response(code=code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, cls=JSONEncoder))    
        
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
        """ Validates and returns request path.
        
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
            http://domain/path/path  /path/path  /path/path            

        Args:
            path: If defined, this path is used instead of the current request path.
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
            self.send_response("Permission denied for resource \"%s\"" % path, 403)
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

        if name not in self.server.plugins:
            return None
        
        return self.server.plugins[name]
    
    def do_POST(self):
        
        self.plugin = None
        
        len = int(self.headers.getheader('content-length'))
        self.post_data = self.rfile.read(len)

        self.handle_request(method = "POST", path = self.get_request_path(), args = self.get_request_args())
                    
    def do_GET(self):

        self.plugin = None
        content_type = self.get_content_type()
        
        if content_type != None:
            
            abs_path = self.get_abs_path()

            try:
                
                fd = open(abs_path, "rb")
                self.send_response(code=200) 
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(fd.read())
                fd.close()
                return
                
            except IOError, e:

                self.send_response("File \"%s\" not found." % abs_path, 404)
                return

        path = self.get_request_path()
        if path == "/": path = "/index/view" # Default page.
        self.handle_request(method="GET", path=path, args=self.get_request_args())
        
    @staticmethod
    def get_obj_id(path):
        """ Tries to extract an object ID from given request path.
        
        Args:
            path: Request path. The object ID is expected to be at the end of this path.
        Returns:
            The very last token of the path which is converted to an integer if numeric. 
        """ 
        id = path.split(os.sep)[-1]
        try: return int(id)
        except ValueError: return id
        
    @staticmethod
    def get_supported_args(method, args):

        supported = {}
        (args_, _, keywords, _) = inspect.getargspec(method)
        for name in args:
            if name in args_ or keywords != None:
                supported[name] = args[name]
        
        return supported        
    
    def invoke_method(self, path, plugin = None, obj_id = None, args = {}, opt_args = {}):
        
        token = path.split(os.sep)[1:]
        if len(token) < 2: return False
        
        method_name = token[1]
        module_name = token[0]
        class_name = module_name.title()
        
        if plugin != None:
            
            # Tolerate missing plugin methods since this could be an overloaded object!
            if not hasattr(plugin, method_name):
                return False
            
            method = getattr(plugin, method_name)
            
        else:
            
            (module_file, module_path, module_description) = imp.find_module(module_name, sys.path)
            module = imp.load_module(module_name, module_file, module_path, module_description)
    
            if not hasattr(module, class_name):
                raise NotImplementedError("Class \"%s\" not found in module \"%s\"." % (class_name, module_name))
        
            class_ = getattr(module, class_name)
    
            if not hasattr(class_, method_name):
                raise NotImplementedError("Method \"%s\" not found in class \"%s\"." % (method_name, class_name))
    
            method = getattr(class_, method_name)
            is_static = isinstance(method, types.FunctionType)
            
            if not is_static:
                
                if obj_id == None:
                    raise RuntimeError("Cannot run non-static method \"%s.%s\" without object id.", (class_name, method_name))

                # TODO: Kind of workaround to enforce device singleton.
                if class_name == "Device": obj = self.server.get_device(obj_id)
                else: obj = class_(obj_id, **self.get_supported_args(getattr(class_, "__init__"), opt_args))
                method = getattr(obj, method_name)

        args.update(self.get_supported_args(method, opt_args))
        
        retval = method(**args)
        retval_type = type(retval)
        
        # We expect HTML data from plugin methods.
        if plugin: self.send_response(retval)
        else: self.send_json_response(retval)
        return True  

    def handle_request(self, method = "GET", path = None, args = {}):
        """ Handle requests and invokes object methods.
                
        For proper object invocation, we assert that the following constraints:
        
            1. The module name is equal the filename with ".py" extension.
            2. The module name is equal to the class name except that the class name is camel cased.
            3. Calling an object's method requires an object initialization by using the last path token as first arguments,
               e.g. http://localhost:4000/<class>/<method>/<id> assumes that <class> can be instantiated when <id> is passed
               as first argument to the constructor.
            
        The return value of a invoked method will be json converted and send as http response (code 200).
        If the request cannot be handled, an 404 response code is sent.
        If the request raises an error, an 500 response code with an appropriate error message is sent.
        
        Note that calling a plugin's object method is tried first, see Plugin.handle_request() for details. If the plugin's
        object method cannot be called, the object's method is tried.
        
        Example:
        
            This is the basic invocation of a object method with <id>:
            
                http://localhost:4000/<class>/<method>/<id>
                
            The <id> is optional in order to invoke static methods:
            
                http://localhost:4000/<class>/<static_method>
                
            Methods arguments can be specified as follows:
            
                http://localhost:4000/<class>/<method>/<id>?<arg1>=<val1>&<param2>=<val2>
                
            This will define arguments "arg1" and "arg2" of the invoked methods.        
        
        Args:
            method: The request method which is either "GET" or "POST".
            path: The extracted request path, see self.get_request_path()
            args: Optional dict with arguments parsed from URL.
        """

        path = self.get_request_path(path)
        plugin = self.get_plugin(path)
        obj_id = self.get_obj_id(path)
        
        # Pass plugin to handler for logging
        self.plugin = plugin
        
        # TODO: Enable this to catch errors e.g. in plugins or user code!
        try:
       
            # Try handling request from plugin 
            if plugin != None and plugin.handle_request(self, method=method, path=path, args=args):
                return
    
            # Try handling request using object invocation.
            opt_args = {"handler": self, "sql": self.server.sql.cursor()}
            if self.invoke_method(path=path, obj_id=obj_id, args=args, opt_args=opt_args):
                return
            
        except Exception, e: 

            self.response_sent = False
            log.error("Exception when handling %s: %s" % (path, e))
            self.send_response(e, 500)
            return

        self.send_response("No handler found for \"%s\"." % path, 404)