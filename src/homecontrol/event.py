import logging as log, json, time
from common import *

class HCEvent(object):

	id = None
	type = None
	timings = []
	receive_time = None
	json_data = None

	def __init__(self):
		return
		
	@staticmethod
	def sql_create(sql):
		
		sql.execute("CREATE TABLE IF NOT EXISTS 'main'.'Events' ( "
					"'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
					"'type' TEXT NOT NULL, "
					"'json' TEXT NOT NULL")
		return
	
	@staticmethod
	def sql_load(sql, event_id):
		HCEvent.sql_create(sql)
		
		sql.execute("SELECT id, type, receive_time, timings "
					"FROM 'Events' stocks WHERE id=? LIMIT 0,1", (event_id,))
		data = c.fetchone()
		
		if data == None:
			log.error("Event id %s not found in database" % event_id)
			return None
		
		(id, type, json) = data
		event = HCEvent.from_json(json)
		event.id = id
		
		return event
	
	def sql_store(self, sql):
		HCEvent.sql_create(sql)
		
		sql.execute("INSERT INTO Events (type, json) "
					"VALUES (?, ?)", (self.type, self.json_data))
		
		self.id = sql.last_row_id
		return
	
	def sql_delete(self, sql):
		HCEvent.sql_create(sql)
		
		if self.id is None:
			log.warning("Ignore attempt to delete non-existing event.")
			return
		
		sql.execute("DELETE FROM Events WHERE id = ?", (self.id,))
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
			if name in self.json_data and value in self.json_data[name]:
				return True

		return False

	@staticmethod
	def from_json(data):

		try:

			json_data = json.loads(data.strip(), object_hook=HCEvent.decode_dict)

			if json_data is None or json_data == "":
				return None

			if "timings" not in json_data:
				log.debug("Skip data without timings \"%s\"" % str(json_data))
				return None

			if "type" not in json_data:
				log.debug("Skip data without event type \"%s\"" % str(json_data))

			event = None

			if json_data["type"] == "ir":
				event = HCIREvent()
				event.decoding = json_data["decoding"]
				event.hex = hex(int(str(json_data["hex"]), 16))
				event.length = json_data["length"]

			elif json_data["type"] == "rf":
				event = HCRFEvent()
				if "error" in json_data:
					event.error = json_data["error"]
				event.pulse_length = json_data["pulse_length"]
				event.len_timings = json_data["len_timings"]

			else: 

				log.debug("Event type \"%s\" not supported" % json_data["type"])
				
			# TODO: Use receive time from device if firmware supports it!
			if "receive_time" not in json_data:
				json_data["receive_time"] = time.time()
								
			event.receive_time = json_data["receive_time"]			 
			event.timings = json_data["timings"]

			event.json_data = json_data 
			
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
	            item = HCEvent.decode_list(item)
	        elif isinstance(item, dict):
	            item = HCEvent.decode_dict(item)
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
	           value = HCEvent.decode_list(value)
	        elif isinstance(value, dict):
	           value = HCEvent.decode_dict(value)
	        rv[key] = value
	    return rv   
	   
class HCIREvent(HCEvent):

	type = HC_TYPE_IR
	decoding = None
	hex = '0x0'
	length = 0

class HCRFEvent(HCEvent):

	type = HC_TYPE_RF
	error = None
	pulse_length = 0
	len_timings = 0