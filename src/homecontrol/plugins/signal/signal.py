from homecontrol.plugin import Plugin
from bootstrap import Bootstrap
import homecontrol.signal, inspect

class Signal(Bootstrap):
    
    def view(self, handler, signal_id):

        signal = homecontrol.signal.Signal.sql_load(self.sql(), signal_id)
        self.send_html_response(
            handler=handler, 
            html_file="assets/html/index.html", 
            html_form_data = {"signal-device": signal.dev_name},
            signal = signal,
            devices = self.get_devices())