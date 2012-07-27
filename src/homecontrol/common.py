import json, logging as log

HC_VERSION = 1.0
HC_TYPE_RF = "rf"
HC_TYPE_IR = "ir"
HC_MAX_REQUEST_SIZE = 612

class HCEncoder(json.JSONEncoder):
    
    def default(self, obj):
                
        try:
            return json.JSONEncoder.default(self, obj)
        
        except TypeError, e:

            # Try to call encode method.
            if hasattr(obj, "json_encode"):
                return obj.json_encode()
                        
            raise e