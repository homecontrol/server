from bootstrap import Bootstrap

class Index(Bootstrap):

    def handle_get(self, handler, path):
        
        if path == "/":

        	self.send_html_response(
	        	handler=handler, 
	        	html_file="assets/html/index.html", 
	        	devices=self.get_devices())

	        # Return true to indicate successful request handling.
	        return True

		return False