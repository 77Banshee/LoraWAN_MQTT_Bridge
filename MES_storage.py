import MES_device
#Implementation of Design Pattern - Singleton
class SingletonMetaClass(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class devices(metaclass=SingletonMetaClass):
    __allowed_to_store = ["Inclinometer", "Thermometer", "Piezometer", "Hygrometer"]
    __inclinometers = []
    __thermometers = []
    __piezometers = []
    __hygrometers = []
   
    def allowed_type(cls, device): # check input instance for allowed type (to avoid the case with wrong input instance)
        if device.get_devType() in cls.__allowed_to_store:
            return True
        else:
            print(f"Not allowed: {device.get_devType()}")
        return False
    
    def append_device(self, device):
        if self.allowed_type(device) and not self.contains_device(device):
            match device.get_devType():
                case 'Inclinometer':
                    self.__inclinometers.append(device)
                    print(f"Appended:\n" + device.__str__() + "\n")
                case 'Thermometer':
                    self.__thermometers.append(device)
                    print(f"Appended:\n" + device.__str__() + "\n")
                case 'Piezometer':
                    self.__piezometers.append(device)
                    print(f"Appended:\n" + device.__str__() + "\n")
                case 'Hygrometer':
                    self.__hygrometers.append(device)
                    print(f"Appended:\n" + device.__str__() + "\n")
        else:
            print("[*] append_device() ->  Device NOT allowd!")

    #TODO: IMPLEMENT!
    def remove_device(device):
        raise NotImplemented()    

    #TODO: Require tests!
    def contains_device(self, device): 
        if isinstance(device, MES_device.device) == False:
            return
        match device.get_devType():
            case "Inclinometer":
                if device in self.__inclinometers:
                    return True
            case "Thermometer":
                if device in self.__thermometers:
                    return True
            case "Piezometer":
                if device in self.__piezometers:
                    return True
            case "Hygrometer":
                if device in self.__hygrometers:
                    return True
        return False

    #TODO: require tests!
    def get_device(self, dev_eui, dev_type): 
        print(len(self.__inclinometers))
        match dev_type:
            case "Inclinometer":
                for i in range(0, len(self.__inclinometers)):
                    if self.__inclinometers[i].get_devEui() == dev_eui:
                        return self.__inclinometers[i]
            case "Thermometer":
                for i in range(0, len(self.__thermometers)):
                    if self.__thermometers[i].get_devEui() == dev_eui:
                        return self.__thermometers[i]
            case "Piezometer":
                for i in range(0, len(self.__piezometers)):
                    if self.__piezometers[i].get_devEui() == dev_eui:
                        return self.__piezometers[i]
            case "Hygrometer":
                for i in range(0, len(self.__hygrometers)):
                    if self.__hygrometers[i].get_devEui() == dev_eui:
                        return self.__hygrometers[i]
        return False
    

if __name__ == "__main__":
    print("Entry point: MES_device.py")