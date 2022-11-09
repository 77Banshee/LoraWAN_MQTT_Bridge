import mraa


def ButtonInterrupt(gpio):
		print("pin " + repr(gpio.getPin(True)) + " = " + repr(gpio.read()))
  
def GpioInterrupt(gpio):
		global GpioIntFlag
		time_uts = int(time.time())
		if gpio.getPin(True) == InputPort1.getPin(True):
			print('Port1 alarm')
			tts = '/Gorizont/'+ ExternMqttConf['object_code'] +'/'+ ExternMqttConf['object_id'] + '/' + ExternMqttConf['uspd_code'] + '/door_open/measure'
			res_msg = str(time_uts) + '\r\n' + repr(gpio.read())
			to_send = MqttObject(tts, res_msg)
			GpioIntFlag = True
			ExtMqMessagesQueue.put(to_send)
		if gpio.getPin(True) == InputPort2.getPin(True):
			tts = '/Gorizont/'+ ExternMqttConf['object_code'] +'/'+ ExternMqttConf['object_id'] + '/' + ExternMqttConf['uspd_code'] + '/UPS_status/measure'
			res_msg = str(time_uts) + '\r\n' + repr(1-gpio.read())
			to_send = MqttObject(tts, res_msg)
			GpioIntFlag = True
			ExtMqMessagesQueue.put(to_send)
			print('Port2 alarm')

		print("pin " + repr(gpio.getPin(True)) + " = " + repr(gpio.read()))
  
if USE_SIEMENS == 1:
	
	LedPort = mraa.Gpio(13)
	ButtonPort = mraa.Gpio(20) #button 20
	InputPort1 = mraa.Gpio(8)
	InputPort2 = mraa.Gpio(9)
	InputPort3 = mraa.Gpio(10)
	InputPort4 = mraa.Gpio(11)
	LedPort.dir(mraa.DIR_OUT)
	InputPort1.dir(mraa.DIR_IN)
	InputPort2.dir(mraa.DIR_IN)
	InputPort3.dir(mraa.DIR_IN)
	InputPort4.dir(mraa.DIR_IN)

	InputPort1.isr(mraa.EDGE_BOTH, GpioInterrupt, InputPort1)
	InputPort2.isr(mraa.EDGE_BOTH, GpioInterrupt, InputPort2)
	InputPort3.isr(mraa.EDGE_BOTH, GpioInterrupt, InputPort3)
	InputPort4.isr(mraa.EDGE_BOTH, GpioInterrupt, InputPort4)
	ButtonPort.isr(mraa.EDGE_FALLING, ButtonInterrupt, ButtonPort)

	#test gpiio board:
	print('Input states:')
	print(str(InputPort1.read()))
	print(str(InputPort2.read()))
	print(str(InputPort3.read()))
	print(str(InputPort4.read()))

	PanelLed1R = mraa.Led(1)
	PanelLed1G = mraa.Led(0)
	PanelLed2R = mraa.Led(3)
	PanelLed2G = mraa.Led(2)

	PanelLed1R.setBrightness(0)
	PanelLed1G.setBrightness(0)
	PanelLed2R.setBrightness(0)
	PanelLed2G.setBrightness(0)
	if startup_delay:
		for i in range(0, 60): 
			PanelLed1G.setBrightness(255)
			PanelLed1R.setBrightness(0)
			time.sleep(0.5)
			PanelLed1G.setBrightness(0)
			PanelLed1R.setBrightness(0)
			time.sleep(0.5)

	PanelLed1R.setBrightness(255)