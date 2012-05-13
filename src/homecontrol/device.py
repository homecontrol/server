__version__ = 0.1

class Device:

	config = None

	def __init__(self, config):

		self.config = config


	def rf_send_raw(self):

		return

	def rf_send_tristate(self):

		return

	def rf_send_binary(self):

		return

	def rf_add_listener(self, callback):

		return

	def ir_send_raw(self):

		return

	def ir_send_binary(self):

		return

	def ir_add_listener(self, callback):

		return

	def run(self):

		return
