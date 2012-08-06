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

            if obj.__class__.__name__ in ["HCEvent", "HCRFEvent", "HCIREvent"]:
                return obj.json_data
                        
            raise e