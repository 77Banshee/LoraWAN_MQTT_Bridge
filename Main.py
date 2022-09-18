import os
import json
import MES_device
import MES_storage

#TODO: Append MES_storage in init_devices method and fill device collections.
#TODO: Init TkConfig.json and append quantity methods to every initialized Thermometer 

def init_devices(sourceJson):
    f = open(sourceJson, 'r')
    DeviceList = json.load(f)
    
    devArr = {}
    for i in range(0, len(DeviceList['devices'])):
        j_object = DeviceList['devices'][i]
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
        devArr.update({device_instance : 0}) 
    print(f"[*] Device created: {MES_device.device_factory.get_device_created()}")
    

def main():
    print("[*] Main called")
    init_devices("cfg/DeviceList.json")
    #INIT localMQTT and externalMQTT connections.
    #INIT DEVICES

if __name__ == "__main__":
    main()