from enum import IntEnum

class RelayStates(IntEnum):
    STATE_OFF = 0
    STATE_WG1 = 1
    STATE_WG2 = 2
    STATE_SCOPE_TO_GND = 3
    STATE_SCOPE_TO_WG1 = 4
    STATE_V_PLUS = 5
    STATE_V_MINUS = 6

