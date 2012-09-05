import json, sys
from bootstrap import Bootstrap
from homecontrol.event import HCEvent
from homecontrol.signal import HCSignal

class Signals(Bootstrap):

    def handle_request(self, handler, method, path=None, args={}, data=None):

        if path == "/":
            self.send_html_response(
                handler=handler, 
                html_file="assets/html/index.html") 
            #devices=self.get_devices())

            return True

        return False
    
    def save(self, handler, data):

        try:
            data = json.loads(data)
            
            signal = HCSignal()
            signal.name = str(data["name"])
            signal.description = str(data["description"])
    
            for e in data["events"]:
                signal.add_event(HCEvent.from_json(e))     
                
            signal.sql_store(self.sql())
            self.sql_commit()
    
        except Exception, e:
            self.log_error(e)
            self.send_json_response(handler, str(e), 400)
            return

        self.send_json_response(handler, "ok")
    