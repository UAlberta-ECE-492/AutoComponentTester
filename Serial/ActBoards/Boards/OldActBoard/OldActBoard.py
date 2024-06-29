
# Allows interfacing with the old ACT board
from Serial.ActBoards.RelayStates import RelayStates
from Serial.ActBoards.IActBoard import IActBoard
from InternalOldBoardStates import relay_state_to_internal_state
import time

relay_state_to_internal_state = {
    RelayStates.STATE_OFF: b'Starting - Press\r\n',
    RelayStates.STATE_WG1: b'Waveform Generator 1\r\n',
    RelayStates.STATE_WG2: b'Waveform Generator 2\r\n',
    RelayStates.STATE_SCOPE_TO_GND: b'Scope Ground All\r\n',
    RelayStates.STATE_SCOPE_TO_WG1: b'Scope to WG1\r\n',
    RelayStates.STATE_V_PLUS: b'Pos Supply\r\n',
    RelayStates.STATE_V_MINUS: b'Neg Supply\r\n'
}

class OldActBoard(IActBoard.IActBoard):
    def __init__(self, com_port: str) -> None:
        super().__init__(com_port)

    def set_relay_state(self, state: RelayStates):
        while True:
            self._get_conn().write(b"\n")
            message = self._get_conn().readline()
            if message == relay_state_to_internal_state[state]:
                break
            time.sleep(0.500)
        #self._get_conn().read(400)
        
    def reset_relays(self):
        self.set_relay_state(RelayStates.STATE_OFF)
    
