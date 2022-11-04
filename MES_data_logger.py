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
    
if __name__ == "__main__":
    print("[*] data_logger DEBUG")
    device_logger.save_data("07293314052d6d1f", "1666533296\r\n-5312.7265625\r\n-3195.140625", "Inclinometer")
    device_logger.save_data("AAAAAAAAA","1666537289\r\n17\r\n0.1\r\n0.78\r\n1.47\r\n3.49\r\n5.92\r\n7.83\r\n8.94\r\n9.73\r\n9.79\r\n9.85\r\n9.77\r\n9.6\r\n9.46\r\n9.52\r\n9.61\r\n9.75", "Thermometer")
    