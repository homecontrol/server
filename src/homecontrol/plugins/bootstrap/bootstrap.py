from homecontrol.plugin import Plugin
import os
from genshi.template import TemplateLoader, MarkupTemplate, Context
from genshi.input import HTML
from genshi.filters import HTMLFormFiller

class Bootstrap(Plugin):

    def __init__(self, server):
        super(Bootstrap, self).__init__(server)
        
        template_dir = os.path.dirname(__file__) + os.sep + ".." + os.sep + self.name

        self.log_debug("Using templates from \"%s\"" % template_dir)
        self.template = TemplateLoader(template_dir)
    
    def send_html_response(self, handler, html_file, code=200, html_form_data={}, **kwargs):
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
            html_form_data: Pass additional html form data to auto-fill html forms
                using genshi.filters.HTMLFormFiller.
            **kwargs: Any additional parameter will be forwarded to the Genshi 
                template.
        """        
        
        handler.send_response(code)
        handler.send_header("Content-type", 'text/html')
        handler.end_headers()

        # Add additional template parameters
        kwargs["plugin"] = self.__module__
            
        template_path = os.path.dirname(__file__) + os.sep + \
            "assets" + os.sep + "html" + os.sep + "index.html"
        fd = open(template_path)
        template = MarkupTemplate(fd, template_path)
        fd.close()

        filler = HTMLFormFiller(data=html_form_data)
    
        # See http://stackoverflow.com/questions/1555644/can-one-prevent-genshi-from-parsing-html-entities
        # because of "us-ascii" encoding.
        html = HTML(self.template.load(html_file).generate(**kwargs).render(encoding= 'us-ascii'))
        template = template.generate(Context(input=html.filter(filler), **kwargs))
    
        handler.wfile.write(template.render('xhtml', doctype='html', encoding= 'us-ascii'))
