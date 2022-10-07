import base64
import enum
import json
import queue
from re import I
import struct
import time
from xmlrpc.client import Boolean
#TODO: Проверить гигрометр.
#TODO: Округлить все значения float до двух символов после запятой?


# RSSI
# SNR
# Ubat
# Pbat
# Sost ???
# FwVer



class packet(object):
    def __init__(self, rx_json):
        self._dev_type = rx_json['applicationName']
        self._dev_eui = base64.b64decode(rx_json['devEUI']).hex()
        self._dev_name = rx_json['deviceName']
        self._f_cnt = rx_json['fCnt']
        self._hex_data = base64.b64decode(rx_json['data'])
        self._rssi = str(rx_json['rxInfo'][0]['rssi'])
        self._snr = str(rx_json['rxInfo'][0]['loRaSNR'])
    def __str__(self):
        return (f"dev_type: {self._dev_type}\n" 
        f"dev_eui: {self._dev_eui}\n"
        f"dev_name: {self._dev_name}\n"
        f"f_cnt: {self._f_cnt}\n"
        f"hex_data: {self._hex_data.hex()}\n"
        f"rssi: {self._rssi}\n"
        f"snr: {self._snr}")
    def get_hex_data(self):
        return self._hex_data
    def get_dev_eui(self):
        return self._dev_eui
    def get_dev_type(self):
        return self._dev_type
    def get_dev_name(self):
        return self._dev_name
    def get_packet_type(self):
        return self.__class__.__name__
    def __eq__(self, other):
        if isinstance(other, Boolean) or other == None:
            return False
        return self.get_hex_data() == other.get_hex_data()

class inclinometer_data_packet(packet):
    def __decode_measures(self, byte_hex_data):
        bArr_x = bytearray()
        bArr_y = bytearray()
        bArr_uts = bytearray()
        for i in range(0, 4):
            bArr_uts.append(byte_hex_data[i+1])
            bArr_x.append(byte_hex_data[8 - i])
            bArr_y. append(byte_hex_data[12 - i])
        [self.y_angle] = struct.unpack('f', bArr_y)
        [self.x_angle] = struct.unpack('f', bArr_x)
        self.timestamp = int.from_bytes(bArr_uts, 'big')
    def __init__(self, rx_json):
        super().__init__(rx_json)
        self.x_angle = None
        self.y_angle = None
        self.timestamp = None
        self.__decode_measures(self._hex_data)
    def __str__(self) -> str:
        return (super().__str__() 
                + '\n x_angle: ' 
                + '{0:.0f}'.format(self.x_angle) 
                + '\n y_angle: ' 
                + '{0:.0f}'.format(self.y_angle) 
                + f'\ntimestamp: {self.timestamp}'
                + f'\ndate: {time.ctime(self.timestamp)}') 
    
    

class thermometer_data_packet(packet):
    def __decode_measures(self, byte_hex_data):
        self.first_sensor = byte_hex_data[1]
        self.last_sensor = byte_hex_data[2]
        bArr_timestamp = bytearray()
        for i in range(3, 7):
            bArr_timestamp.append(byte_hex_data[i])
        self.timestamp = int.from_bytes(bArr_timestamp, 'big')
        measures_hex_data = self._hex_data[7:] # отрезаем первые 7 байт чтобы оставить только измерения.
        for i in range(self.first_sensor, self.last_sensor + 1):
            bMeasure = bytearray()
            bMeasure.append(measures_hex_data[0])
            bMeasure.append(measures_hex_data[1])
            measures_hex_data = measures_hex_data[2:]
            self.measures[i] = int.from_bytes(bMeasure, 'big', signed=True) / 100
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
        self.first_sensor = None
        self.last_sensor = None
        self.timestamp = None
        self.measures = {}
        self.stage = 0
        self.__decode_measures(self._hex_data)
        match self.first_sensor:
            case 1:
                self.stage = 1
            case 9:
                self.stage = 2
            case 17:
                self.stage = 3
            case 25:
                self.stage = 4
    def concat_measures(self):
        measures = ""
        for i in range(self.first_sensor, self.last_sensor + 1):
            measures += f"{self.measures.get(i)}\r\n"
        return measures
    def __str__(self) -> str:
        str_measures = ''
        for i in range(self.first_sensor, self.last_sensor + 1):
            str_measures += (f"\n{i}: {self.measures.get(i)}")
        return super().__str__() + str_measures
    

