from plugin import HCPlugin

class Index(HCPlugin):

    def handle_get(self, handler, path):
        
        self.send_html_response(
        	handler=handler, 
        	html_file="assets/html/index.html", 
        	devices=self.server.devices)