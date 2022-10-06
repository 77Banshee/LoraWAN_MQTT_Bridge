import sys
import json
import MES_device
import MES_storage
import MES_packet_handler
import paho.mqtt.client as mqtt
import base64

    # TODO:  Продумать логину как пушить пакет после того как прешли все. 
        # TODO: (Сделать очередь для пуша как у горизонта?) (Сделать класс Mqtt_Topic? На вход подавать конкретный экземпляр класса, предварительно проверив ready_to_send)
    
    # TODO: -- Пакет пришел CHECK > Достали устройство CHECK > Обработали пакет CHECK > Добавили в устройство CHECK > В мейне тут же проверили ready_to_send, если вернул True CHECK > Сделали два топика
        #TODO:  (mqtt_topic [measures, status]) > Запихиваем в очередь которая проверяется в бесконечном цикле и сразу чистим девайс.

    #TODO: Create mqtt object class
# TODO: Addittional
    # TODO: CSV
    # TODO: Chirpstack and gateway status
    # TODO: GPIO
    # TODO: MAKE PROPER COMMENTARIES!!
    # TODO: check that we getting values from accesors and mutators

#   --Arguments
host = 'localhost'
port = '1883'
args = sys.argv
if (len(args) > 1):
    host = args[1]

#   --Init instances
device_storage = MES_storage.devices()
packet_factory = MES_packet_handler.packet_factory()
local_mqtt_client = mqtt.Client(reconnect_on_failure=True)
external_mqtt_client = mqtt.Client(reconnect_on_failure=True)

#   --MQTT
def on_message(client, userdata, msg):
    if msg.topic.endswith("/event/up") and msg.topic.startswith("application"):  
        # Get device info
        rx_json = json.loads(msg.payload)
        rx_dev_eui = base64.b64decode(rx_json['devEUI']).hex()
        rx_dev_type = rx_json['type']
        # Get device
        rx_device = device_storage.get_device(rx_dev_eui, rx_dev_type)
        if rx_device == False:
            raise ValueError("Device not found in storage!")
        rx_device.set_chirpstack_name(rx_json['deviceName'])
        # Handle packet
        rx_packet = packet_factory.create_packet(rx_json)
        # Insert packet into device
        if packet_factory.is_measures(rx_packet):
            rx_device.insert_measure_packet(rx_packet)
        elif packet_factory.is_status(rx_packet):
            rx_device.insert_status_packet(rx_packet)
        # Check ready state.
         # Push?
        #TODO: Check ready statement and push data to mqtt
        #TODO: RESET PACKETS IN DEVICE!!
        
        
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[*] Server: {host} connected.")
    else:
        raise ConnectionError("!!! Server is unavailable !!")
    #TODO: Implement
    pass

#   --Functions
def init_devices(json_device_list, json_tk_config):
    """Создание экземпляро каждого устройства на обьекте. Добавление их в MES_storage.devices"""
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
    print("[*] Bridge server start...")
    init_devices("cfg/DeviceList.json", "cfg/TkConfig.json")
    local_mqtt_client.connect(host, port)
    local_mqtt_client.subscribe('application/+/device/+/event/up', qos=2)
    local_mqtt_client.subscribe('gateway/+/event/#', qos=2)
    local_mqtt_client.on_connect = on_connect
    local_mqtt_client.on_message = on_message
    # TODO: local_mqtt_client.subscribe() implement for check gateway status and switch gateway status flag
    local_mqtt_client.loop_start()
    external_mqtt_client.connect(host, port)
    external_mqtt_client.loop_start()
    print("[*] Device initialized: TODO COUNT")
    

