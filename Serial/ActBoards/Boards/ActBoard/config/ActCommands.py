
from enum import IntEnum, auto

class ActCommands(IntEnum):
    setRelayState = 0,
    checkCurrent = 1,
    setCalStatus = 2,
    
class ActCalStatus(IntEnum):
    not_ready = 0,
    ready = 1,
    calibrating = 2,
    cal_good = 3,
    error = 4