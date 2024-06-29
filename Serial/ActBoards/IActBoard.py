from abc import ABC, abstractmethod
from Serial.ActBoards.RelayStates import RelayStates
from Serial.SerialConfig import SerialConfig

from serial import Serial
from Serial.SerialConnection import SerialConnection

# All board classes will inherit from this one.
# This class inherits from SerialConnection which implements
# __enter__ and __exit__ methods for managing the serial connection
# through Context Manager
class IActBoard(ABC):
    def __init__(self, com_port: str):
        self.__serial_conn__ = Serial(com_port, timeout=1)

    
    @abstractmethod
    def set_relay_state(self, state: RelayStates):
        ...
    
    @abstractmethod
    def reset_relays( self):
        ...
    
    def _get_conn(self):
        return self.__serial_conn__
    
    def close(self):
        self.__serial_conn__.close()
    
    
