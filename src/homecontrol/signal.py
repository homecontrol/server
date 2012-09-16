import logging as log, json
from homecontrol.event import Event
from homecontrol.common import JSONEncoder

class Signal(object):
    
    id = None
    name = None
    description = None
    events = []
    
    @staticmethod
    def sql_create(sql):
        sql.execute("CREATE TABLE IF NOT EXISTS 'main'.'Signals' ( "
                    "'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "'name' TEXT NOT NULL, "
                    "'description' TEXT)")
        return
    
    @staticmethod
    def sql_load(sql, signal_id = None, order_by = None):
        Signal.sql_create(sql)
        
        if signal_id != None:
            sql.execute("SELECT id, name, description "
                        "FROM 'Signals' WHERE id=? LIMIT 0,1", (signal_id,))
        else:
            if order_by == None: order_by = "name"
            sql.execute("SELECT id, name, description "
                        "FROM 'Signals' ORDER BY ?", (order_by,))
            
        result = sql.fetchall()
        if signal_id != None and result == None:
            raise Exception("Could not find signal id %i" % signal_id)
            return None
        
        signals = []
        for data in result:
            s = Signal()
            (s.id, s.name, s.description) = data
            s.events = Event.sql_load(sql, signal_id = s.id)
            if signal_id != None: return s
            signals.append(s)
            
        return signals
    
    def sql_store(self, sql):
        Signal.sql_create(sql)
        
        if self.name == None:
            raise Exception("Signal name not specified.")
        
        if self.id == None:
            sql.execute("INSERT INTO Signals (name, description) "
                        "VALUES (?, ?)", (self.name, self.description))
            self.id = sql.lastrowid
        else:
            sql.execute("UPDATE Signals "
                        "SET name = ?, description = ? "
                        "WHERE id = ?", (self.name, self.description, self.id))
        
        for event in self.events:
            event.signal_id = self.id
            event.sql_store(sql)
            
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
        obj["name"] = self.name
        obj["description"] = self.description
        obj["events"] = self.events
        
        return json.dumps(obj, cls=JSONEncoder)