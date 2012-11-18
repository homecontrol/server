from bootstrap import Bootstrap

class Index(Bootstrap):

	def view(self, handler):

		self.send_html_response(handler=handler, 
			html_file="assets/html/index.html", 
			devices=self.get_devices())