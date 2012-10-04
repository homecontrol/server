from homecontrol.plugin import Plugin
from bootstrap import Bootstrap
import homecontrol.signal, inspect

class Signal(Bootstrap):
    
    def handle_request(self, handler, method, path=None, args={}, data=None):
        """ HTTP wrapper for signal base class.
        
        Determines signal, function and their appropriate arguments from the 
        given URL invokes it within the appropriate context. The return data 
        of the appropriate method will be converted into JSON and added to the
        http response. 
        
        Example:
            Invoke a method of the signal base class within a signal context:
            http://localhost:4000/signal/<id>/<func>/<args>
            
            Note that if the method name starts with "sql_" prefix, a SQL 
            cursor will be added to the "sql" argument.
            
            Invoke a static method of the  signal base class: 
            http://localhost:4000/signal/<func>/<arg>
        """
        
        token = path.split("/")
        
        if len(token) < 2:
            self.log_error("Skip invalid path \"%s\"." % path)
            return False
        
        # Support missing signal id's e.g. for creating new signals.
        signal_id = None
        
        try:
            signal_id = int(token[1])
            method_name = token[2]
            token = token[2:]
        except ValueError:
            signal_id = None
            method_name = token[1]
            token = token[1:]
        
        # Load signal from database
        signal = homecontrol.signal.Signal
        if signal_id is not None:
            signal = homecontrol.signal.Signal.sql_load(self.sql(), signal_id)
        
        # Auto-add sql cursor if this is a sql method!
        if method_name.startswith("sql_") and "sql" not in args:
            args["sql"] = self.sql()
        
        if not hasattr(signal, method_name):
            self.log_error("No such method \"%s\"" % method_name)
            return False

        method = getattr(signal, method_name)
        if not callable(method):
            self.log_error("Method \"%s\" not callable" % method)
            return False
        
        if data != None:
            self.send_json_response(handler, method(data, **args))
            return True

        self.send_json_response(handler, method(**args))
        return True
    
    def view(self, handler, signal_id):

        signal = homecontrol.signal.Signal.sql_load(self.sql(), signal_id)
        self.send_html_response(
            handler=handler, 
            html_file="assets/html/index.html", 
            signal = signal)
                
        return True
        