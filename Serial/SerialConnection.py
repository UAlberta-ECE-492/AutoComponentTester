
from serial import Serial
from Serial.SerialConfig import SerialConfig

class SerialConnection:
    def __init__(self, serialConfig: SerialConfig) -> None:
        self.__serial_conn__ = None
        self.__serial_config__ = serialConfig
    
    def __enter__(self):
        print(self.__serial_config__)
        com_port = self.__serial_config__.com_port
        baud_rate = self.__serial_config__.baud_rate
        byte_size = self.__serial_config__.byte_size
        parity = self.__serial_config__.parity
        stopbits = self.__serial_config__.stop_bits
        serial_timeout = self.__serial_config__.serial_timeout
        xon_xoff = self.__serial_config__.xon_xoff
        rts_cts = self.__serial_config__.rts_cts
        self.__serial_conn__ = Serial(com_port, baud_rate, byte_size, parity, stopbits, timeout, xon_xoff, rts_cts)
        return self
    
    def _get_conn(self):
        return self.__serial_conn__
    
    def __exit__(self, exc_type, exc_value, tb):
        if self.__serial_conn__ != None:
            self.__serial_conn__.close()