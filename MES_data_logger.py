import os
import time

log_folder = 'logs'

if not os.path.exists(log_folder):
    os.mkdir(log_folder, 0o777)
    
class device_logger(object):
    @classmethod
    def save_data(self, dev_eui,  mqtt_data, type):
        put_header = True
        file_name = log_folder + f'/{type}_' + time.strftime("%Y.%m.csv", time.localtime(time.time()))
        if os.path.exists(file_name):
            put_header = False
        with open(file_name, 'a') as file:
            if put_header:
                match type:
                    case 'Inclinometer':
                        file.write('DevEUI;Unix Time;X;Y' + '\n')
                    case 'Thermometer':
                        file.write('DevEUI;Unix Time;Sensors Quantity;')
                        for i in range(1, 30):  # max sensors for now is 29
                            file.write('T' + str(i) + ';')
                        file.write('\n')
                    case 'Hygrometer':
                        return
                    case 'Piezometer':
                        file.write('DevEUI;Unix Time;Pressure' + '\n')
                        pass
            file.write(dev_eui + ';')
            file.write(mqtt_data.replace('\r\n', ';'))
            file.write('\n')
            # file.write(self.__mqtt_to_csv_data_format(mqtt_data))
            print("Saved!")
    @classmethod
    def save_uspd(self, chirpstack_state, gateway_state, input1_response, input2_response, start_time):
        filename = f"{log_folder}/Status_"+time.strftime("%Y.%m.csv", time.localtime(time.time()))
        put_header = True
        if os.path.exists(filename):
            put_header = False
        with open(filename, "a") as file:
            #write header in new file
            if put_header:
                file.write('Unix Time;Uptime;Gateway;Chirpstack;Door;UPS\r\n')
            current_time = int(time.time())
            uptime = current_time - start_time
            inputs_str = f"{str(current_time)};{uptime};{gateway_state};{chirpstack_state};{input1_response};{input2_response}"
            file.write(inputs_str)
            file.write('\r\n')
            file.close()
            
if __name__ == "__main__":
    device_logger.save_uspd("0","0",1)