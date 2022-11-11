import mraa
import time

class simatic(object):
    def set_gpio_interrupt(self, gpio_interrupt):
        self.input_port_1.isr(mraa.EDGE_BOTH, gpio_interrupt, self.input_port_1) # При нажатии и отпускании
        self.input_port_2.isr(mraa.EDGE_BOTH, gpio_interrupt, self.input_port_2) # При нажатии и отпускании
        self.input_port_3.isr(mraa.EDGE_BOTH, gpio_interrupt, self.input_port_3) # При нажатии и отпускании
        self.input_port_4.isr(mraa.EDGE_BOTH, gpio_interrupt, self.input_port_4) # При нажатии и отпускании
        self.gpio_interrupt_has_set = True

    def set_button_interrupt(self, button_interrupt):
        self.button_port.isr(mraa.EDGE_FALLING, button_interrupt, self.button_port) # При отпускании кнопки
        self.button_interrupt_has_set = True
        
    def get_input_port_1(self):
        return repr(self.input_port_1.read())
    
    def get_input_port_2(self):
        return repr(1 - self.input_port_2.read())
    
    def led_port_on(self):
        self.led_port.write(1)
    
    def led_port_off(self):
        self.led_port.write(0)
    
    def __init__(self, startup_delay = True):
        self.button_interrupt_has_set = False
        self.gpio_interrupt_has_set = False
        self.led_port = mraa.Gpio(13)
        self.led_port.dir(mraa.DIR_OUT) # Direction pin output
        
        self.button_port = mraa.Gpio(20) #button 20
        
        self.input_port_1 = mraa.Gpio(8)
        self.input_port_1.dir(mraa.DIR_IN) # Direction pin input
        
        self.input_port_2 = mraa.Gpio(9)
        self.input_port_2.dir(mraa.DIR_IN) # Direction pin input

        self.input_port_3 = mraa.Gpio(10)
        self.input_port_3.dir(mraa.DIR_IN) # Direction pin input

        self.input_port_4 = mraa.Gpio(11)
        self.input_port_4.dir(mraa.DIR_IN) # Direction pin input
        
        self.panel_led_1R = mraa.Led(1)
        self.panel_led_1G = mraa.Led(0)
        self.panel_led_2R = mraa.Led(3)
        self.panel_led_2G = mraa.Led(2)    
        
        self.panel_led_1R.setBrightness(0)
        self.panel_led_1G.setBrightness(0)
        self.panel_led_2R.setBrightness(0)
        self.panel_led_2G.setBrightness(0)
        self.startup_delay = startup_delay
        
        # if startup_delay:
        #     for i in range(0, 60): 
        #         self.panel_led_1G.setBrightness(255)
        #         self.panel_led_1R.setBrightness(0)
        #         time.sleep(0.5)
        #         self.panel_led_1G.setBrightness(0)
        #         self.panel_led_1R.setBrightness(0)
        #         time.sleep(0.5)
        self.panel_led_1R.setBrightness(255) # При успешной инициализции зажигаем LED 1R.

if __name__ == '__main__':
    simatic = simatic()
    print('Input states:')
    print("Port1: " + str(simatic.input_port_1.read()))
    print("Port2: " + str(simatic.input_port_2.read()))
    print("Port3: " + str(simatic.input_port_3.read()))
    print("Port4: " + str(simatic.input_port_4.read())) 