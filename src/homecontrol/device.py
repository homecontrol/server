import logging as log, httplib, socket
from threading import Lock
from exceptions import RuntimeError
from listener import Listener

__version__ = 0.1

class HCDevice:

	slug = None
	name = None
	config = None
	host = None
	port_cmds = None
	port_events = None
	features = []
	http = None
	event_limit = None
	event_listener = None

	def __init__(self, name, config):

		self.name = name
		self.config = config

		if not self.config.has_section(self.name):
			raise RuntimeError("Device \"%s\" not found in configuration!" % self.name)

		self.timeout = self.config.getint("global", "timeout")
		self.location = self.config.get(self.name, "location");
		self.host = self.config.get(self.name, "host");
		self.port_cmds = self.config.getint(self.name, "port_cmds");
		self.port_events = self.config.getint(self.name, "port_events");
		self.features = [x.strip() for x in self.config.get(self.name, "features").split(",")]
		self.event_limit = self.config.getint("global", "event_limit")
			
	def start_listener(self):

		if self.event_listener is None and self.event_limit > 0:
			self.event_listener = Listener(self.host, self.port_events, self.event_limit)
			self.event_listener.start()
			
	def stop(self):
		
		log.debug("Stopping device \"%s\" ..." % self.name)
		
		if self.event_listener is not None:
			self.event_listener.stop()
			# Don't wait for event listener since in the meantime, we can stop
			# the other event listeners.
			#self.event_listener.join()

	def request(self, url, method = "GET"):
		""" Sends a request to the registered server.

		Sends a request with the given method to the configured 
		server and returns the appropriate response.

		Args:
			url: The request URL.
			method: Method of request which must be either GET or POST.

		Returns:
			A tuple containing status, reason and data of the response.
			Example: 

				(200, "OK", "<html>...</html>")

		Raises:
			httplib.HTTPException: An error occured during the request.
			socket.timeout: The request timed out.
			socket.error: An socket error occured.
		"""

		if url[0] != "/": url = "/%s" % url

		with Lock():

			log.debug("Connecting to http://%s:%i" % (self.host, self.port_cmds))
			self.http = httplib.HTTPConnection(self.host, self.port_cmds, timeout=self.timeout)
			log.debug("Doing %s request, url \"%s\"" % (method, url))
			self.http.request(method, url)
			response = self.http.getresponse()

		# TODO: HomeControler device always returns status code 500 which should be 200 (OK)
		log.debug("Got response status \"%s\" (%i)" % (response.reason, response.status))
		return (response.status, response.reason, response.read().strip())

	def is_available(self):

		with Lock():

			try:
				(_, _, data) = self.request("mem")
				token = data.split(" ")
				return (len(token) == 3 and token[2] == "free")

			except socket.timeout:
				return False
			
	def add_listener(self, callback, filters = []):
		self.start_listener()
		self.event_listener.register(callback, filters)
		return

	def run(self):

		return			

	def rf_send_raw(self, timings):

		return

	def rf_send_tristate(self, tristate):

		# Parse tristate
		tristate = tristate.lower()
		for c in tristate:
			if c != '0' and c != 'f' and c != '1':
				raise ValueError("Invalid tristate value: \"%s\", "
								 "only '1', '0' and 'f' allowed" % tristate)

		log.info("Sending tristate \"%s\", device \"%s\"" % (tristate, self.name))
		(status, reason, data) = self.request("rf-tristate/%s" % tristate)

		if data.strip().lower() != "ok":
			raise RuntimeError("Error while sending tristate \"%s\", "
							   "server returns \"%s\" (%i), "
							   "data \"%s\"" % (tristate, reason, status, data))

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