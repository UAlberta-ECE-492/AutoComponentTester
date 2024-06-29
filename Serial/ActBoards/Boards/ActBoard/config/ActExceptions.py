

class ArduinoActException(Exception):
    pass

class InvalidAckReceivedException(ArduinoActException):
    pass

class ActCommandExecFailure(ArduinoActException):
    pass