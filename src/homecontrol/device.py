import logging as log, httplib, socket
from threading import Lock
from exceptions import RuntimeError

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
		"""

		if url[0] != "/": url = "/%s" % url

		#try:
		log.debug("Connecting to http://%s:%i" % (self.host, self.port_cmds))
		self.http = httplib.HTTPConnection(self.host, self.port_cmds, timeout=self.timeout)
		log.debug("Doing %s request, url \"%s\"" % (method, url))
		self.http.request(method, url)
		response = self.http.getresponse()
		#except httplib.HTTPException as e:
		#	log.error("Request failed: %s" % e)
		#	return None
		#except socket.timeout as e:
		#	log.error("Request timed out: %s" % e)
		#	return None
		#except socket.error as e:
		#	log.error("Socket error: %s" % e)
		#	return None

		# TODO: HomeControler device always returns status code 500 which should be 200 (OK)
		log.debug("Got response status \"%s\" (%i)" % (response.reason, response.status))
		return (response.status, response.reason, response.read().strip())

	def is_available(self):

		with Lock():

			try:
				(status, reason, data) = self.request("mem")
				token = data.split(" ")
				return (len(token) == 3 and token[2] == "free")

			except socket.timeout:
				return False

	def rf_send_raw(self, timings):

		return

	def rf_send_tristate(self, tristate):

		# Parse tristate
		tristate = tristate.lower()
		for c in tristate:
			if c != '0' and c != 'f' and c != '1':
				raise ValueError("Invalid tristate value: \"%s\", only '1', '0' and 'f' allowed" % tristate)

		with Lock():

			log.info("Sending tristate \"%s\", device \"%s\"" % (tristate, self.name))
			(status, reason, data) = self.request("rf-tristate/%s" % tristate)

			if data.strip().lower() != "ok":
				raise RuntimeError("Error while sending tristate \"%s\", server responds \"%s\"" % (tristate, data))

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
