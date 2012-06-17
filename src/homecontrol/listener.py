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
		
	def run(self):
			
		while not self.is_stopped():
			
			try:
				
				if not self.connect():
					time.sleep(0.5)
					continue	
	
				json_data = None
				
				data = self.conn.read_until("\n", self.timeout)
				json_data = json.loads(json.dumps(data.strip(), ensure_ascii=True))
				
				if json_data is None or json_data == "":
					continue
	
				# Discard data if no timing can be found
				if "timings" not in json_data:
					log.debug("Skip invalid data \"%s\"" % str(json_data))
					continue				
	
				for (callback,filters) in self.callbacks:
					
					# Determine whether to include this event
					if len(filters) != 0:
						include = False
						for (name, value) in filters:
							if name in json_data and value in json_data[name]:
								include = True
								break
						if not include:
							continue

					# Get events for this callback.
					events = self.events[str(callback)]

					# Too much events, remove the first.
					if events == self.event_limit:
						events = self.events[1:]

					# Append new event.
					events.append(json_data)				

					# Call callback function.
					callback(json_data, events)

					# Update event list of callback.
					self.events[str(callback)] = events
					
			except socket.timeout:
				continue
			except ValueError:
				continue
			except:
				break

	def register(self, callback, filters = []):
		""" Registeres a callback function for new events

		Registered a method that will be called if a new event was received, while 
		the first parameter contains the current event and the second parameter 
		contains a list of events limited to "event_limit" defined in the configuration.


		Args:
			callback: The method to call for each new event.
			filters: A list of name, value tuples to include events that provides
				the given name, value pair. If no filter is specified, all event
				will be accepted.
		"""

		self.callbacks.append((callback, filters))
		self.events[str(callback)] = []