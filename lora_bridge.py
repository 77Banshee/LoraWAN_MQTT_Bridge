import sys, os
if '-gpio' in sys.argv:
    import MES_gpio
    pass
import json
from MES_data_logger import device_logger
import MES_device
import MES_storage
import MES_packet_handler
import MES_server
import paho.mqtt.client as mqtt
import base64
import time
import datetime

# Map
# -- Пакет пришел CHECK > Достали устройство CHECK > Обработали пакет CHECK > 
#    Добавили в устройство CHECK > 
#    В мейне тут же проверили ready_to_send, если вернул True CHECK > 
#    Дулаем топики CHECK > Запихиваем в очередь которая проверяется в бесконечном цикле CHECK> и сразу чистим девайс CHECK.

## TODO: Debug
    # Remove TEST prefix from ExternalMqttConf
    # Remove __ prefix in MES_device.device func create_measure_topic and create_status_topic

# TODO: Devices
    # Test hygrometer
    # Add flag status_has_sent and check for avoid double status topic publish
    
# TODO: Addittional
    # TODO: GPIO
    # TODO: MAKE PROPER COMMENTARIES!!
    # TODO: check that we getting values from accesors and mutators
    # TODO: Check that we gain values from accessors from external.

#   --Arguments
host = 'localhost'
port = 1883
use_siemens = False
if '-gpio' in sys.argv:
    use_siemens = True
device_list_path = "cfg/DeviceList.json"
external_mqtt_conf_path = "cfg/ExternalMqttConf.json"

# --Parse arguments
# def arg_parse():
args = sys.argv
if '--help' in args:
    print("./lora_bridge -host [127.0.0.1] | -gpio | -mqttport [1883] | -object [GRS-2/ZAP_ABK/USNK]")
    os._exit(0)
if '-host' in args:
    # global host
    host = args[args.index('-host') + 1]
if '-mqttport' in args:
    # global port
    port = int(args[args.index('-mqttport') + 1])
if '-object' in args:
    # global device_list_path
    devlist_path_pattern = 'cfg/{}/DeviceList.json'
    extconf_path_pattern = 'cfg/{}/ExternalMqttConf.json'
    match args[args.index('-object') + 1]:
        case 'GRS-2':
            device_list_path = devlist_path_pattern.format("GRS-2")
            external_mqtt_conf_path = extconf_path_pattern.format("GRS-2")
        case 'ZAP_ABK':
            device_list_path = devlist_path_pattern.format("ZAP_ABK")
            external_mqtt_conf_path = extconf_path_pattern.format("ZAP_ABK")
        case 'USNK':
            device_list_path = devlist_path_pattern.format("USNK")
            external_mqtt_conf_path = extconf_path_pattern.format("USNK")
        case 'BVC':
            device_list_path = devlist_path_pattern.format("BVC")
            external_mqtt_conf_path = extconf_path_pattern.format("BVC")
        case 'CGTS':
            device_list_path = devlist_path_pattern.format("CGTS")
            external_mqtt_conf_path = extconf_path_pattern.format("CGTS")
        case 'CMVI':
            device_list_path = devlist_path_pattern.format("CMVI")
            external_mqtt_conf_path = extconf_path_pattern.format("CMVI")
        case 'CTMP':
            device_list_path = devlist_path_pattern.format("CTMP")
            external_mqtt_conf_path = extconf_path_pattern.format("CTMP")
        case 'Dudinka':
            device_list_path = devlist_path_pattern.format("Dudinka")
            external_mqtt_conf_path = extconf_path_pattern.format("Dudinka")
        case 'FOK':
            device_list_path = devlist_path_pattern.format("FOK")
            external_mqtt_conf_path = extconf_path_pattern.format("FOK")
        case 'GRS-1':
            device_list_path = devlist_path_pattern.format("GRS-1")
            external_mqtt_conf_path = extconf_path_pattern.format("GRS-1")
        case 'Mayak_ABK':
            device_list_path = devlist_path_pattern.format("Mayak_ABK")
            external_mqtt_conf_path = extconf_path_pattern.format("Mayak_ABK")
        case 'Mayak_PZK':
            device_list_path = devlist_path_pattern.format("Mayak_PZK")
            external_mqtt_conf_path = extconf_path_pattern.format("Mayak_PZK")
        case 'Messoyaha':
            device_list_path = devlist_path_pattern.format("Messoyaha")
            external_mqtt_conf_path = extconf_path_pattern.format("Messoyaha")
        case 'NOV3':
            device_list_path = devlist_path_pattern.format("NOV3")
            external_mqtt_conf_path = extconf_path_pattern.format("NOV3")
        case 'Pelyatka':
            device_list_path = devlist_path_pattern.format("Pelyatka")
            external_mqtt_conf_path = extconf_path_pattern.format("Pelyatka")
        case 'PESH_BIO':
            device_list_path = devlist_path_pattern.format("PESH_BIO")
            external_mqtt_conf_path = extconf_path_pattern.format("PESH_BIO")
        case 'Plot_3':
            device_list_path = devlist_path_pattern.format("Plot_3")
            external_mqtt_conf_path = extconf_path_pattern.format("Plot_3")
        case 'PNS-3':
            device_list_path = devlist_path_pattern.format("PNS-3")
            external_mqtt_conf_path = extconf_path_pattern.format("PNS-3")
        case 'Tuhard':
            device_list_path = devlist_path_pattern.format("Tuhard")
            external_mqtt_conf_path = extconf_path_pattern.format("Tuhard")
        case 'ZAP_9BIS':
            device_list_path = devlist_path_pattern.format("ZAP_9BIS")
            external_mqtt_conf_path = extconf_path_pattern.format("ZAP_9BIS")
        case 'NASOS-2':
            device_list_path = devlist_path_pattern.format("NASOS-2")
            external_mqtt_conf_path = extconf_path_pattern.format("NASOS-2")
        case _:
            raise Exception(f"Config files for object not found! Check cfg folder.")

