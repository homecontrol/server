from plugin import HCPlugin

class Index(HCPlugin):

    def handle_get(self, handler, path):
        
        self.send(handler=handler, template="assets/html/index.html", devices=self.server.devices)