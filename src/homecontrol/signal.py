import logging as log, json
from homecontrol.event import Event
from homecontrol.common import JSONEncoder

class Signal(object):

    def __init__(self):
        
        self.id = None
        self.dev_name = None
        self.name = None
        self.vendor = None
        self.description = None
        self.events = []
        self.event_types = []
    
    @staticmethod
    def sql_create(sql):
        sql.execute("CREATE TABLE IF NOT EXISTS 'main'.'Signals' ( "
                    "'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "'dev_name' TEXT NOT NULL, "                    
                    "'name' TEXT NOT NULL, "
                    "'vendor' TEXT, "
                    "'description' TEXT)")
        return
    
    @staticmethod
    def sql_load(sql, signal_id = None, order_by = None):
        Signal.sql_create(sql)
        
        if signal_id != None:
            sql.execute("SELECT id, dev_name, name, vendor, description "
                        "FROM 'Signals' WHERE id=? LIMIT 0,1", (signal_id,))
        else:
            if order_by == None: order_by = "name"
            sql.execute("SELECT id, dev_name, name, vendor, description "
                        "FROM 'Signals' ORDER BY ?", (order_by,))
            
        result = sql.fetchall()
        if signal_id != None and result == None:
            raise Exception("Could not find signal id %i" % signal_id)
            return None
        
        signals = []
        for data in result:
            s = Signal()
            (s.id, s.dev_name, s.name, s.vendor, s.description) = data

            for e in Event.sql_load(sql, signal_id = s.id):
                s.add_event(e)
                
            if signal_id != None: return s
            signals.append(s)
            
        return signals
    
    def sql_save(self, sql):
        Signal.sql_create(sql)
        
        if self.dev_name == None:
            raise Exception("Device name not specified.")
        
        if self.name == None:
            raise Exception("Signal name not specified.")
        

        if self.id == None:
            sql.execute("INSERT INTO Signals (dev_name, name, vendor, description) "
                        "VALUES (?, ?, ?, ?)", (self.dev_name, self.name, self.vendor, self.description))
            self.id = sql.lastrowid
        else:
            sql.execute("UPDATE Signals "
                        "SET dev_name = ?, name = ?, vendor = ?, description = ? "
                        "WHERE id = ?", (self.dev_name, self.name, self.vendor, self.description, str(self.id)))
        
        for event in self.events:
            assert event.signal_id == self.id, \
                "Attempt to save event id %s (signal_id=%s) that don't belong to signal id %s" % \
                (str(event.id), str(event.signal_id), str(self.id))
            event.sql_save(sql)
            
        return
        
    def sql_delete(self, sql):
        Signal.sql_create(sql)
        
        if self.id is None:
            raise Exception("Attempt to delete non-existing signal.")
        
        sql.execute("DELETE FROM Signals WHERE id = ?", (self.id,))
        self.id = None
        return
    
    def add_event(self, event):
        
        if event.type not in self.event_types:
            self.event_types.append(event.type)
            
        self.events.append(event)
        event.signal_id = self.id
        
    @staticmethod
    def from_json(data):
        
            data = json.loads(data)

            signal = Signal()
            signal.dev_name = str(data["dev_name"])
            signal.name = str(data["name"])
            signal.vendor = str(data["vendor"])
            signal.description = str(data["description"])
            
            if "id" in data:
                signal.id = str(data["id"])

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
        obj["events"] = self.events
        obj["event_types"] = self.event_types
        
        return obj