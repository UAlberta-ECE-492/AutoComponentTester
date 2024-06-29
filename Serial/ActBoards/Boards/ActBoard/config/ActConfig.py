from dataclasses import dataclass

@dataclass
class ArduinoActConfig:
    ackDelimiter = "|"
    ackChunkLen = 2 # code|message
    ackReadyMessage = b"ready!\n"
