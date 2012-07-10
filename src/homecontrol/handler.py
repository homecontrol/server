import logging as log, os
from BaseHTTPServer import BaseHTTPRequestHandler
from genshi.template.base import TemplateSyntaxError
from macpath import realpath

class HCHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        
        token = None
        plugin_name = None
        
        if token != "/":
            token = self.path.split("/")

        if token == None or len(token[0]) == 0:
            plugin_name = "index" # Default plugin.
        else: plugin_name = token[0]
        
        type = None;
        if self.path.endswith("png"): type = "image/png"
        elif self.path.endswith("gif"): type = "image/gif"
        elif self.path.endswith("css"): type = "text/css"
        elif self.path.endswith("js"): type = "text/js"

        if type != None:
            
            src_path = self.server.document_root + os.sep + "plugins" + os.sep + plugin_name + os.sep + self.path

            if not os.path.exists(src_path):
                src_path = self.server.document_root + os.sep + self.path
                
            src_path = os.path.realpath(src_path)
            
            if src_path[:len(self.server.document_root)] != self.server.document_root:
                log.warn("Skipped loading resource not in document root \"%s\"" % src_path)
                return
            
            try:
                fd = open(src_path, "rb")
                self.send_response(200) 
                self.send_header("Content-type", type)
                self.end_headers()
                self.wfile.write(fd.read())
                fd.close()
                
            except IOError, e:
                log.error(e)
            
            return
                
        if plugin_name not in self.server.plugins:
            self.send_response(400, "Plugin \"%s\" not found." % plugin_name)
            return
            
        plugin = self.server.plugins[plugin_name]    
        
        try:        
            plugin.handle_get(self, "/".join(token[1:]))
            
        except TemplateSyntaxError, e:
            log.error("Error in handling GET request for plugin \"%s\": %s" %
                (plugin_name, e))
            