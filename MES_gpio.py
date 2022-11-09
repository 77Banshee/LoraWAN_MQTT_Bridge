import mraa
import time

class simatic(object):
    def ButtonInterrupt(gpio):
        print("pin " + repr(gpio.getPin(True)) + " = " + repr(gpio.read()))
  
    def GpioInterrupt(gpio):
            global GpioIntFlag
            time_uts = int(time.time())
            if gpio.getPin(True) == InputPort1.getPin(True):
                print('Port1 alarm')
                
                #Формирование топика
                tts = '/Gorizont/'+ ExternMqttConf['object_code'] +'/'+ ExternMqttConf['object_id'] + '/' + ExternMqttConf['uspd_code'] + '/door_open/measure'
                res_msg = str(time_uts) + '\r\n' + repr(gpio.read())
                to_send = MqttObject(tts, res_msg)
                
                #Флаг для логгирования
                GpioIntFlag = True
                
                #Отправка
                ExtMqMessagesQueue.put(to_send)
            if gpio.getPin(True) == InputPort2.getPin(True):
                print('Port2 alarm')
                
                #Формирование топика
                tts = '/Gorizont/'+ ExternMqttConf['object_code'] +'/'+ ExternMqttConf['object_id'] + '/' + ExternMqttConf['uspd_code'] + '/UPS_status/measure'
                res_msg = str(time_uts) + '\r\n' + repr(1-gpio.read())
                to_send = MqttObject(tts, res_msg)
                
                #Флаг для логгирования
                GpioIntFlag = True
                
                #Отправка
                ExtMqMessagesQueue.put(to_send)
            print("pin " + repr(gpio.getPin(True)) + " = " + repr(gpio.read()))
    def __init__(self, startup_delay = True):
        self.startup_delay = startup_delay
        self.LedPort = mraa.Gpio(13)
        self.LedPort.dir(mraa.DIR_OUT)
        
        self.ButtonPort = mraa.Gpio(20) #button 20
        self.ButtonPort.isr(mraa.EDGE_FALLING, self.ButtonInterrupt, self.ButtonPort)
        
        self.InputPort1 = mraa.Gpio(8)
        self.InputPort1.dir(mraa.DIR_IN)
        self.InputPort1.isr(mraa.EDGE_BOTH, self.GpioInterrupt, self.InputPort1)
        
        self.InputPort2 = mraa.Gpio(9)
        self.InputPort2.dir(mraa.DIR_IN)
        self.InputPort2.isr(mraa.EDGE_BOTH, self.GpioInterrupt, self.InputPort2)

        self.InputPort3 = mraa.Gpio(10)
        self.InputPort3.dir(mraa.DIR_IN)
        self.InputPort3.isr(mraa.EDGE_BOTH, self.GpioInterrupt, self.InputPort3)

        self.InputPort4 = mraa.Gpio(11)
        self.InputPort4.dir(mraa.DIR_IN)
        self.InputPort4.isr(mraa.EDGE_BOTH, self.GpioInterrupt, self.InputPort4)
        
        self.PanelLed1R = mraa.Led(1)
        self.PanelLed1G = mraa.Led(0)
        self.PanelLed2R = mraa.Led(3)
        self.PanelLed2G = mraa.Led(2)    
        
        self.PanelLed1R.setBrightness(0)
        self.PanelLed1G.setBrightness(0)
        self.PanelLed2R.setBrightness(0)
        self.PanelLed2G.setBrightness(0)
        if startup_delay:
            for i in range(0, 60): 
                self.PanelLed1G.setBrightness(255)
                self.PanelLed1R.setBrightness(0)
                time.sleep(0.5)
                self.PanelLed1G.setBrightness(0)
                self.PanelLed1R.setBrightness(0)
                time.sleep(0.5)
        self.PanelLed1R.setBrightness(255)
            
 
    




if __name__ == '__main__':
    simatic = simatic()
    print('Input states:')
    print(str(simatic.InputPort1.read()))
    print(str(simatic.InputPort2.read()))
    print(str(simatic.InputPort3.read()))
    print(str(simatic.InputPort4.read())) 