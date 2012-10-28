import json, logging as log

HC_VERSION = 1.0
HC_TYPE_RF = "rf"
HC_TYPE_IR = "ir"
HC_MAX_REQUEST_SIZE = 612

class JSONEncoder(json.JSONEncoder):
    
    def default(self, obj):
                
        try:
            return json.JSONEncoder.default(self, obj)
        
        except TypeError, e:
            
            if "to_json" in dir(obj):
                return json.loads(obj.to_json())
            
            log.error("Missing required method to_json() in class %s." % type(obj))
            raise e
        
def get_value(data, name, converter = None, optional = False):
    
    if name not in data or data[name] == None:
        if optional == False:
            raise Exception("Missing non-optional attribute \"%s\"." % name)
        return None
    
    if data[name] == "":
        return None
    
    value = data[name]
    if converter != None:
        value = converter(value)
    
    return value