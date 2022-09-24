import base64
import json
import struct
#TODO: В классе пакет проинициализировать поля которые встречаются в каждом пакете.
#TODO: Продумать логику как определять пакет (по первому байту?) и сделать методы по созданию экземпляра конкретного пакета.

# RSSI
# SNR
# Ubat
# Pbat
# Sost ???
# FwVer

class packet_factory(object):
    pass    

class packet(object):
    def __init__(self, rx_json):
        self._dev_type = rx_json['applicationName']
        self._dev_eui = base64.b64decode(rx_json['devEUI'])
        self._dev_name = rx_json['deviceName']
        self._f_cnt = rx_json['fCnt']
        self._hex_data = base64.b85decode(rx_json['data'])
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

class inclinometer_data_packet(packet):
    def __decode_measures(self, str_hex_data):
        bArr_x = bytearray()
        bArr_y = bytearray()
        bArr_uts = bytearray()
        for i in range(0, 4):
            bArr_uts.append(str_hex_data[i+1])
            bArr_x.append(str_hex_data[8 - i])
            bArr_y.append(str_hex_data[12 - i])
        [self.x_angle] = struct.unpack('f', bArr_x)
        [self.y_angle] = struct.unpack('f', bArr_y)
        print('\tAng X: ' + '{0:.0f}'.format(self.x_angle))
        print('\tAng Y: ' + '{0:.0f}'.format(self.y_angle))
    def __init__(self, rx_json):
        super().__init__(rx_json)
        self.x_angle = None
        self.y_angle = None
        self.timesptamp = None
        self.__decode_measures(self._hex_data)
    def __str__(self) -> str:
        return super().__str__() + '\n x_angle: ' + '{0:.0f}'.format(self.x_angle) + '\n y_angle: ' + '{0:.0f}'.format(self.y_angle) 
    

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
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
    def __str__(self) -> str:
        return super().__str__()

class status_packet_info(packet):
    def __init__(self, rx_json):
        super().__init__(rx_json)
    def __str__(self):
        return super().__str__()

if __name__ == "__main__":
    print("Entry point: MES_package_handler")
    inc_11_o = open("debug/Inclinometer_07293314052DFF9E/11.txt", 'r')
    rx_json = json.load(inc_11_o)
    p = inclinometer_data_packet(rx_json)
    print(p.__str__())
