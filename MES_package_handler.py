#TODO: В классе пакет проинициализировать поля которые встречаются в каждом пакете.
#TODO: Продумать логику как определять пакет (по первому байту?) и сделать методы по созданию экземпляра конкретного пакета.

class packet_factory(object):
    pass    

class packet(object):
    def __init__(self, rx_json) -> None:
        pass
    def __str__(self) -> str:
        pass

class inclinometer_data_package(packet):
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
    def __str__(self) -> str:
        return super().__str__()

class thermometer_data_package(packet):
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
    def __str__(self) -> str:
        return super().__str__()

class piezometer_data_package(packet):
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
    def __str__(self) -> str:
        return super().__str__()

class hygrometer_data_package(packet):
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)

class battery_info_packet(packet):
    def __init__(self, rx_json) -> None:
        super().__init__(rx_json)
    def __str__(self) -> str:
        return super().__str__()

if __name__ == "__main__":
    print("Entry point: MES_package_handler")