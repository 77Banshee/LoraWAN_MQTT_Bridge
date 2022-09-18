
import json
from select import select


class device_factory(object):
    __device_created = 0
  
    @staticmethod
    def __count_increment(cls): 
        cls.__device_created += 1
    
    @classmethod 
    def get_device_created(cls):
        return cls.__device_created
    
    @classmethod
    def create_device(cls, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        match dev_type:
            case "Inclinometer":
                cls.__count_increment(cls)
                return inclinometer(dev_eui, mqtt_name, object_id, object_code, uspd_code, dev_type)
            case "Thermometer":
                cls.__count_increment(cls)
                return thermometer(dev_eui, mqtt_name, object_id, object_code, uspd_code, dev_type)
            case "Pizeometer":
                cls.__count_increment(cls)
                return piezometer(dev_eui, mqtt_name, object_id, object_code, uspd_code, dev_type)
            case "Hygrometer":
                cls.__count_increment(cls)
                return hygrometer(dev_eui, mqtt_name, object_id, object_code, uspd_code, dev_type)
            case _:
                raise ValueError(f"Device not recognized: {type}")
        #Get dev info from ... json/straight params?

class device(object):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        self.__dev_eui = dev_eui
        self.__mqtt_name = mqtt_name
        self.__object_id = object_id
        self.__object_code = object_code
        self.__uspd_code = uspd_code
        self.__dev_type = dev_type
        self.__chirpstack_name = "UNKNOWN"
    def get_devEui(self):
        return self.__dev_eui
    def get_devType(self):
        return self.__dev_type
    def get_mqtt_nqme(self):
        return self.__mqtt_name
    def get_object_id(self):
        return self.__object_id
    def get_object_code(self):
        return self.__object_code
    def get_uspd_code(self):
        return self.__uspd_code
    def __str__(self):
        return f"Device: {self.__dev_type}\nDev EUI: {self.__dev_eui}\nMQTT Name: {self.__mqtt_name}\nObject Code: {self.__object_code}\nUSPD Code: {self.__uspd_code}\nChirpstack Name: {self.__chirpstack_name}"

       
class inclinometer(device):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        super().__init__(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
    def __str__(self):
        return super().__str__()
    #S_BAT
    #S_INFO
    #MEASURES   

class thermometer(device):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        super().__init__(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
        self.__quantity = 0
    def get_quantity(self):
        return self.__quantity
    def set_quantity(self, value):
       self.__quantity = value
    def __str__(self):
        return super().__str__()
    #@property
    #def quantity(self):
    #    return self.quantity
    #@quantity.setter
    #def set_quantity(self, quantity):
    #    self.quantity = quantity
    #S_BAT
    #S_INFO
    #MEASURES x3
    
class piezometer(device):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        super().__init__(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
    def __str__(self):
        return super().__str__()
    #S_BAT
    #S_INFO
    #MEASURES
    
class hygrometer(device):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        super().__init__(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
    def __str__(self):
        return super().__str__()
    #S_BAT
    #S_INFO
    #MEASURES

if __name__ == "__main__":
   pass 

#Inclinometer init example
#dev_1 = device_factory.create_device("07293314052D0EED", "i1.1", "10000089", "MRY", "U0042", "Inclinometer")