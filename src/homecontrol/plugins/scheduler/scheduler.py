import sys
from bootstrap import Bootstrap
from homecontrol.event import Event
from homecontrol.signal import Signal

class Scheduler(Bootstrap):

    def handle_request(self, handler, method, path=None, args={}, data=None):

        if path == "/":
            self.send_html_response(
                handler=handler, 
                html_file="assets/html/index.html") 
            #devices=self.get_devices())

            return True

        return False
    
    def load_signals(self, handler, order_by = "name"):
        
        signals = Signal.sql_load(self.sql(), order_by=order_by)
        self.send_json_response(handler, signals)
    
    def save_signal(self, handler, data):

        try:
            
            signal = Signal.from_json(data)
            signal.sql_save(self.sql())
            self.sql_commit()
    
        except Exception, e:
            self.log_error(e)
            self.send_json_response(handler, str(e), 400)
            return

        self.send_json_response(handler, "ok")
    