import logging as log, json, sys, time, socket
from threading import Thread, Lock, Event as TreadEvent
from telnetlib import Telnet
from homecontrol.event import Event

class Listener(Thread):

	def __init__(self, host, port, event_limit):

		self.host = host
		self.port = port
		self.event_limit = event_limit
		self.conn = None
		self.events = {}
		self.callbacks = []
		self.timeout = 2 #s

		super(Listener, self).__init__()
		self._stop = TreadEvent()
		
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
			
				data = self.conn.read_until("\n", self.timeout)
				if data == None or data == "": continue
				
				event = Event.from_json(data)
				if event == None: continue
					
				for (callback,filters) in self.callbacks:

					if not event.include(filters):
						continue
					
					# Append event to the callback's event stack	
					events = self.append_event(str(callback), event)
	
					# Call callback function.
					callback(event, events)
					
			except socket.timeout:
				continue
			
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