class piezometer_data_packet(packet): # 1b - type | 4b - tempo float | 4b - pressure float
    def __decode_measures(self, byte_hex_data):
        bArr_timestamp = bytearray()
        bArr_temperature = bytearray()
        bArr_pressure = bytearray()
        for i in range(0, 4):
            bArr_timestamp.append(byte_hex_data[i+1])
            bArr_temperature.append(byte_hex_data[i + 5])
            bArr_pressure.append(byte_hex_data[i + 9])
        self.timestamp = int.from_bytes(bArr_timestamp, 'big')
        self.measures_temperature = int.from_bytes(bArr_temperature, 'big')
        self.measures_pressure = int.from_bytes(bArr_pressure, 'big')
        self.measures_pressure = 222.35 + self.measures_pressure/10000
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
        self.timestamp = None
        self.measures_temperature = None
        self.measures_pressure = None
        self.__decode_measures(self._hex_data)
    def __str__(self) -> str:
        return (super().__str__() + f"\ntimestamp: {self.timestamp}" 
                + f"\nmeasures_temperature: {self.measures_temperature}" 
                + f"\nmeasures_pressure: {self.measures_pressure}")

class hygrometer_data_packet(packet): # 1b -type | 4b - unix time | 4b - tempo measures float | 4b relative humidity float
    def __decode_measures(self, byte_hex_data):
        bArr_timestamp = bytearray()
        bArr_temperature = bytearray()
        bArr_humidity = bytearray()
        for i in range(0, 4):
                bArr_timestamp.append(byte_hex_data[i + 1])
                bArr_temperature.append(byte_hex_data[8 - i])
                bArr_humidity.append(byte_hex_data[12 - i])
        self.timestamp = int.from_bytes(bArr_timestamp, 'big')        
        [self.measures_temperature] = struct.unpack('f', bArr_temperature)
        [self.measures_humidity] = struct.unpack('f', bArr_humidity)
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
        self.timestamp = None
        self.measures_temperature = None
        self.measures_humidity = None
        self.__decode_measures(self._hex_data)
    def __str__(self):
        return (super().__str__()
                + f"\ntimestamp: {self.timestamp}"
                + f"\nmeasures_temperature: {self.measures_temperature}"
                + f"\nmeasures_humidity: {self.measures_humidity}")

class battery_info_packet(packet):
    def __battery_info_decode(self, byte_hex_data):
        bArr_v_bat = bytearray()
        for i in range(0, 4):
            bArr_v_bat.append(byte_hex_data[4 - i])
        [self.u_battery] = struct.unpack('f', bArr_v_bat)
        self.u_battery = round(self.u_battery, 3) 
        self.battery_level = round(((self.u_battery - 3.0)/(3.6 - 3.0))*100.0)
    def __init__(self, rx_json):
        super().__init__(rx_json)
        self.battery_level = None
        self.u_battery = None
        self.__battery_info_decode(self._hex_data)
    def __str__(self) -> str:
        return (super().__str__() 
                + f"\nu_battery: {self.u_battery}"
                + f"\nbattery_level: {self.battery_level}" + "%")

