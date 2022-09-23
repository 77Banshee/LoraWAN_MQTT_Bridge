import base64
import json
from operator import iconcat
from struct import pack
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
    def __init__(self, rx_json) -> None:
        self.dev_type = rx_json['applicationName']
        self.dev_eui = rx_json['devEUI']
        self.dev_name = rx_json['deviceName']
        self.f_cnt = rx_json['fCnt']
        self.hex_data = base64.b85decode(rx_json['data']).hex()
        self.rssi = rx_json['rxInfo']['rssi']
        self.snr = rx_json['rxInfo']['LoRaSNR']
    def __str__(self):
        return (f"dev_type: {self.dev_type}\n" 
        f"dev_eui: {self.dev_eui}\n"
        f"dev_name: {self.dev_name}\n"
        f"f_cnt: {self.f_cnt}\n"
        f"hex_data: {self.hex_data}\n"
        f"rssi: {self.rssi}\n"
        f"snr: {self.snr}")

class inclinometer_data_package(packet):
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
    def __str__(self) -> str:
        return super().__str__()

class thermometer_data_package(packet):
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
    def __str__(self) -> str:
        return super().__str__()

class piezometer_data_package(packet):
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
    def __str__(self) -> str:
        return super().__str__()

class hygrometer_data_package(packet):
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)

class battery_info_packet(packet):
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
    def __str__(self) -> str:
        return super().__str__()

if __name__ == "__main__":
    print("Entry point: MES_package_handler")
    inc_11_o = open("debug/Inclinometer_07293314052DFF9E/11.txt", 'r')
    rx_json = json.load(inc_11_o)
    print(str(rx_json['rxInfo']['rssi']))
    # p = packet(rx_json)
    # print(p.__str__())