def init_device_list(device_list_path):
    with open(device_list_path, 'r') as f:
        js = json.load(f)
    return js

def init_tk_config(tk_config_file):
    with open(tk_config_file, 'r') as f:
        js = json.load(f)
    return js

def init_external_mqtt_conf(path):
        with open(path, 'r') as f:
            ext_mqtt_conf = json.load(f)
        return ext_mqtt_conf

#   --Init instances
tk_config = init_tk_config("cfg/TkConfig.json")
device_storage = MES_storage.devices()
packet_factory = MES_packet_handler.packet_factory()
local_mqtt_client = mqtt.Client(reconnect_on_failure=True)
external_mqtt_client = mqtt.Client(reconnect_on_failure=True)
if use_siemens:
    simatic = MES_gpio.simatic()
external_mqtt_conf = init_external_mqtt_conf(external_mqtt_conf_path)
ups_door_time = time.time() + 60 * 15


#   --MQTT
def on_message(client, userdata, msg):
    # Handle device data.
    if msg.topic == "application/trigger":
        ## Топик для отладки имеющихся дампов
        pass
    if msg.topic.endswith("/event/up") and msg.topic.startswith("application"): #UNCOMMENT 
        rx_json = json.loads(msg.payload) # Getting sent device data from MQTT #UNCOMMENT
        # Get device info
        rx_dev_eui = base64.b64decode(rx_json['devEUI']).hex()
        rx_dev_type = rx_json['applicationName']
        # Get device
        rx_device = device_storage.get_device(rx_dev_eui, rx_dev_type)
        if rx_device == False:
            raise ValueError(f"Device not found in storage! {rx_dev_type} {rx_dev_eui}")
        rx_device.set_chirpstack_name(rx_json['deviceName'])
        print(f"[*] Debug: << PACKET {rx_dev_type} {rx_dev_eui} {rx_json['deviceName']} | DATA: {base64.b64decode(rx_json['data']).hex()}")  
        # Handle packet
        rx_packet = packet_factory.create_packet(rx_json)
        rx_device.append_to_history(rx_packet)
        match rx_packet:
            case False:
                print("Packet is discarded.")
                return
            case "TIME_RQ":
                print(f"Time request for {rx_dev_type} {rx_dev_eui} {rx_device.get_chirpstack_name()}")
                rx_device.set_require_time_update()
            case None:
                # Попытка поймать не описанный в протоколе пакет.
                with open('unknown_packets', 'a') as file:
                    file.write(f"{rx_dev_type} {base64.b64decode(rx_json['data']).hex()}\n")
                return
        # Insert packet into device
        if packet_factory.is_measures(rx_packet):
            rx_device.insert_measure_packet(rx_packet, rx_packet.timestamp)
        elif packet_factory.is_status(rx_packet):
            rx_device.insert_status_packet(rx_packet)
            if rx_device.get_status_state() and rx_device.status_has_sent == False:
                status_topic= rx_device.create_status_topic()
                status_payload= rx_device.get_formatted_status()
                external_mqtt_client.publish(
                    topic= status_topic,
                    payload= status_payload,
                    qos=2
                )
                print("[*] Status has sent:", status_topic, status_payload)
                rx_device.status_has_sent = True

        ##!--TIME REQUESTS
        if packet_factory.is_time_request(rx_packet) or rx_device.is_require_time_update() and msg.topic != "application/trigger": #TODO: REMOVER TRIGGER AFTER TESTS
            msgtopic = msg.topic
            command_topic = current_topic_command(msgtopic)
            payload = server_info.get_formatted_command(type='time')
            external_mqtt_client.publish(
                topic=command_topic,
                payload=payload,
                qos=2
            )
            print(f"[*] >> SEND_TIME to {rx_dev_type} {rx_dev_eui}")
            print(command_topic)
            print(payload)
            rx_device.reset_require_time_update()
        if rx_device.is_require_settings_update():
            msgtopic = msg.topic
            command_topic = current_topic_command(msgtopic)
            payload = server_info.get_formatted_command(type='settings')
            external_mqtt_client.publish(
                topic=command_topic,
                payload=payload,
                qos=2
            )
            print(">>SEND_SETTINGS")
            print(command_topic)
            print(payload)
            rx_device.reset_require_settings_update()
        ##!--
        # Check ready statement and push data to mqtt
        if rx_device.ready_to_send:
            if rx_device.status_has_sent:
                print(f"[*] Debug | {rx_device.get_devType()} {rx_device.get_devEui()} status alrady sent. Sending measures...")
                measure_topic = rx_device.create_measure_topic()
                measure_values = rx_device.get_formatted_measures()
                mqtt_payload = MES_storage.mqtt_device_object(
                measure_topic = measure_topic,
                status_topic = None,
                measure_values = measure_values,
                status_values = None,
                dev_type = rx_dev_type,
                dev_eui = rx_dev_eui
            )
                rx_device.status_has_sent = False
            else:
                mqtt_payload = MES_storage.mqtt_device_object(
                    measure_topic = rx_device.create_measure_topic(),
                    status_topic = rx_device.create_status_topic(),
                    measure_values = rx_device.get_formatted_measures(),
                    status_values = rx_device.get_formatted_status(),
                    dev_type = rx_dev_type,
                    dev_eui = rx_dev_eui
                )
                print(rx_device.create_measure_topic())
                print(rx_device.create_status_topic())
                print(rx_device.get_formatted_measures())
                print(rx_device.get_formatted_status())
            device_storage.insert_to_send_queue(mqtt_payload)
            rx_device.reset_packets()
    if msg.topic.startswith("gateway"):  # топик для получения статуса geteway
        gw_id =  msg.topic.split('/')[1]
