import sys
import json
from MES_data_logger import device_logger
import MES_device
import MES_storage
import MES_packet_handler
import MES_server
import paho.mqtt.client as mqtt
import base64
import time

# Map
# -- Пакет пришел CHECK > Достали устройство CHECK > Обработали пакет CHECK > 
#    Добавили в устройство CHECK > 
#    В мейне тут же проверили ready_to_send, если вернул True CHECK > 
#    Дулаем топики CHECK > Запихиваем в очередь которая проверяется в бесконечном цикле CHECK> и сразу чистим девайс CHECK.

## TODO: Debug
    # Remove TEST profix from ExternalMqttConf
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
# host = 'localhost'
host = '10.19.128.162'
port = 1883
args = sys.argv
if (len(args) > 1):
    host = args[1]

# --Init settings
def init_device_list(device_list_path):
    with open(device_list_path, 'r') as f:
        js = json.load(f)
    return js

def init_tk_config(tk_config_file):
    with open(tk_config_file, 'r') as f:
        js = json.load(f)
    return js

#   --Init instances
device_list = init_device_list("cfg/DeviceList.json")
tk_config = init_tk_config("cfg/TkConfig.json")
device_storage = MES_storage.devices()
packet_factory = MES_packet_handler.packet_factory()
local_mqtt_client = mqtt.Client(reconnect_on_failure=True)
external_mqtt_client = mqtt.Client(reconnect_on_failure=True)
server_info = MES_server.server_info(host, device_list)

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
            raise ValueError("Device not found in storage!")
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
            print(f">> SEND_TIME to {rx_dev_type} {rx_dev_eui}")
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
        server_info.set_gateway_online()
        
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


def main():
    print("[*] Bridge server start...")
    device_count = init_devices(device_list, tk_config)
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
        time.sleep(0.5)

if __name__ == "__main__":
    main()
    # debug()