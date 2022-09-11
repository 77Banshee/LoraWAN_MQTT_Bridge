import sys

class device(object):
    dev_eui = None
    mqtt_name = None
    object_id = None
    object_code = None
    uspd_code = None
    def initialize_device(type):
        match type:
            case "Incinometer":
                pass
            case "Thermometer":
                pass
            case "Pizeometer":
                pass
            case "Hygrometer":
                pass
            case _:
                raise ValueError(f"Device not recognized: {type}")
            
    def __init__(self, dev_eui, mqtt_name, object_id, object_code, uspd_code, type):
        self.dev_eui = dev_eui
        self.mqtt_name = mqtt_name
        self.object_id = object_id
        self.object_code = object_code
        self.uspd_code = uspd_code
        self.type = type
    def get_devEui(self):
        return self.dev_eui
    def get_devType(self):
        return self.type


class inclinometer(device):
    def __init__(self):
        pass
    #S_BAT
    #S_INFO
    #MEASURES   

class thermometer(device):
    def __init__(self):
        pass
    #S_BAT
    #S_INFO
    #MEASURES x3
    
class piezometer(device):
    def __init__():
        pass
    #S_BAT
    #S_INFO
    #MEASURES
    
class hygrometer(device):
    def __init__():
        pass
    #S_BAT
    #S_INFO
    #MEASURES