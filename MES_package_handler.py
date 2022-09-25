import base64
import enum
import json
import struct
import time
#TODO: В классе пакет проинициализировать поля которые встречаются в каждом пакете.
#TODO: Продумать логику как определять пакет (по первому байту?) и сделать методы по созданию экземпляра конкретного пакета.
#TODO: Продумать как отбрасывать дубликаты пакетов (где хранить последние 20 пришедших пакетов? в мейне? в packet_factory?).

# RSSI
# SNR
# Ubat
# Pbat
# Sost ???
# FwVer

class device_error_code(enum.Enum):
    no_error = "00"
    no_respone = "01"
    power_overload = "02"
    low_voltage = "03"
    thermometer_elctro_leak = "04"
    thermometer_error_scan = "05"
    thermometer_is_missing = "06"
    error_1wire = "07"
    calibration_data_error = "08"
    thermosensor_is_missing = "09"
    thermometer_is_too_long = "10"
    queue_overflow = "20"
    clock_chip_damaged = "30"

class packet_factory(object):
    pass    

class packet(object):
    def __init__(self, rx_json):
        self._dev_type = rx_json['applicationName']
        self._dev_eui = base64.b64decode(rx_json['devEUI'])
        self._dev_name = rx_json['deviceName']
        self._f_cnt = rx_json['fCnt']
        self._hex_data = base64.b64decode(rx_json['data'])
        self._rssi = str(rx_json['rxInfo'][0]['rssi'])
        self._snr = str(rx_json['rxInfo'][0]['loRaSNR'])
    def __str__(self):
        return (f"dev_type: {self._dev_type}\n" 
        f"dev_eui: {self._dev_eui.hex()}\n"
        f"dev_name: {self._dev_name}\n"
        f"f_cnt: {self._f_cnt}\n"
        f"hex_data: {self._hex_data.hex()}\n"
        f"rssi: {self._rssi}\n"
        f"snr: {self._snr}")
    def get_hex_data(self):
        return self._hex_data

class inclinometer_data_packet(packet):
    def __decode_measures(self, str_hex_data):
        bArr_x = bytearray()
        bArr_y = bytearray()
        bArr_uts = bytearray()
        for i in range(0, 4):
            bArr_uts.append(str_hex_data[i+1])
            bArr_x.append(str_hex_data[8 - i])
            bArr_y. append(str_hex_data[12 - i])
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
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
    def __str__(self) -> str:
        return super().__str__()

class piezometer_data_packet(packet):
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
    def __str__(self) -> str:
        return super().__str__()

class hygrometer_data_packet(packet):
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)

class battery_info_packet(packet):
    def __battery_info_decode(self, str_hex_data):
        bArr_v_bat = bytearray()
        for i in range(0, 4):
            bArr_v_bat.append(str_hex_data[4 - i])
        [self.u_battery] = struct.unpack('f', bArr_v_bat)
        self.battery_level = round(((self.u_battery - 3.0)/(3.6 - 3.0))*100.0)
        print("1") 
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
    def __decode_status(self, str_hex_data):
        self.error_code = str(str_hex_data[1])
        self.protocol_version = str(str_hex_data[4])
        self.firmmware_version = str(str_hex_data[5]) + "." + str(str_hex_data[6])
        self.device_version = str(str_hex_data[7]) + str(str_hex_data[8])
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


    inc_13_o = open("debug/Thermometer_07293314052dff55/13.txt", 'r')
    rx_json = json.load(inc_13_o)
    p_bat = battery_info_packet(rx_json)
    print(p_bat.__str__())