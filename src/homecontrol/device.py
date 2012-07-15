import logging as log, httplib, socket, json
from threading import Lock
from exceptions import RuntimeError
from listener import Listener

HC_MAX_REQUEST_SIZE = 612

class HCDevice:

	id = None
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

	def __init__(self, id, name, config):

		self.id = id
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

		if len(url) > HC_MAX_REQUEST_SIZE:
			log.warning("Reach max request size, truncate request to %i characters." % HC_MAX_REQUEST_SIZE)
			url = url[0:HC_MAX_REQUEST_SIZE-1]
		
		log.debug("Connecting to http://%s:%i ..." % (self.host, self.port_cmds))
		self.http = httplib.HTTPConnection(self.host, self.port_cmds, timeout=self.timeout)
		log.debug("Doing %s request, url \"%s\" ..." % (method, url))
		self.http.request(method, url)
		response = self.http.getresponse()

		# TODO: HomeControler device always returns status code 500 which should be 200 (OK)
		log.debug("Got response status \"%s\" (%i)." % (response.reason, response.status))
		return (response.status, response.reason, response.read().strip())

	def get_info(self):
		""" Reads device information.
		
		Checks whether current device is online and gets device status
		including firmware version and free memory.
		
		Returns:
			A dict with the following attributes:
			- "status" is set to "online" or "offline".
			- "version" contains the current firmware version if device is online.
			- "memory" contains free amount of memory if the device is online.
		"""
		
		info = {"status": "offline", "version": None, "memory": None};

		try:
			(_, _, data) = self.request("mem")
			token = data.split(" ")
			
			if len(token) == 3 and token[2] == "free":
							
				info["status"] = "online"
				info["version"] = "V1.0" # TODO: Read version if firmware provides it!
				info["memory"] = "%i Bytes" % int(token[0])
			
			return info

		except socket.timeout:
			return info
			
	def add_listener(self, callback, filters = []):
		""" Adds a callback function for new events

		Registeres a method to the listener that will be called if a new event was received.
		See listener.register() for more information.

		Args:
			callback: The method to call for each new event.
			filters: A list of name, value tuples to include events that provides
				the given name, value pair. If no filter is specified, all event
				will be accepted.
		"""
				
		self.start_listener()
		self.event_listener.register(callback, filters)
		return
	
	def rf_add_listener(self, callback):
		return
	
	def ir_add_listener(self, callback):
		return	

	def run(self):

		return

	def get_timings(self, json_data):

		# Json data is expected to be an array
		if type(json_data) != type([]):
			return self.rf_send_json(json_data.strip().split("\n"))

		# Convert to json data if not done so far and extract 
		# timing values.
		timings = []

		for d in json_data:
			
			if type(d) != type({}):
				try:
					d = json.loads(d)
				except ValueError:
					log.warning("Could not parse invalid json data \"%s\", ignore." % d)
					continue

			if "timings" not in d:
				continue
			
			timings.extend([int(x) for x in d["timings"][1:]])	
		
		return timings

	def rf_send_json(self, json_data):
		""" Sends json data via RF module of given device.

		Args:
			json_data: Json data can be either an array of json data objects,
			an array of strings that will then be parsed as json object or a
			string containing several json dumps separated by newlines.
		"""

		timings = self.get_timings(json_data)
		self.rf_send_raw(timings)

	def rf_send_raw(self, timings):
		""" Sends raw code defined by timings via RF module of given device.

		Args:
			timings: Timings in miliseconds that defines the pulse lengths, 
			starting with an high pulse.

		Raises: 
			RuntimeError: If the RF code could not be sent due to a server error.
		"""

		if len(timings) == 0:
			raise ValueError("Found no timings that can be sent to the RF module!")

		log.info("Sending timings \"%s\", device \"%s\"" % (str(timings), self.name))
		(status, reason, data) = self.request("rf-raw/%s" % ".".join([str(t) for t in timings]))

		if data.strip().lower() != "ok":
			raise RuntimeError("Error while sending timings \"%s\", "
							   "server returns \"%s\" (%i), "
							   "data \"%s\"." % (str(timings), reason, status, data))

	def rf_send_tristate(self, tristate):
		""" Sends given tristate via RF module of given device.

		Args:
			tristate: Tristate to be sent, allowed characters are '1', '0' and 
			'f'/'F'.

		Raises: 
			ValueError: For an invalid tristate.
			RuntimeError: If the tristate could not be sent due to a server error.
		"""		

		# Parse tristate
		tristate = tristate.lower()
		for c in tristate:
			if c != '0' and c != 'f' and c != '1':
				raise ValueError("Invalid tristate value: \"%s\", "
								 "only '1', '0' and 'f' allowed!" % tristate)

		log.info("Sending tristate \"%s\", device \"%s\"" % (tristate, self.name))
		(status, reason, data) = self.request("rf-tristate/%s" % tristate)

		if data.strip().lower() != "ok":
			raise RuntimeError("Error while sending tristate \"%s\", "
							   "server returns \"%s\" (%i), "
							   "data \"%s\"." % (tristate, reason, status, data))
			
	def ir_send_json(self, json_data):
		""" Sends json data via IR module of given device.

		Args:
			json_data: Json data can be either an array of json data objects,
			an array of strings that will then be parsed as json object or a
			string containing several json dumps separated by newlines.
		"""

		timings = self.get_timings(json_data)
		self.ir_send_raw(timings)			

	def ir_send_raw(self, timings, khz = None):
		""" Sends raw code defined by timings via IR module of given device.

		Args:
			timings: Timings in miliseconds that defines the marks and spaces
			of the IR code starting with a mark (high pulse).
			khz: The modulation frequency in khz of the IR base signal. By 
			default, the frequency is "None" and defined by the device itself. 

		Raises: 
			RuntimeError: If the IR code could not be sent due to a server error.
		"""

		if len(timings) == 0:
			raise ValueError("Found no timings that can be sent to the IR module!")
		
		request = "ir-raw/%s" % ".".join([str(t) for t in timings])
		
		if khz is not None:
			request = "%s/%s" % (request, khz)

		log.info("Sending timings \"%s\", device \"%s\"" % (str(timings), self.name))
		(status, reason, data) = self.request(request)

		if data.strip().lower() != "ok":
			raise RuntimeError("Error while sending timings \"%s\", "
							   "server returns \"%s\" (%i), "
							   "data \"%s\"." % (str(timings), reason, status, data))		
		return

	def ir_send_nec_binary(self, bin):
		""" Sends given NEC compatible binary string via IR module of given device.

		Args:
			bin: NEC compatible binary string, allowed characters are '1' and '0'.

		Raises: 
			ValueError: For an invalid binary string..
			RuntimeError: If the binary string could not be sent due to a server error.
		"""		

		for b in bin:
			if b != '0' and b != '1':
				raise ValueError("Invalid binary value value: \"%s\", "
								 "only '1' and '0' allowed!" % bin)

		log.info("Sending NEC binary string \"%s\", device \"%s\"" % (bin, self.name))
		(status, reason, data) = self.request("ir-nec/%s/%i" % (bin, len(bin)))

		if data.strip().lower() != "ok":
			raise RuntimeError("Error while sending binary string \"%s\", "
							   "server returns \"%s\" (%i), "
							   "data \"%s\"." % (bin, reason, status, data))
		return