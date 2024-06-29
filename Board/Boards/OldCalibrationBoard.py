from IBoardManager import IBoardManager, RELAY_STATES
import serial
import time

board_stages_id_by_name = {
    b'Starting - Press\r\n': RELAY_STATES.STATE_OFF,
    b'Waveform Generator 1\r\n': RELAY_STATES.STATE_WG1,
    b'Waveform Generator 2\r\n': RELAY_STATES.STATE_WG2,
    b'Scope Ground All\r\n': RELAY_STATES.STATE_SCOPE_TO_GND,
    b'Scope to WG1\r\n': RELAY_STATES.STATE_SCOPE_TO_WG1,
    b'Pos Supply\r\n': RELAY_STATES.STATE_V_PLUS,
    b'Neg Supply\r\n': RELAY_STATES.STATE_V_MINUS,
    b'Finished\r\n': RELAY_STATES.STATE_OFF,
    b'\r\n': RELAY_STATES.STATE_OFF,
    b'\r\n': RELAY_STATES.STATE_OFF,
    b'\r\n': RELAY_STATES.STATE_OFF,
}
name_by_board_stages_id = {
    RELAY_STATES.STATE_OFF: b'Starting - Press\r\n',
    RELAY_STATES.STATE_WG1: b'Waveform Generator 1\r\n',
    RELAY_STATES.STATE_WG2: b'Waveform Generator 2\r\n',
    RELAY_STATES.STATE_SCOPE_TO_GND: b'Scope Ground All\r\n',
    RELAY_STATES.STATE_SCOPE_TO_WG1: b'Scope to WG1\r\n',
    RELAY_STATES.STATE_V_PLUS: b'Pos Supply\r\n',
    RELAY_STATES.STATE_V_MINUS: b'Neg Supply\r\n'
}

class OldCalibrationBoard(IBoardManager):
    def __init__(self) -> None:
        super().__init__()
        self.current_state = None
        self.__serial_conn__ = None
        self.__baud_rate__ = None
        self.__com_port__ = None
        self.__timeout__ = None

    def set_relay_state(self, state: RELAY_STATES):
        if self.current_state == None:
            self.reset_relays()
        
        
    def get_relay_state(self) -> RELAY_STATES:
        ...
    def reset_relays(self):
        self.__go_to_stage(board_stages_id_by_name[b'Starting - Press\r\n'])
    

    def __next_stage__(self):
        self.__serial_conn__.write(b"\n")
        message = self.__serial_conn__.readline()
        return message

    def __go_to_stage(self, target_idx: int):
        while True:
            self.__serial_conn__.write(b"\n")
            message = self.__serial_conn__.readline()
            print(message)
            if board_stages_id_by_name[message] == target_idx:
                break
            time.sleep(0.500)
        self.__serial_conn__.read(400)


    def __init__(self, COM_PORT: str, baudRate = 9600, timeout=1):
        self.__baud_rate__ = baudRate
        self.__com_port__ = COM_PORT
        self.__timeout__ = timeout
    
