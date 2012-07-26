import logging as log, json, sys, time, socket
from threading import Thread, Lock, Event
from telnetlib import Telnet

class Listener(Thread):

	host = None
	event_limit = None
	conn = None
	events = {}
	callbacks = []

	def __init__(self, host, port, event_limit):

		self.event_limit = event_limit
		self.host = host
		self.port = port
		self.timeout = 2 #s

		super(Listener, self).__init__()
		self._stop = Event()
		
	def stop(self):
		self._stop.set()
		
	def is_stopped(self):
		return self._stop.isSet()
	
	def is_connected(self):
		return self.conn is not None
		
	def connect(self):
		
		if self.is_connected():
			return True
		
		if self.is_stopped():
			return False
			
		try:
			
			log.debug("Connecting to event server %s:%i ..." % (self.host, self.port))		
			self.conn = Telnet(self.host, self.port, self.timeout)	
			log.debug("Established connection to event server.")
			return True
			
		except:
			
			if self.is_stopped():
				return False			
				
			log.warning("Could not connect to event server %s:%i, "
						"reason: \"%s\". Will retry in a few seconds ..." % 
						(self.host, self.port, sys.exc_info()[0]))
			
			return False
	
	@staticmethod	
	def decode_list(data):
	    rv = []
	    for item in data:
	        if isinstance(item, unicode):
	            item = item.encode('utf-8')
	        elif isinstance(item, list):
	            item = Listener.decode_list(item)
	        elif isinstance(item, dict):
	            item = Listener.decode_dict(item)
	        rv.append(item)
	    return rv
	
	@staticmethod
	def decode_dict(data):
	    rv = {}
	    for key, value in data.iteritems():
	        if isinstance(key, unicode):
	           key = key.encode('utf-8')
	        if isinstance(value, unicode):
	           value = value.encode('utf-8')
	        elif isinstance(value, list):
	           value = Listener.decode_list(value)
	        elif isinstance(value, dict):
	           value = Listener.decode_dict(value)
	        rv[key] = value
	    return rv
		
	def run(self):
					
		while not self.is_stopped():
			
			try:
				
				if not self.connect():
					time.sleep(0.5)
					continue
					
				json_data = None				
				data = self.conn.read_until("\n", self.timeout)
				json_data = json.loads(data.strip(), object_hook=Listener.decode_dict)
				
				if json_data is None or json_data == "":
					continue
	
				# Discard data if no timing can be found
				if "timings" not in json_data:
					log.debug("Skip invalid data \"%s\"" % str(json_data))
					continue
				
				# TODO: Workaround to add missing receive timestamp that is not
				# yet supported by the device firmware.
				if "time" not in json_data:
					json_data["time"] = time.time()
	
				for (callback,filters) in self.callbacks:

					if not Listener.include(json_data, filters):
						continue
					
					# Append event to the callback's event stack	
					events = self.append_event(str(callback), json_data)
	
					# Call callback function.
					callback(json_data, events)
					
			except socket.timeout:
				continue
			except ValueError:
				continue

	@staticmethod
	def include(event, filters):
		""" Determines whether to include this event.

		The event will be included if at least on of the name value tuples
		of the filters aggrees with the event: The event must provide an 
		attribute with the fitler name whose value is equal the filter value.
		For example:
			A filter list [("type", "rf")] will include an event providing 
			the attribute "type" with value "rf" or "rf-blabla".

		Args:
			event: The event to be included or not.
			filters: A list of name, value tuples to filter the event.

		Returns:
			True if the event is included, false otherwise.
		"""

		if len(filters) == 0: 
			return True

		for (name, value) in filters:
			if name in json_data and value in json_data[name]:
				return True

		return False
			
	def append_event(self, key, event):
		
		# Get events for this callback.
		events = self.events[key]

		# Too much events, remove the first.
		if events == self.event_limit:
			events = self.events[1:]

		# Append new event.
		events.append(event)				

		# Update event list of callback.
		self.events[key] = events
		
		return events

	def register(self, callback, filters = []):
		""" Registers a callback function for new events

		Registered a method that will be called if a new event was received, while 
		the first parameter contains the current event and the second parameter 
		contains a list of events limited to "event_limit" defined in the configuration.


		Args:
			callback: The method to call for each new event.
			filters: A list of name, value tuples to include events that provides
				the given name, value pair. If no filter is specified, all event
				will be accepted. See Listener::include() for more information about
				filters.
		"""
		self.callbacks.append((callback, filters))
		self.events[str(callback)] = []
		
	def unregister(self, callback):
		""" Unregisters a callback function from the listener

		Args:
			callback: The previously registered callback method.
		"""
		callbacks = []
		for i in range(0, len(self.callbacks)):
			if self.callbacks[i][0] != callback:
				callbacks.append(self.callbacks[i])
				
		self.callbacks = callbacks
		self.events[str(callback)] = []