def debug():
    init_devices("cfg/DeviceList.json", "cfg/TkConfig.json")
    for i in range(0, 6):
        if i == 0:
            rx_json = open("debug/thermometer_usnk_07293314052dff55_usnk/1.txt",'r')
        if i == 1:
            rx_json = open("debug/thermometer_usnk_07293314052dff55_usnk/2.txt",'r')
        if i == 2:
            rx_json = open("debug/thermometer_usnk_07293314052dff55_usnk/3.txt",'r')
        if i == 3:
            rx_json = open("debug/thermometer_usnk_07293314052dff55_usnk/4.txt",'r')
        if i == 4:
            rx_json = open("debug/thermometer_usnk_07293314052dff55_usnk/5.txt",'r')
        if i == 5:
            rx_json = open("debug/thermometer_usnk_07293314052dff55_usnk/6.txt",'r')
        rx_json = json.load(rx_json)
        ## COPY FROM HERE
        rx_dev_eui = base64.b64decode(rx_json['devEUI']).hex()
        rx_dev_type = rx_json['applicationName']
        # Get device
        rx_device = device_storage.get_device(rx_dev_eui, rx_dev_type)
        if rx_device == False:
            raise ValueError("Device not found in storage!")
        rx_device.set_chirpstack_name(rx_json['deviceName'])
        # Handle packet
        rx_packet = packet_factory.create_packet(rx_json)
        if rx_packet == False:
            print("Packet is discarded.")
            continue
        # Insert packet into device
        if packet_factory.is_measures(rx_packet):
            rx_device.insert_measure_packet(rx_packet)
        elif packet_factory.is_status(rx_packet):
            rx_device.insert_status_packet(rx_packet)
        print("--DEBUG", rx_device.ready_to_send)
    print(rx_device.fill_measures())
    print("Done!")
        # TODO: RESET PACKETS!
        # TODO: PUSH TO Queue
        # TODO: Grab from queue and push to mqtt
    # Thermometer debug
    # packet_factory = MES_packet_handler.packet_factory()
    # thermo1 = device_storage.get_device('07293314052def1c'.lower(), 'Thermometer')
    # f1 = open("debug/thermo_07293314052d6646/1.json", 'r')
    # j1 = json.load(f1)
    # pack_1 = MES_packet_handler.battery_info_packet(j1)
    # f2 = open("debug/thermo_07293314052d6646/2.json", 'r')
    # j2 = json.load(f2) 
    # pack_2 = MES_packet_handler.status_packet_info(j2)
    # f3 = open("debug/thermo_07293314052d6646/3.json", 'r')
    # j3 = json.load(f3)
    # pack_3 = MES_packet_handler.thermometer_data_packet(j3)
    # f4 = open("debug/thermo_07293314052d6646/4.json", 'r')
    # j4 = json.load(f4)
    # pack_4 = MES_packet_handler.thermometer_data_packet(j4)
    # f4 = open("debug/thermo_07293314052d6646/5.json", 'r')
    # j4 = json.load(f4)
    # pack_5 = MES_packet_handler.thermometer_data_packet(j4)
    # thermo1.insert_sbat_packet(pack_1)
    # thermo1.insert_sinfo_packet(pack_2)
    # thermo1.insert_measure_packet(pack_3)
    # thermo1.insert_measure_packet(pack_4)
    # thermo1.insert_measure_packet(pack_5)

    # Inclinometer debug
    # inc = device_storage.get_device("07293314052DFF9E".lower(), 'Inclinometer')
    # inc_f1 = open("debug/Inclinometer_07293314052DFF9E/11.txt",'r')
    # inc_j1 = json.load(inc_f1)
    # inc_f2 = open("debug/Inclinometer_07293314052DFF9E/12.txt",'r')
    # inc_j2 = json.load(inc_f2)
    # inc_f3 = open("debug/Inclinometer_07293314052DFF9E/13.txt",'r')
    # inc_j3 = json.load(inc_f3)
    # sbat = MES_packet_handler.battery_info_packet(inc_j3)
    # sinfo = MES_packet_handler.status_packet_info(inc_j2)
    # measures = MES_packet_handler.inclinometer_data_packet(inc_j1)
    # inc.insert_measure_packet(measures)
    # inc.insert_sbat_packet(sbat)
    # inc.insert_sinfo_packet(sinfo)

    # piezometer debug
    # piez = MES_device.piezometer("07293314052d2ef0", "mqname", "Piezometer", "o_id999", "code1", "uspd_99")
    # pack_12_o = open('debug/piezometer_zap_07293314052d2ef0/12.json') 
    # pack_13_o = open('debug/piezometer_zap_07293314052d2ef0/13.json') 
    # pack_1b_1_o = open('debug/piezometer_zap_07293314052d2ef0/1b_1.json') 
    # j12 = json.load(pack_12_o)
    # j13 = json.load(pack_13_o)
    # j1b = json.load(pack_1b_1_o)
    # sbat = MES_packet_handler.battery_info_packet(j13)
    # sinfo = MES_packet_handler.status_packet_info(j12)
    # piez_meas = MES_packet_handler.piezometer_data_packet(j1b)
    # piez.insert_measure_packet(piez_meas)
    # piez.insert_sbat_packet(sbat)
    # piez.insert_sinfo_packet(sinfo)

    # pack_1b_2_o = open('debug/piezometer_zap_07293314052d2ef0/1b_2.json') 
    # pack_1b_3_o = open('debug/piezometer_zap_07293314052d2ef0/1b_3.json') 
    pass
if __name__ == "__main__":
    # main()
    debug()