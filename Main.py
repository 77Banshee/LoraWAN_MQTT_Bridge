import os
import json
import MES_device
import MES_storage

#TODO: Make Package classes
#TODO: Create feature for pass data.json files as args
#TODO: Fill chirpstack name with value from mqtt topic.

device_storage = MES_storage.devices()

# Создание экземпляро каждого устройства на обьекте.
def init_devices(json_device_list, json_tk_config):
    dev_list_file = open(json_device_list, 'r')
    device_list = json.load(dev_list_file)
    
    tk_config_file = open(json_tk_config)
    tk_config = json.load(tk_config_file)
    
    for i in range(0, len(device_list['devices'])):
        j_object = device_list['devices'][i]
        dev_eui = j_object['devEui'] 
        dev_mqtt_name = j_object['MqttName']
        dev_type = j_object['type']
        dev_object_id = j_object['object_id']
        dev_object_code = j_object['object_code'] 
        dev_uspd_code = j_object['uspd_code']
        device_instance = MES_device.device_factory.create_device(dev_eui, 
                                                                  dev_mqtt_name,
                                                                  dev_type,
                                                                  dev_object_id,
                                                                  dev_object_code,
                                                                  dev_uspd_code)
        if dev_type == 'Thermometer':
            for i in tk_config['TK']:
                if i['DevEUI'] == dev_eui:
                    device_instance.set_quantity(i['Quantity'])
        MES_storage.devices.append_device(device_storage, device_instance)

def main():
    print("[*] Main called")
    init_devices("cfg/DeviceList.json", "cfg/TkConfig.json")
    #INIT localMQTT and externalMQTT connections.
    #INIT DEVICES

if __name__ == "__main__":
    main()