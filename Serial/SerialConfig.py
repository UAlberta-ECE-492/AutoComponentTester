
from dataclasses import dataclass
from serial import EIGHTBITS, PARITY_NONE,  STOPBITS_ONE

# Default values from https://pyserial.readthedocs.io/en/latest/pyserial_api.html
@dataclass
class SerialConfig:
    com_port: str
    baud_rate: int = 9600
    byte_size: int = EIGHTBITS
    parity: str = PARITY_NONE
    stop_bits: float =  STOPBITS_ONE
    timeout: float = 1 # We set a default of 1 second
    xon_xoff: bool = False
    rts_cts: bool = False


