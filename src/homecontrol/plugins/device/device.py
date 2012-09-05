from homecontrol.plugin import HCPlugin

class Device(HCPlugin):
    
    def handle_request(self, handler, method, path=None, args={}, data=None):
        """ HTTP wrapper for device interface
        
        Determines device, function and their appropriate arguments from the 
        given URL e.g. device/dev_name/method_name/args and invokes them. The 
        return data of the appropriate method will be packed and added to the
        http response. 
        
        Example:
            Send radio tristate to configured device "dev1" using the URL: 
            http://localhost:4000/device/dev1/rf_send_tristate/fff0ff0fffff.
        """
        
        token = path.split("/")
        
        if len(token) < 3:
            self.log_error("Skip invalid path \"%s\"." % path)
            return False
        
        dev_name = token[1]
        method_name = token[2]
        
        # Search for device name in current devices
        device = None
        for d in self.get_devices():
            if d.name == dev_name:
                device = d
                break
            
        if device == None:
            self.log_error("No such device \"%s\"" % device);
            return False
            
        if not hasattr(device, method_name):
            self.log_error("No such method \"%s\"" % method_name)
            return False

        method = getattr(device, method_name)
        if not callable(method):
            self.log_error("Method \"%s\" not callable" % method)
            return False

        if data != None:
            self.send_json_response(handler, method(data, **args))
            return True

        self.send_json_response(handler, method(**args))
        return True