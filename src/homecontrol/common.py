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
                return obj.to_json
                        
            raise e