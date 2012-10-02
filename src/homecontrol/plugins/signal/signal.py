from homecontrol.plugin import Plugin
import homecontrol.signal, inspect

class Signal(Plugin):
    
    def handle_request(self, handler, method, path=None, args={}, data=None):
        """ HTTP wrapper for signal interface
        
        Determines signal, function and their appropriate arguments from the 
        given URL e.g. signal/id/method_name/args and invokes them. The 
        return data of the appropriate method will be packed and added to the
        http response. 
        
        Example:
            Deleting signal <id> can be invoked using the URL:
            http://localhost:40000/signal/<id>/delete.
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
        signal = None
        if signal_id is not None:
            signal = homecontrol.signal.Signal.sql_load(self.sql(), signal_id)
            
        if signal is None:
            self.log_warn("Not yet implement.");
            return True
        
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