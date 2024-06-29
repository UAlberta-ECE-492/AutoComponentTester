
from Serial.ActBoards.RelayStates import RelayStates
from Serial.ActBoards.IActBoard import IActBoard

from dataclasses import dataclass

from Serial.ActBoards.Boards.ActBoard.config.ActCommands import ActCommands, ActCalStatus
from Serial.ActBoards.Boards.ActBoard.config.ActConfig import ArduinoActConfig
from Serial.ActBoards.Boards.ActBoard.config.ActExceptions import ActCommandExecFailure, InvalidAckReceivedException

class ActBoard(IActBoard):
    def __init__(self, com_port: str, max_attempt=10) -> None:
        
        super().__init__(com_port)
        conn = self._get_conn()
        
        print("Waiting for ready message from arduino...")
        connected = conn.readline() == ArduinoActConfig.ackReadyMessage
        attempts = 0
        while not connected:
            connected = conn.readline() == ArduinoActConfig.ackReadyMessage
            attempts += 1
            if attempts >= max_attempt and not connected:
                print("Could not connect to Arduino")
                raise Exception("Could not connect to Arduino")
        
        print(f"Arduino on {com_port} is ready!")

    def check_current(self) -> str:
        # Returns string rep of meas. current in uA
        self.exec_command(ActCommands.checkCurrent, 0)
        return self._get_conn().readline().strip()

    def set_relay_state(self, state: RelayStates):
        self.exec_command(ActCommands.setRelayState, state)
        
    def set_cal_status(self, status: ActCalStatus):
        self.exec_command(ActCommands.setCalStatus, status)
        
    def reset_relays(self):
        self.exec_command(ActCommands.setRelayState, RelayStates.STATE_OFF)

    def exec_command(self, cmd: ActCommands, data: int):
        self._send_act_command(cmd, data)
    
    def _send_act_command(self, command: ActCommands, data: int):
        # 3 sequential bytes expected by ActBoard (command, data, 0xFF)
        # Third byte must always be 0xFF
        dataToWrite = bytearray([int(command), data, 0xFF])
        self._get_conn().write(dataToWrite)
        # Expect an ack message, will timeout after 1s 
        ack_response = self._get_conn().readline()
        # code, message = self.parse_ack_response(ack_response)
        # if code == 0:
        #     raise ActCommandExecFailure(message)
        
    def parse_ack_response(self, response: str) -> tuple[int, str]:
        '''
        Ack response format:
        code|message
        ------------
        Codes:
        0: failure
        1: success
        '''
        chunks = response.split(ArduinoActConfig.ackDelimiter)
        if len(chunks) != ArduinoActConfig.ackChunkLen:
            raise InvalidAckReceivedException
        try:
            code = int(chunks[0])
        except:
            raise InvalidAckReceivedException("Invalid ack code received. Expected an integer")
        message = chunks[1]
        return code, message
    