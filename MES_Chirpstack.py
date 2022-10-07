import base64
import json
import urllib

class server_info():
    def __init__(self, address, device_list) -> None:
        with open("cfg/SensorConfig.json") as descriptor:
            self.sensor_config = json.load(descriptor)
        with open("cfg/ExternalMqttConf.json") as descriptor:
            self.mqtt_config = json.load(descriptor)
        self.settings_dict = {"confirmed": False,
                                    "fPort": 60,
                                    "data": 0}
        self.address = address
        self.uptime = 0 # TODO: MAKE THIS VALUE UPDATE
        self.device_list = device_list
    def get_b64setting_payload(self):
        b_settings_str = bytes.fromhex(self.sensor_config['settings_str_hex'])
        b_arr_settings_str = bytearray()
        for i in range(0, 8):
            b_arr_settings_str.append(b_settings_str[i])
        return base64.b64decode(b_arr_settings_str).decode('ascii')
    def get_chirpstack_state(self):
        chirpstack_http_code = urllib.request.urlopen('http://' + self.address + ':8080')
        match chirpstack_http_code:
            case '200':
                return "OK"
        return "ERROR"
    def get_topic_status(self):
        return f"/Gorizont/{self.mqtt_config['object_code']}/" #TODO: APPEND OBJECT LIST!!!!!
    def get_status_values():
        pass







    # with open('SensorConfig.json', 'w') as descriptor:
        # json.dump(sensor_config, descriptor)