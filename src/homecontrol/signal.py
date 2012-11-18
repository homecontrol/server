import logging as log, json, time
from homecontrol.event import Event
from homecontrol.common import *

class Signal(object):

    def __init__(self, id = None):
        
        self.id = id
        self.dev_name = None
        self.name = None
        self.vendor = None
        self.description = None
        self.delay = None
        self.events = []
        self.event_types = []
    
    @staticmethod
    def sql_create(sql):
        sql.execute("CREATE TABLE IF NOT EXISTS signals ( "
                    "'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "'dev_name' TEXT DEFAULT NULL, "
                    "'name' TEXT DEFAULT NULL, "
                    "'vendor' TEXT DEFAULT NULL, "
                    "'description' TEXT DEFAULT NULL, "
                    "'delay' INTEGER DEFAULT NULL)")
        return
    
    @staticmethod
    def sql_load(sql, signal_id = None, order_by = None):
        Signal.sql_create(sql)
        
        if signal_id != None:
            sql.execute("SELECT id, dev_name, name, vendor, description, delay "
                        "FROM signals WHERE id=? LIMIT 0,1", (signal_id,))
        else:
            if order_by == None: order_by = "name"
            sql.execute("SELECT id, dev_name, name, vendor, description, delay "
                        "FROM signals ORDER BY ?", (order_by,))
            
        result = sql.fetchall()
        if signal_id != None and len(result) == 0:
            raise Exception("Could not find signal id \"%s\"" % signal_id)
            return None
        
        signals = []
        for data in result:
            signal = Signal()
            
            signal.id = get_value(data[0], "id", int, optional = True)
            signal.dev_name = get_value(data[1], "dev_name", str, optional = True)
            signal.name = get_value(data[2], "name", str, optional = True)
            signal.vendor = get_value(data[3], "vendor", str, optional = True)
            signal.description = get_value(data[4], "description", str, optional = True)
            signal.delay = get_value(data[5], "delay", int, optional = True)            

            for e in Event.sql_load(sql, signal_id = signal.id):
                signal.add_event(e)
                
            if signal_id != None: return signal
            signals.append(signal)
            
        return signals
    
    def sql_save(self, sql):
        Signal.sql_create(sql)
        
        # Non delay signals must have a name and default device.
        if self.delay == None:
            if self.dev_name == None: raise Exception("Device name not specified.")
            if self.name == None: raise Exception("Signal name not specified.")
        
        if self.id == None:
            sql.execute("INSERT INTO signals (dev_name, name, vendor, description, delay) "
                        "VALUES (?, ?, ?, ?, ?)", (self.dev_name, self.name, self.vendor, self.description, self.delay))
            self.id = sql.lastrowid
            log.debug("Created signal id %s" % str(self.id))
        else:
            sql.execute("UPDATE signals "
                        "SET dev_name = ?, name = ?, vendor = ?, description = ?, delay = ? "
                        "WHERE id = ?", (self.dev_name, self.name, self.vendor, self.description, self.delay, str(self.id)))
            log.debug("Updated signal id %s" % str(self.id))
        
        for event in self.events:
            event.signal_id = self.id
            event.sql_save(sql)
            
        return self
        
    def sql_delete(self, sql):
        Signal.sql_create(sql)
        
        if self.id is None:
            raise Exception("Attempt to delete non-existing signal.")
        
        sql.execute("DELETE FROM signals WHERE id = ?", (self.id,))
        self.id = None
        return
    
    def add_event(self, event):
        
        if event.type not in self.event_types:
            self.event_types.append(event.type)
            
        event.signal_id = self.id
        self.events.append(event)        
        
    @staticmethod
    def from_json(data):
        
        if type(data) != type({}):
            data = json.loads(str(data).strip())

        signal = Signal()
        
        signal.id = get_value(data, "id", int, optional = True)
        signal.dev_name = get_value(data, "dev_name", str, optional = True)
        signal.name = get_value(data, "name", str, optional = True)
        signal.vendor = get_value(data, "vendor", str, optional = True)
        signal.description = get_value(data, "description", str, optional = True)
        signal.delay = get_value(data, "delay", int, optional = True)

        for e in data["events"]: 
            signal.add_event(Event.from_json(e))
                        
        return signal
        
    def to_json(self):
        
        obj = {}
        obj["id"] = self.id
        obj["dev_name"] = self.dev_name
        obj["name"] = self.name
        obj["vendor"] = self.vendor
        obj["description"] = self.description
        obj["delay"] = self.delay
        obj["events"] = self.events
        obj["event_types"] = self.event_types
        
        # Optional attributes
        #if self.vendor == None: obj["vendor"] = "";
        #if self.description == None: obj["description"] = "";
        #if self.delay == None: obj["delay"] = "";
        
        return json.dumps(obj, cls=JSONEncoder)
    
    def send(self, device = None):
        
        if self.delay != None:
            time.sleep(self.delay / 1000)
            return
        
        # TODO: No chance to get the device from dev_name!
        if device == None:
            raise Exception("No device specified to send signal \"%s\"" % self.name)
        
        for event in self.events:
            if event.type == HC_TYPE_IR: device.ir_send_raw(event.timings)
            elif event.type == HC_TYPE_RF: device.rf_send_raw(event.timings)
            
            
            
        