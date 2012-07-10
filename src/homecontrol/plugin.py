import os
import logging as log
from exceptions import NotImplementedError
from genshi.template import TemplateLoader, MarkupTemplate, Context
from genshi.input import HTML

class HCPlugin:
    
    server = None
    name = None
    template = None
    
    def __init__(self, server):
        self.server = server
        
        template_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep + \
            "plugins" + os.sep + self.__module__

        self.log_debug("Using templates from \"%s\"" % template_dir)
        self.template = TemplateLoader(template_dir)
        
    def handle_get(self, handler, path):
        raise NotImplementedError
    
    def log_warn(self, msg):
        log.warn("[%s]: %s" % (self.__module__, msg))
        
    def log_debug(self, msg):
        log.debug("[%s]: %s" % (self.__module__, msg))
        
    def log_info(self, msg):
        log.info("[%s]: %s" % (self.__module__, msg))
        
    """
    @todo: Add description!!!!
    """
    def send(self, handler, code = 200, **kwargs):
        
        handler.send_response(code)
        
        if "template" in kwargs:
        
            handler.send_header("Content-type", 'text/html')
            handler.end_headers()
            
            template_path = os.path.dirname(os.path.realpath(__file__)) + os.sep + \
                "assets" + os.sep + "html" + os.sep + "index.html"
            fd = open(template_path)
            template = MarkupTemplate(fd, template_path)
            fd.close()
            
            html = HTML(self.template.load(kwargs["template"]).generate(**kwargs).render())
            template = template.generate(Context(input=html))
            
            handler.wfile.write(template.render('xhtml', doctype='html'))
            return
        
        raise NotImplementedError