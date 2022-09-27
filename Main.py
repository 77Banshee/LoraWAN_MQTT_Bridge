import os
import json
import MES_device
import MES_storage
import MES_packet_handler

#TODO: Make Package classes
#TODO: Create feature for pass data.json files as args
#TODO: Fill chirpstack name with value from mqtt topic.

device_storage = MES_storage.devices()
packet_factory = MES_packet_handler.packet_factory()


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
                    break
        MES_storage.devices.append_device(device_storage, device_instance)

def main():
    print("[*] Main called")
    init_devices("cfg/DeviceList.json", "cfg/TkConfig.json")

    
    # Получаем json из mqtt
    
    
    
    #INIT localMQTT and externalMQTT connections.
    #INIT DEVICES

def debug():
    init_devices("cfg/DeviceList.json", "cfg/TkConfig.json")
    packet_factory = MES_packet_handler.packet_factory()
    
    thermo1 = device_storage.get_device('07293314052def1c'.lower(), 'Thermometer')

    f1 = open("debug/thermo_07293314052d6646/1.json", 'r')
    j1 = json.load(f1)
    pack_1 = MES_packet_handler.battery_info_packet(j1)
    
    f2 = open("debug/thermo_07293314052d6646/2.json", 'r')
    j2 = json.load(f2) 
    pack_2 = MES_packet_handler.status_packet_info(j2)

    f3 = open("debug/thermo_07293314052d6646/3.json", 'r')
    j3 = json.load(f3)
    pack_3 = MES_packet_handler.thermometer_data_packet(j3)

    f4 = open("debug/thermo_07293314052d6646/4.json", 'r')
    j4 = json.load(f4)
    pack_4 = MES_packet_handler.thermometer_data_packet(j4)

    f4 = open("debug/thermo_07293314052d6646/5.json", 'r')
    j4 = json.load(f4)
    pack_5 = MES_packet_handler.thermometer_data_packet(j4)



    thermo1.insert_sbat_packet(pack_1)
    thermo1.insert_sinfo_packet(pack_2)
    thermo1.insert_measure_packet(pack_3)
    thermo1.insert_measure_packet(pack_4)
    thermo1.insert_measure_packet(pack_5)

    inc = device_storage.get_device("07293314052DFF9E".lower(), 'Inclinometer')
    
    inc_f1 = open("debug/Inclinometer_07293314052DFF9E/11.txt",'r')
    inc_j1 = json.load(inc_f1)
    inc_f2 = open("debug/Inclinometer_07293314052DFF9E/12.txt",'r')
    inc_j2 = json.load(inc_f2)
    inc_f3 = open("debug/Inclinometer_07293314052DFF9E/13.txt",'r')
    inc_j3 = json.load(inc_f3)

    sbat = MES_packet_handler.battery_info_packet(inc_j3)
    sinfo = MES_packet_handler.status_packet_info(inc_j2)
    measures = MES_packet_handler.inclinometer_data_packet(inc_j1)
    
    
    inc.insert_measure_packet(measures)
    inc.insert_sbat_packet(sbat)
    inc.insert_sinfo_packet(sinfo)
    print()
if __name__ == "__main__":
    # main()
    debug()