<<<<<<< HEAD
        print(f"[*] << GW {gw_id} | time: %s" % datetime.datetime.now())
=======
>>>>>>> f04be7711a139e42414826ec69b905435fa9e2ab
        server_info.gw_append_or_update(gw_id)
        
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[*] Server: {host} connected.")
    else:
        raise ConnectionError("!!! Server is unavailable !!")
    #TODO: Implement
    pass

#   --Functions
def init_devices(device_list_json, tk_config_json):
    """Создание экземпляро каждого устройства на обьекте. Добавление их в MES_storage.devices"""
    device_list = device_list_json
    tk_config = tk_config_json
    device_counter = 0
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
        device_counter = MES_device.device_factory.get_device_created()
    return device_counter

def update_uspd_status(server_info_instance, mqtt_client):
    object_count = len(server_info_instance.object_id_list)
    for i in range(0, object_count):
        topic = server_info_instance.get_topic_status(server_info_instance.object_id_list[i])
        value = server_info_instance.get_uspd_status_value()
        mqtt_client.publish(
            topic= topic,
            payload = value,
            qos= 2
        )
        print(f"[*] update_spd_status send: {topic}")
        print(f"[*] update_spd_status send: {value}")

def current_topic_command(topic):
    splitted_topic = topic.split('/')
    command_topic = ""
    for i in range(0,4):
        command_topic += splitted_topic[i] + '/'
    command_topic += "command/down"
    return command_topic

if use_siemens:
    #Trigggers for gpio
    def gpio_interrupt(gpio):
        time_uts = int(time.time())
        if gpio.getPin(True) == simatic.input_port_1.getPin(True):
            print('Door_open alarm')
            door_topic = '/Gorizont/'+ external_mqtt_conf['object_code'] +'/'+ external_mqtt_conf['object_id'] + '/' + external_mqtt_conf['uspd_code'] + '/door_open/measure'
            print(door_topic)
            door_value = str(time_uts) + '\r\n' + repr(gpio.read())
            mqtt_uspd_object = MES_storage.mqtt_uspd_object(door_topic, door_value)
            device_storage.insert_uspd_queue(mqtt_uspd_object)
        if gpio.getPin(True) == simatic.input_port_2.getPin(True):
            print('ups_status alarm')
            ups_topic = '/Gorizont/'+ external_mqtt_conf['object_code'] +'/'+ external_mqtt_conf['object_id'] + '/' + external_mqtt_conf['uspd_code'] + '/ups_status/measure'
            print(ups_topic)
            ups_value = str(time_uts) + '\r\n' + repr(1-gpio.read())
            mqtt_uspd_object = MES_storage.mqtt_uspd_object(ups_topic,ups_value)
            device_storage.insert_uspd_queue(mqtt_uspd_object)

        print("pin " + repr(gpio.getPin(True)) + " = " + repr(gpio.read()))
    
    def button_interrupt(gpio):
        print("pin " + repr(gpio.getPin(True)) + " = " + repr(gpio.read()))
    simatic.set_button_interrupt(button_interrupt)
    simatic.set_gpio_interrupt(gpio_interrupt)
    

