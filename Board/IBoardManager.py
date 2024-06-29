from abc import ABC, abstractmethod
from enum import Enum, auto
import serial

class RelayStates(Enum):
    STATE_OFF = 0
    STATE_WG1 = 1
    STATE_WG2 = 2
    STATE_SCOPE_TO_GND = 3
    STATE_SCOPE_TO_WG1 = 4
    STATE_V_PLUS = 5
    STATE_V_MINUS = 6

class IBoardManager(ABC):
    def __init__(self, COM_PORT: str, baudRate = 9600, timeout=1):
        self.__baud_rate__ = baudRate
        self.__com_port__ = COM_PORT
        self.__timeout__ = timeout
        self.__serial_conn__ = None

    @abstractmethod
    def set_relay_state(self, state: RelayStates):
        ...
    @abstractmethod
    def get_relay_state(self) -> RelayStates:
        ...
    @abstractmethod
    def reset_relays(  self):
        ...
    
    def getSerial(self) -> serial.Serial:
        if self.__serial_conn__ == None:
            raise ValueError("Serial connection not opened yet. Use 'with' resource management")
        return self.__serial_conn__
    
    def __enter__(self):
        self.__serial_conn__ = serial.Serial(self.__com_port__, self.__baud_rate__, self.__timeout__)
        return self.__serial_conn__
    
    def __exit__(self):
        if self.__serial_conn__ != None:
            self.__serial_conn__.close()
