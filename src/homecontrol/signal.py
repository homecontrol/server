import logging as log, json
from homecontrol.event import Event
from homecontrol.common import JSONEncoder

class Signal(object):
    
    id = None
    devide_id = None    
    name = None
    vendor = None
    description = None
    events = []
    
    @staticmethod
    def sql_create(sql):
        sql.execute("CREATE TABLE IF NOT EXISTS 'main'.'Signals' ( "
                    "'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "'device_id' TEXT NOT NULL, "                    
                    "'name' TEXT NOT NULL, "
                    "'vendor' TEXT, "
                    "'description' TEXT)")
        return
    
    @staticmethod
    def sql_load(sql, signal_id = None, order_by = None):
        Signal.sql_create(sql)
        
        if signal_id != None:
            sql.execute("SELECT id, device_id, name, vendor, description "
                        "FROM 'Signals' WHERE id=? LIMIT 0,1", (signal_id,))
        else:
            if order_by == None: order_by = "name"
            sql.execute("SELECT id, device_id, name, vendor, description "
                        "FROM 'Signals' ORDER BY ?", (order_by,))
            
        result = sql.fetchall()
        if signal_id != None and result == None:
            raise Exception("Could not find signal id %i" % signal_id)
            return None
        
        signals = []
        for data in result:
            s = Signal()
            (s.id, s.devide_id, s.name, s.vendor, s.description) = data
            s.events = Event.sql_load(sql, signal_id = s.id)
            if signal_id != None: return s
            signals.append(s)
            
        return signals
    
    def sql_save(self, sql):
        Signal.sql_create(sql)
        
        if self.device_id == None:
            raise Exception("Device id not specified.")
        
        if self.name == None:
            raise Exception("Signal name not specified.")
        
        if self.id == None:
            sql.execute("INSERT INTO Signals (device_id, name, vendor, description) "
                        "VALUES (?, ?, ?, ?)", (self.device_id, self.name, self.vendor, self.description))
            self.id = sql.lastrowid
        else:
            sql.execute("UPDATE Signals "
                        "SET device_id = ?, name = ?, vendor = ?, description = ? "
                        "WHERE id = ?", (self.device_id, self.name, self.vendor, self.description, self.id))
        
        for event in self.events:
            event.signal_id = self.id
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
        
        self.events.append(event)
        event.signal_id = id
        
    def to_json(self):
        
        obj = {}
        obj["id"] = self.id
        obj["device_id"] = self.devide_id
        obj["name"] = self.name
        obj["vendor"] = self.vendor
        obj["description"] = self.description
        obj["events"] = self.events
        
        return obj