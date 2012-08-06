import logging as log, json, time
from common import *

class HCEvent(object):

	type = None
	timings = []
	receive_time = None
	json_data = None
	gap = 0

	def __init__(self):
		return

	def include(self, filters):
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
				event.hex = hex(int(json_data["hex"], 16))
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