from plugin import HCPlugin
import os
from genshi.template import TemplateLoader, MarkupTemplate, Context
from genshi.input import HTML

class Bootstrap(HCPlugin):

    def __init__(self, server):
        super(Bootstrap, self).__init__(server)
        
        template_dir = os.path.dirname(__file__) + os.sep + ".." + os.sep + self.name

        self.log_debug("Using templates from \"%s\"" % template_dir)
        self.template = TemplateLoader(template_dir)
    
    def send_html_response(self, handler, html_file, code=200, skip_template=False, **kwargs):
        """ Generates and sends an HTML response.

        This generates headers and an HTML response either from the specified HTML 
        source or HTML file. Both will be parsed using the Genhsi template engine
        and will be extended with the default template.

        Args:
            handler: References the handler of the current http request.
            code: Defines the response code is send within the http headers, 
                by default, responde code 200 (success) is sent.
            html_file: Must reference a HTML document within the current 
                document root or the plugin directory that will be loaded and
                parsed using Genshi.
            **kwargs: Any additional parameter will be forwarded to the Genshi 
                template.
        """        
        
        handler.send_response(code)
        handler.send_header("Content-type", 'text/html')
        handler.end_headers()

        # Add additional template parameters
        kwargs["plugin"] = self.__module__
            
        if skip_template:

            handler.wfile.write(
                self.template.load(kwargs["html"]).generate(**kwargs).render())

        else:

            template_path = os.path.dirname(__file__) + os.sep + \
                "assets" + os.sep + "html" + os.sep + "index.html"
            fd = open(template_path)
            template = MarkupTemplate(fd, template_path)
            fd.close()
        
            html = HTML(self.template.load(html_file).generate(**kwargs).render())
            template = template.generate(Context(input=html, **kwargs))
        
            handler.wfile.write(template.render('xhtml', doctype='html'))
