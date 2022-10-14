import base64
import json
import urllib.request
import time

class server_info(object):
    def __init__(self, address, device_list):
        self.address = address
        self.start_time = time.time()
        self.device_list = device_list
        self.object_id_list = self.get_object_id_list()
        self._sensor_config = self.refresh_settings_config()
        self.extrnal_mqtt_config = self.init_external_mqtt_conf()
        self.__gateway_state = False
    def get_gateway_state(self):
        match self.__gateway_state:
            case True:
                return "OK"
            case False:
                return "ERROR"
    def reset_gateway_state(self):
        self.__gateway_state = False
    def set_gateway_online(self):
        self.__gateway_state = True
        
    def get_object_id_list(self):
        result_obj_id_list = []
        for i in self.device_list['devices']:
            if i['object_id'] not in result_obj_id_list:
                result_obj_id_list.append(i['object_id'])
        return result_obj_id_list
    def get_b64setting_payload(self):
        b_settings_str = bytes.fromhex(self._sensor_config['settings_str_hex'])
        b_arr_settings_str = bytearray()
        for i in range(0, 8):
            b_arr_settings_str.append(b_settings_str[i])
        return base64.b64decode(b_arr_settings_str).decode('ascii')
    def get_chirpstack_state(self):
        try:
            chirpstack_http_code = urllib.request.urlopen('http://' + self.address + ':8080')
            match chirpstack_http_code:
                case '200':
                    return "OK"
            return "ERROR"
        except:
            return "ERROR"
    def get_topic_status(self, object_id):
        return (f"/Gorizont/{self.extrnal_mqtt_config['object_code']}/{object_id}/"
                + f"{self.extrnal_mqtt_config['uspd_code']}/status_measure")
    def get_uspd_status_value(self):
        return f"Uptime: {int(time.time() - self.start_time)}\r\nGatway:{self.get_gateway_state()}\r\nChirpstack:{self.get_chirpstack_state()}"
    def init_external_mqtt_conf(self):
        with open("cfg/ExternalMqttConf.json") as descriptor:
            ext_mqtt_conf = json.load(descriptor)
        return ext_mqtt_conf
    def refresh_settings_config(self):
        with open("cfg/SensorConfig.json") as descriptor:
            sensor_conf = json.load(descriptor)
        self._sensor_config = sensor_conf
        require_update = self._sensor_config['update']
        if require_update:
            self._sensor_config['update'] = False
            with open("cfg/SensorConfig.json", 'w') as descriptor:
                json.dump(self._sensor_config, descriptor)
                
        return require_update # Bool
    def get_formatted_command(self, type):
        b_arr = bytearray()
        match type:
            case "settings":
                b_settings = bytes.fromhex(self._sensor_config['settings_str_hex'])
                b_arr = bytearray()
                for i in range(0, 8):
                    b_arr.append(b_settings[i])
                b64data = base64.encode(b_arr).decode('ascii')
            case "time":
                current_time = int(time.time())
                current_time_big = current_time.to_bytes(4, byteorder='big')
                b_arr.append(3)
                for i in range(0, 4):
                    b_arr.append(current_time_big[i])
                b64data = base64.b64encode(b_arr).decode('ascii') 
        return json.dumps({"confirmed": False, "fPort": 60, "data": b64data})
    

if __name__ == "__main__":
    with open('cfg/DeviceList.json','r') as f:
        dev_list = json.load(f)
    chirpstack_info = server_info('localhost', dev_list)
    for i in range(0, len(chirpstack_info.object_id_list)):
        print(chirpstack_info.get_topic_status(chirpstack_info.object_id_list[i]))
        print(chirpstack_info.get_uspd_status_value("OK"))






    # with open('SensorConfig.json', 'w') as descriptor:
        # json.dump(sensor_config, descriptor)