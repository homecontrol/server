import logging as log, httplib, socket, json, time
from threading import Lock
from exceptions import RuntimeError
from homecontrol.listener import Listener
from homecontrol.event import *
from homecontrol.common import *

class Device:

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
	
	event_callback = None
	event_queue = []

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
		
		self.event_queue = []
			
	def start_listener(self):

		if self.event_listener is None and self.event_limit > 0:
			self.event_listener = Listener(self.host, self.port_events, self.event_limit)
			self.event_listener.start()
			
	def stop_listener(self):
		
		if self.event_listener is not None:
			self.event_listener.stop()
			# Don't wait for event listeners since we don't need
			# them anymore!
			#self.event_listener.join()
			self.event_listener = None

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
		
		max_request_size = HC_MAX_REQUEST_SIZE - len(self.host) - len(str(self.port_cmds)) - 1

		if len(url) > max_request_size:
			log.warning("Reach max request size, truncate request to %i characters." % HC_MAX_REQUEST_SIZE)
			url = url[0:max_request_size -1]
		
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
			A dict with the following string attributes:
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

		Registers a method to the listener that will be called if a new event was received.
		See listener.register() for more information.

		Args:
			callback: The method to call for each new event.
			filters: A list of name, value tuples to include events that provides
				the given name, value pair. If no filter is specified, all events
				will be accepted. See Event.include() for more information about
				filters.
		"""
		self.start_listener()
		self.event_listener.register(callback, filters)
		return
	
	def rf_add_listener(self, callback):
		""" Adds a callback function for RF events

		Registers a method to the listener that will be called if a new RF event was 
		received. See listener.register() for more information.

		Args:
			callback: The method to call for each new event.
		"""
		self.add_listener(callback, [("type", HC_TYPE_RF)])
		return
	
	def ir_add_listener(self, callback):
		""" Adds a callback function for IR events

		Registers a method to the listener that will be called if a new IR event was 
		received. See listener.register() for more information.

		Args:
			callback: The method to call for each new event.			
		"""
		self.add_listener(callback, [("type", HC_TYPE_IR)])
		return
	
	def add_event(self, event, event_queue):
		self.event_queue = event_queue;
	
	def start_capture(self):
		""" Starts event capturing.
		
		Starts to capture events from the current device. See Device.get_events(), 
		Device.rf_get_events() or Device.ir_get_events() to access already captured 
		events. See Device.stop_capture() to stop capturing.
		"""
		self.start_listener()
		
		self.stop_capture() # Just make sure we do not capture twice!
		self.event_listener.register(getattr(self, "add_event"))

		return True
	
	def stop_capture(self):
		""" Stops event capturing.
		
		Stops to capture events from the current device. Already captured events 
		will be discarded.
		"""
		if self.event_listener is None:
			return True
		
		self.event_listener.unregister(getattr(self, "add_event"))
		return True
	
	def get_events(self, timestamp = None, filters = []):
		""" Returns captured events.
		
		Returns captured events that are received after the given time and that 
		agree with the given filters. See Device.start_capture() that must be 
		used to enabled capturing before events can be retrieved using this 
		method.
		
		Args:
			timestamp: Return events that are newer than the given timestamp. Leave 
				empty to retrieve all captured events since Device.start_capture().
			filters: A list of name, value tuples to include events that provides
				the given name, value pair. If no filter is specified, all captured
				events will be returned. See Event.include() for more information about
				filters.
				
		Return:
			An array of event objects or an empty array if no events have been 
			captured so far.
		"""
		events = []
		for e in self.event_queue:

			if not Event.include(e, filters):
				continue

			if timestamp != None and e.receive_time <= float(timestamp):
				continue		
		
			events.append(e)
			
		return events
	
	def rf_get_events(self, timestamp = None):
		""" Returns captured RF events.
		
		This is a wrapper for Device.get_events() with an appropriate filter to 
		include RF events only.
		
		Args:
			timestamp: Return events that are newer than the given timestamp. Leave 
				empty to retrieve all captured events since Device.start_capture().
			
		Return:
			An array of RF event objects or an empty array if no events have been 
			captured so far.			
		"""	
		return self.get_events(timestamp, [("type", HC_TYPE_RF)])
	
	def ir_get_events(self, timestamp = None):
		""" Returns captured IR events.
		
		This is a wrapper for Device.get_events() with an appropriate filter to 
		include IR events only.
		
		Args:
			timestamp: Return events that are newer than the given timestamp. Leave 
				empty to retrieve all captured events since Device.start_capture().
			
		Return:
			An array of IR event objects or an empty array if no events have been 
			captured so far.			
		"""
		return self.get_events(timestamp, [("type", HC_TYPE_IR)])	

	def get_timings(self, json_data):

		if type(json_data) != type([]):
			return self.get_timings(json_data.strip().split("\n"))

		timings = []
		for d in json_data:

			event = Event.from_json(d)
			if event == None: continue
			timings.extend([int(x) for x in event.timings])	
		
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
		
		# Remove the first timing since this is the gap to
		# the previous received signal!
		timings = timings[1:]

		log.info("Sending %i timings \"%s\", device \"%s\"" % (len(timings), str(timings), self.name))
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
		
		# Remove the first timing since this is the gap to
		# the previous received signal!
		timings = timings[1:]		
		
		request = "ir-raw/%s" % ".".join([str(t) for t in timings])
		
		if khz is not None:
			request = "%s/%s" % (request, khz)

		log.info("Sending timings \"%s\", device \"%s\"" % (str(timings), self.name))
		(status, reason, data) = self.request(request)

		if data.strip().lower() != "ok":
			raise RuntimeError("Error while sending timings \"%s\", "
							   "server returns \"%s\" (%i), "
							   "data \"%s\"." % (str(timings), reason, status, data))		

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