class status_packet_info(packet):
    def __decode_status(self, byte_hex_data):
        self.error_code = str(byte_hex_data[1])
        self.protocol_version = str(byte_hex_data[4])
        self.firmmware_version = str(byte_hex_data[5]) + "." + str(byte_hex_data[6])
        self.device_version = str(byte_hex_data[7]) + str(byte_hex_data[8])
    def __init__(self, rx_json):
        super().__init__(rx_json)
        self.error_code = None
        self.protocol_version = None
        self.firmmware_version = None
        self.device_version = None
        self.__decode_status(self._hex_data)
    def __str__(self):
        return (super().__str__() 
                + f"\nerror_code: {self.error_code}"
                + f"\nprotocol_version: {self.protocol_version}"
                + f"\nfirmware_version: {self.firmmware_version}"
                + f"\ndevice_version: {self.device_version}")

class packet_factory(object):
    def __init__(self):
       self.__received_packet_history = []
       self.__measure_packet_types = []
       self.__status_packet_types = []
       self.__fill_packet_types() # TODO: CHECK!
    def __received_history_free(self):
        if len(self.__received_packet_history) >= 20:
            self.__received_packet_history.pop(0)
    def is_dublicate(self, packet):
        if packet in self.__received_packet_history:
            return True
        else:
            return False
    def __append_to_history(self, packet):
        if self.is_dublicate(packet):
            return False
        else:
            self.__received_packet_history.append(packet)
            self.__received_history_free()
            return True
    def create_packet(self, rx_json):
        hex_data = base64.b64decode(rx_json['data'])
        current_packet = None
        match hex_data[0]:
            case 0x11:
                current_packet = inclinometer_data_packet(rx_json)
            case 0x12:
                current_packet = status_packet_info(rx_json)
            case 0x13:
                current_packet = battery_info_packet(rx_json)
            case 0x05:
                current_packet =  thermometer_data_packet(rx_json)
            case 0x1b:
                current_packet =  piezometer_data_packet(rx_json)
                pass
            case 0x1a:
                current_packet = hygrometer_data_packet(rx_json)
            case 0x03:
                raise ValueError("Not implemented!")
                #TODO: IMPLEMENT!
        if self.__append_to_history(current_packet) != True:
            return False
        #TODO: CHECK FOR DUBLICATE
        return current_packet
    def __fill_packet_types(self):
        #fill measures
        self.__measure_packet_types.append(inclinometer_data_packet.__name__)
        self.__measure_packet_types.append(thermometer_data_packet.__name__)
        self.__measure_packet_types.append(piezometer_data_packet.__name__)
        self.__measure_packet_types.append(hygrometer_data_packet.__name__)
        #fill status
        self.__status_packet_types.append(status_packet_info.__name__)
        self.__status_packet_types.append(battery_info_packet.__name__)
    def is_measures(self, packet):
        return packet.get_packet_type() in self.__measure_packet_types
    def is_status(self, packet):
        return packet.get_packet_type() in self.__status_packet_types

if __name__ == "__main__":
    print("Entry point: MES_package_handler")
    # inc_11_o = open("debug/Inclinometer_07293314052DFF9E/11.txt", 'r')
    # rx_json = json.load(inc_11_o)
    # p = inclinometer_data_packet(rx_json)
    # print(p.__str__())
    
    # inc_12_o = open("debug/Inclinometer_07293314052DFF9E/12.txt", 'r')
    # rx_json = json.load(inc_12_o)
    # sp = status_packet_info(rx_json)
    # print(sp.__str__())


    # inc_13_o = open("debug/Thermometer_07293314052dff55/13.txt", 'r')
    # rx_json = json.load(inc_13_o)
    # p_bat = battery_info_packet(rx_json)
    # print(p_bat.__str__())

    # thermo_05_o = open("debug/thermo_07293314052d6646/5.json", 'r')
    # rx_json = json.load(thermo_05_o)
    # thermo = thermometer_data_packet(rx_json)
    # print(thermo.__str__())

    piez_1b_o = open("debug/piezometer_zap_07293314052d2ef0/3.json", 'r')
    rx_json = json.load(piez_1b_o)
    piez = piezometer_data_packet(rx_json)
    print(piez.__str__())