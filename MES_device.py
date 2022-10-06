
from MES_packet_handler import battery_info_packet, status_packet_info


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
                return inclinometer(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
            case "Thermometer":
                cls.__count_increment(cls)
                return thermometer(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
            case "Pizeometer":
                cls.__count_increment(cls)
                return piezometer(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
            case "Hygrometer":
                cls.__count_increment(cls)
                return hygrometer(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
            case _:
                raise ValueError(f"Device not recognized: {type}")

class device(object):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        self._dev_eui = dev_eui.lower()
        self._mqtt_name = mqtt_name
        self._object_id = object_id
        self._object_code = object_code
        self._uspd_code = uspd_code
        self._dev_type = dev_type
        self._chirpstack_name = "UNKNOWN"
        self.measures = None
        self.sinfo = None
        self.sbat = None
        self.ready_to_send = False
    def get_devEui(self):
        return self._dev_eui
    def get_devType(self):
        return self._dev_type
    def get_mqtt_nqme(self):
        return self._mqtt_name
    def get_object_id(self):
        return self._object_id
    def get_object_code(self):
        return self._object_code
    def get_uspd_code(self):
        return self._uspd_code
    def set_chirpstack_name(self, chirpstack_name):
        self._chirpstack_name = chirpstack_name
    def __str__(self):
        return (f"Device: {self._dev_type}\n"
                f"Dev EUI: {self._dev_eui}\n"
                f"MQTT Name: {self._mqtt_name}\n"
                f"Object Code: {self._object_code}\n"
                f"USPD Code: {self._uspd_code}\n"
                f"Chirpstack Name: {self._chirpstack_name}")
    def __is_ready_or_not(self):
        return self.measures != None and self.sinfo != None and self.sbat != None
    def reset_packets(self):
        self.measures = None
        self.sinfo = None
        self.sbat = None
        self.ready_to_send = False
    def insert_measure_packet(self, packet):
        self.measures = packet
        self.ready_to_send = self.__is_ready_or_not()
    def insert_sbat_packet(self, packet):
        self.sbat = packet
        self.ready_to_send = self.__is_ready_or_not()
    def insert_sinfo_packet(self, packet):
        self.sinfo = packet
        self.ready_to_send = self.__is_ready_or_not()
    def insert_status_packet(self, packet):
        if status_packet_info.__name__ == packet.get_packet_type():
            self.insert_sinfo_packet(packet)
        elif battery_info_packet.__name__ == packet.get_packet_type():
            self.insert_sbat_packet(packet)
    def create_measure_topic(self):
        return (f"/Gorizont/{self._object_code}/{self._object_id}/{self._uspd_code}/" +
                f"{self._dev_type}/{self._object_id}_{self._mqtt_name}/from_device/measure")
    def create_status_topic(self):
        return (f"/Gorizont/{self._object_code}/{self._object_id}/{self._uspd_code}/" +
                f"/{self._dev_type}/{self._object_id}_{self._mqtt_name}/from_device/status")
    def fill_status(self):
        device_status = 1
        if self.sinfo.error_code != 0:
            device_status = 0
        return (f"DeviceName: {self._chirpstack_name}\r\n" +
                f"Ubat: {self.sbat.u_battery}\r\n" +
                f"Pbat: {self.sbat.battery_level}\r\n" +
                f"RSSI: {self.sbat._rssi}\r\n" +
                f"SINR: {self.sbat._snr}\r\n" +
                f"Sost: \r\n {device_status}" +
                f"FwVer: {self.sinfo.firmware_version}") 

class inclinometer(device):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        super().__init__(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
    def __str__(self):
        return super().__str__()
    
    def fill_measures(self):
        return f"{self.measures.timestamp}\r\n{self.measures.x_angle}\r\n{self.measures.y_angle}"
    

class thermometer(device):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        super().__init__(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
        self.__quantity = 0
        self.measures = {}
    def __is_ready_or_not(self):
        return (self.sbat != None) and (self.sinfo != None) and (None not in self.measures.values())
    def insert_measure_packet(self, packet):
        match packet.stage:
            case 1:
                self.measures['measures_1'] = packet
            case 2:
                self.measures['measures_2'] = packet
            case 3:
                self.measures['measures_3'] = packet
            case 4:
                self.measures['measures_4'] = packet
        self.ready_to_send = self.__is_ready_or_not()
    def get_quantity(self):
        return self.__quantity
    def set_quantity(self, value):
       self.__quantity = value
       self.__init_measure_container(value)
    def __init_measure_container(self, quantity):
        match quantity:
            case quantity if 1 <= quantity <= 8:
                containers = {"measures_1" : None} 
                self.measures.update(containers)
            case quantity if 9 <= quantity <= 16:
                containers = {"measures_1": None, "measures_2": None}
                self.measures.update(containers)
            case quantity if 17 <= quantity <= 24:
                containers = {"measures_1": None, "measures_2" : None, "measures_3": None}
                self.measures.update(containers)
            case quantity if 25 <= quantity <= 32:
                # ТАК НЕ БЫВАЕТ
                    raise ValueError()
    def __str__(self):
        return (super().__str__() 
                + f'\nQuantity: {self.__quantity}'
                + f'\nMeasures: {self.measures}'
                + f'\nsbat: {self.sbat}'
                + f'\nsinfo: {self.sinfo}')
    def fill_measures(self):
        # measure_topic_value = f"{self.measures.timestamp}\r\n{self.__quantity}\r\n"
        measures_array = list(self.measures.values())
        res = ""
        for i in range (0, len(measures_array)):
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            temp = measures_array[0].concat_measures()
            print(temp)
            res += measures_array[i].__str__()
        # print(x)
        # s = ", ".join(x)
        # for i in range(0, self.__quantity):
            # measure_topic_value += self.measures[i].values()
    
    
    
class piezometer(device):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        super().__init__(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
    def __str__(self):
        return super().__str__()
    
class hygrometer(device):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        super().__init__(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
    def __str__(self):
        return super().__str__()
        
if __name__ == "__main__":
   pass 

#Inclinometer init example
#dev_1 = device_factory.create_device("07293314052D0EED", "i1.1", "10000089", "MRY", "U0042", "Inclinometer")