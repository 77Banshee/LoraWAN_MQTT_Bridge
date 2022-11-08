import enum
import time
import MES_packet_handler

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
            case "Piezometer":
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
        self._status_is_ready = False
        self.ready_to_send = False
        self._require_time_update = False
        self._require_setting_update = False
    def check_status_state(self):
        self._status_is_ready = self.sinfo != None and self.sbat != None
    def get_status_state(self):
        return self._status_is_ready
    def is_correct_time(self, timestamp): # Check time offset
        if abs(timestamp - (int(time.time()))) > 300: # for simatic 
            print(f"Time difference for {self._dev_type} {self._dev_eui}: {timestamp - (int(time.time()))}")
            self._require_time_update = True
            return False
        return True
    def is_require_time_update(self):
        return self._require_time_update
    def set_require_time_update(self):
        self._require_time_update = True
    def reset_require_time_update(self):
        self._require_time_update = False
    def is_require_settings_update(self):
        return self._require_setting_update
    def set_require_settings_update(self):
        self._require_setting_update = True
    def reset_require_settings_update(self):
        self._require_setting_update = False
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
    def get_chirpstack_name(self):
        return self._chirpstack_name
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
    # Insert packet that and check for ready_to_send state.
    def insert_measure_packet(self, packet, timestamp): 
        self.measures = packet
        if self.is_correct_time(timestamp):
            print(f"Time offset detected for: {self._dev_type} {self._dev_eui} {self._chirpstack_name}")
            self.set_require_time_update()
        self.ready_to_send = self.__is_ready_or_not()
    def insert_sbat_packet(self, packet):
        self.sbat = packet
        self.ready_to_send = self.__is_ready_or_not()
    def insert_sinfo_packet(self, packet):
        self.sinfo = packet
        self.ready_to_send = self.__is_ready_or_not()
    def insert_status_packet(self, packet):
        if MES_packet_handler.status_info_packet.__name__ == packet.get_packet_type():
            self.insert_sinfo_packet(packet)
        elif MES_packet_handler.battery_info_packet.__name__ == packet.get_packet_type():
            self.insert_sbat_packet(packet)
        self.check_status_state()
    # Mqtt topic createion
    def create_measure_topic(self):
        return (f"__/Gorizont/{self._object_code}/{self._object_id}/{self._uspd_code}/" + #TODO: TEST TOPIC!
                f"{self._dev_type}/{self._object_id}_{self._mqtt_name}/from_device/measure")
    def create_status_topic(self):
        return (f"__/Gorizont/{self._object_code}/{self._object_id}/{self._uspd_code}/" + #TODO: TEST TOPIC!
                f"{self._dev_type}/{self._object_id}_{self._mqtt_name}/from_device/status")
    def get_formatted_status(self):
        if self.sinfo.error_code == device_error_code.no_error.value:
            device_status = 1
        else:
            device_status = 0
            # TODO: PLACE TELEGRAM BOT NOTIFICATION HERE
        return (f"DeviceName:{self._chirpstack_name}\r\n" +
                f"Ubat:{self.sbat.u_battery}\r\n" +
                f"Pbat:{self.sbat.battery_level}\r\n" +
                f"RSSI:{self.sbat._rssi}\r\n" +
                f"SINR:{self.sbat._snr}\r\n" +
                f"Sost:{device_status}\r\n" +
                f"FwVer:{self.sinfo.firmmware_version}") 

class inclinometer(device):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        super().__init__(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
    def __str__(self):
        return super().__str__()
    def get_formatted_measures(self):
        return f"{self.measures.timestamp}\r\n{self.measures.x_angle}\r\n{self.measures.y_angle}"

class thermometer(device):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        super().__init__(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
        self.__quantity = 0
        self.measures = {}
    def __is_ready_or_not(self):
        return (self.sbat != None) and (self.sinfo != None) and (None not in self.measures.values())
    def insert_measure_packet(self, packet, timestamp):
        match packet.stage:
            case 1:
                self.measures['measures_1'] = packet
                if self.is_correct_time(timestamp):
                    print(f"Time offset detected for: {self._dev_type} {self._dev_eui} {self._chirpstack_name}")
                self.set_require_time_update()
            case 2:
                self.measures['measures_2'] = packet
            case 3:
                self.measures['measures_3'] = packet
            case 4:
                self.measures['measures_4'] = packet
        self.ready_to_send = self.__is_ready_or_not()
    def reset_packets(self):
        self.measures = {}
        self.sinfo = None
        self.sbat = None
        self.ready_to_send = False   
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
                containers = {"measures_1": None, "measures_2": None, "measures_3": None, "measures_4": None}
                self.measures.update(containers)             
    def __str__(self):
        return (super().__str__() 
                + f'\nQuantity: {self.__quantity}'
                + f'\nMeasures: {self.measures}'
                + f'\nsbat: {self.sbat}'
                + f'\nsinfo: {self.sinfo}')
    def get_formatted_measures(self):
        measures_array = list(self.measures.values())
        if measures_array.count == 0:
            return
        measure_topic_value = f"{measures_array[-1].timestamp}\r\n{self.__quantity}\r\n"
        for i in range (0, len(measures_array)):
            measure_topic_value += measures_array[i].concat_measures()
        return measure_topic_value
    
class piezometer(device):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        super().__init__(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
    def __str__(self):
        return super().__str__()
    def get_formatted_measures(self):
        return f"{self.measures.timestamp}\r\n{self.measures.measures_pressure}"
    
class hygrometer(device):
    def __init__(self, dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code):
        super().__init__(dev_eui, mqtt_name, dev_type, object_id, object_code, uspd_code)
    def __str__(self):
        return super().__str__()
    def get_formatted_measures(self):
        return f"{self.measures.timestamp}\r\n{self.measures.measures_temperature}\r\n{self.measures.measures_humidity}"
        
class device_error_code(enum.Enum):
    no_error = "0"
    sensor_not_respond = "1"
    power_overload = "2"
    low_voltage = "3"
    thermometer_elctro_leak = "4"
    thermometer_error_scan = "5"
    thermometer_is_missing = "6"
    error_1wire = "7"
    calibration_data_error = "8"
    thermosensor_is_missing = "9"
    thermometer_is_too_long = "10"
    queue_overflow = "20"
    clock_chip_damaged = "30"       
if __name__ == "__main__":
   pass 