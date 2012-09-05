import logging as log
from homecontrol.event import HCEvent

class HCSignal(object):
    
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
    def sql_load(sql, signal_id):
        HCSignal.sql_create(sql)
        
        sql.execute("SELECT id, name, description "
                    "FROM 'Signals' WHERE id=? LIMIT 0,1", (signal_id,))
        data = sql.fetchone()
        
        if data == None:
            raise Exception("Could not find signal id %i" % signal_id)
            return None
        
        s = HCSignal()
        (s.id, s.name, s.description) = data
        s.events = HCEvent.sql_load(signal_id = s.id)
    
    def sql_store(self, sql):
        HCSignal.sql_create(sql)
        
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
        HCSignal.sql_create(sql)
        
        if self.id is None:
            raise Exception("Attempt to delete non-existing signal.")
        
        sql.execute("DELETE FROM Signals WHERE id = ?", (self.id,))
        self.id = None
        return
    
    def add_event(self, event):
        
        self.events.append(event)
        event.signal_id = id