def main():
    global server_info
    global ups_door_time
    # arg_parse()
    print("[*] Bridge server start...")
    device_list = init_device_list(device_list_path)
    device_count = init_devices(device_list, tk_config)
    server_info = MES_server.server_info(host, device_list, external_mqtt_conf)
    local_mqtt_client.connect(host, port)
    local_mqtt_client.subscribe('application/+/device/+/event/up', qos=2)
    local_mqtt_client.subscribe('gateway/+/event/#', qos=2)
    local_mqtt_client.subscribe('application/trigger', qos=2)
    local_mqtt_client.on_connect = on_connect
    local_mqtt_client.on_message = on_message
    local_mqtt_client.loop_start()
    external_mqtt_client.connect(host, port)
    external_mqtt_client.loop_start()
    print(f"[*] Devices initialized: {device_count}")
    

    while(True):
        if use_siemens:
            if device_storage.uspd_queue_not_empty():
                mqtt_uspd_object = device_storage.pop_uspd_queue()
                print(mqtt_uspd_object.topic)
                print(mqtt_uspd_object.value)
                external_mqtt_client.publish(
                        topic= mqtt_uspd_object.topic,
                        payload= mqtt_uspd_object.value,
                        qos=2
                    )
                device_logger.save_uspd(chirpstack_state=server_info.get_chirpstack_state(),
                                        gateway_state=server_info.get_gateway_state(),
                                        input1_response= simatic.get_input_port_1(),
                                        input2_response= simatic.get_input_port_2(),
                                        start_time=server_info.start_time)
        if device_storage.send_queue_not_empty():
            mqtt_device_object = device_storage.pop_mqtt_object()
            match mqtt_device_object.type:
                case "full":
                    print(mqtt_device_object.measure_topic)
                    print(mqtt_device_object.measure_values)
                    print(mqtt_device_object.status_topic)
                    print(mqtt_device_object.status_values)

                    external_mqtt_client.publish(
                        topic= mqtt_device_object.measure_topic,
                        payload= mqtt_device_object.measure_values, 
                        qos=2
                    )
                    external_mqtt_client.publish(
                        topic= mqtt_device_object.status_topic,
                        payload= mqtt_device_object.status_values,
                        qos=2
                    )
                    
                    device_logger.save_data(
                        dev_eui = mqtt_device_object.dev_eui,
                        mqtt_data= mqtt_device_object.measure_values,
                        type= mqtt_device_object.dev_type
                    )
                case "measures_only":
                    print(mqtt_device_object.measure_topic)
                    print(mqtt_device_object.measure_values)
                    external_mqtt_client.publish(
                        topic= mqtt_device_object.measure_topic,
                        payload= mqtt_device_object.measure_values, 
                        qos=2
                    )
                    device_logger.save_data(
                    dev_eui = mqtt_device_object.dev_eui,
                    mqtt_data= mqtt_device_object.measure_values,
                    type= mqtt_device_object.dev_type
                    )
                case "status_only":
                    print(mqtt_device_object.status_topic)
                    print(mqtt_device_object.status_values)
                    external_mqtt_client.publish(
                        topic= mqtt_device_object.status_topic,
                        payload= mqtt_device_object.status_values,
                        qos=2
                    )
            
        if server_info.request_uspd_update:
            update_uspd_status(
                server_info_instance=server_info,
                mqtt_client= external_mqtt_client
                )
            server_info.request_uspd_update = False
            server_info.reset_gateway_state()
            server_info.update_timer()
        device_settings_require_update = server_info.refresh_settings_config()
        if device_settings_require_update:
            device_storage.update_settings()
            server_info.refresh_settings_config()
        if use_siemens:
            if ups_door_time <= time.time():
                ups_door_time = time.time() + 60 * 15
                gpio_interrupt(simatic.input_port_1)
                gpio_interrupt(simatic.input_port_2)
            simatic.led_port_on()
            time.sleep(0.05)
            simatic.led_port_off()
        time.sleep(0.5)

if __name__ == "__main__":
    main()
    # debug()