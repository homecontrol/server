from bootstrap import Bootstrap

class Index(Bootstrap):

	def handle_request(self, handler, method, path=None, args={}, data=None):

		if path == "/":
			self.send_html_response(
				handler=handler, 
				html_file="assets/html/index.html", 
				devices=self.get_devices())

			return True

		return False