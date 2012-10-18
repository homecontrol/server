import logging as log, json, time
from homecontrol.common import *

class Event(object):
	
	def __init__(self):
		
		self.id = None
		self.signal_id = None
		self.type = None
		self.timings = []
		self.receive_time = None
		
	@staticmethod
	def sql_create(sql):
		
		sql.execute("CREATE TABLE IF NOT EXISTS 'main'.'events' ( "
					"'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
					"'signal_id' INTEGER NOT NULL, "
					"'type' TEXT NOT NULL, "
					"'json' TEXT NOT NULL, "
					"FOREIGN KEY(signal_id) REFERENCES signals(id) ON DELETE CASCADE)")
		return
	
	@staticmethod
	def sql_load(sql, event_id = None, signal_id = None):
		Event.sql_create(sql)

		if event_id != None:		
			sql.execute("SELECT id, signal_id, type, json "
						"FROM 'events' WHERE id=? LIMIT 0,1", (event_id,))
			
		elif signal_id != None:
			sql.execute("SELECT id, signal_id, type, json "
						"FROM 'events' WHERE signal_id=?", (signal_id,))
		
		events = []
		for data in sql.fetchall():

			(id, signal_id, type, json) = data

			event = Event.from_json(json)
			event.id = id
			event.signal_id = signal_id
			events.append(event)
			
		if len(events) == 0:
			if event_id != None:
				log.error("Could not find event id %i" % event_id)
			elif signal_id != None:
				log.error("Coult not find any event for signal id %i" % signal_id)
		
		return events
	
	def sql_save(self, sql):
		Event.sql_create(sql)
		
		if self.signal_id == None:
			raise Exception("Missing signal id to store event: %s" % str(self.to_json()))
		
		if self.type == None:
			raise Exception("Missing event type to store event %s: %s" % str(self.to_json()))
		
		# Prepare json data string
		json = str(self.to_json())
		json = json.replace("u'","'")
		json = json.replace("'","\"")
		
		if self.id == None:
			sql.execute("INSERT INTO events (signal_id, type, json) "
						"VALUES (?, ?, ?)", (self.signal_id, self.type, json))
			self.id = sql.lastrowid
			log.debug("Created event id %s for signal id %s" % (self.id, self.signal_id))
		else:
			sql.execute("UPDATE events "
						"SET signal_id = ?, type = ?, json = ? "
						"WHERE id = ?", (self.signal_id, self.type, json, self.id))
			log.debug("Updated event id %s for signal id %s" % (self.id, self.signal_id))
	
	def sql_delete(self, sql):
		Event.sql_create(sql)
		
		if self.id is None:
			log.warning("Ignore attempt to delete non-existing event.")
			return
		
		sql.execute("DELETE FROM events WHERE id = ?", (self.id,))
		self.id = None
		return

	def include(self, filters):
		""" Determines whether to include this event.

		The event will be included if at least on of the name value tuples
		of the filters agrees with the event: The event must provide an 
		attribute with the filter name whose value is equal the filter value.
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
			if hasattr(self, name) and value in getattr(self, name):
				return True

		return False

	@staticmethod
	def from_json(data):
		
		try:
			
			if type(data) != type({}):
				data = json.loads(str(data).strip(), object_hook=Event.decode_dict)

			if data is None or data == "":
				return None

			if "timings" not in data:
				log.debug("Skip data without timings \"%s\"" % str(data))
				return None

			if "type" not in data:
				log.debug("Skip data without event type \"%s\"" % str(data))

			event = None

			if data["type"] == "ir":
				event = IREvent()
				event.decoding = data["decoding"]
				event.hex = hex(int(str(data["hex"]), 16))
				event.length = data["length"]

			elif data["type"] == "rf":
				event = RFEvent()
				if "error" in data:
					event.error = data["error"]
				event.pulse_length = data["pulse_length"]
				event.len_timings = data["len_timings"]

			else: 

				log.debug("Event type \"%s\" not supported" % data["type"])
				
			# TODO: Use receive time from device if firmware supports it!
			if "receive_time" not in data:
				data["receive_time"] = time.time()
				
			if "id" in data and data["id"] != None:
				event.id = int(data["id"])
				
			if "signal_id" in data and data["signal_id"] != None:
				event.signal_id = int(data["signal_id"])
								
			event.receive_time = data["receive_time"]			 
			event.timings = data["timings"]
			
			return event
		
		except TypeError, e:
			log.debug("Could not load event data \"%s\", reason: %s" % (data, e))

		except ValueError, e:
			log.debug("Skip invalid data \"%s\", reason: %s" % (data, e))
			
		return None
	
	@staticmethod	
	def decode_list(data):
	    rv = []
	    for item in data:
	        if isinstance(item, unicode):
	            item = item.encode('utf-8')
	        elif isinstance(item, list):
	            item = Event.decode_list(item)
	        elif isinstance(item, dict):
	            item = Event.decode_dict(item)
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
	           value = Event.decode_list(value)
	        elif isinstance(value, dict):
	           value = Event.decode_dict(value)
	        rv[key] = value
	    return rv   
	   
class IREvent(Event):

	def __init__(self):		
		super(IREvent, self).__init__()
		
		self.type = HC_TYPE_IR
		self.decoding = None
		self.hex = '0x0'
		self.length = 0
		
	def to_json(self):
		
		obj = { }
		obj["id"] = self.id
		obj["signal_id"] = self.signal_id
		obj["receive_time"] = self.receive_time
		obj["timings"] = self.timings		
		obj["type"] = self.type
		obj["decoding"] = self.decoding
		obj["hex"] = self.hex
		obj["length"] = self.length
		
		return json.dumps(obj, cls=JSONEncoder)

class RFEvent(Event):

	def __init__(self):
		super(RFEvent, self).__init__()
		
		self.type = HC_TYPE_RF
		self.error = None
		self.pulse_length = 0
		self.len_timings = 0
		
	def to_json(self):
		
		obj = { }
		obj["id"] = self.id
		obj["signal_id"] = self.signal_id
		obj["receive_time"] = self.receive_time
		obj["timings"] = self.timings		
		obj["type"] = self.type
		obj["error"] = self.error
		obj["pulse_length"] = self.pulse_length
		obj["len_timings"] = self.len_timings
		
		return json.dumps(obj, cls=JSONEncoder)