
import serial
import time


board_stages_name_by_id = {
    0: b'Starting - Press\r\n',
    1: b'Waveform Generator 1\r\n',
    2: b'Waveform Generator 2\r\n',
    3: b'Scope Ground All\r\n',
    4: b'Scope to WG1\r\n',
    5: b'Pos Supply\r\n',
    6: b'Neg Supply\r\n',
    7: b'Finished\r\n',
    8: b'\r\n',
    9: b'\r\n',
    10: b'\r\n',
}

board_stages_id_by_name = {
    b'Starting - Press\r\n': 0,
    b'Waveform Generator 1\r\n': 1,
    b'Waveform Generator 2\r\n': 2,
    b'Scope Ground All\r\n': 3,
    b'Scope to WG1\r\n': 4,
    b'Pos Supply\r\n': 5,
    b'Neg Supply\r\n': 6,
    b'Finished\r\n': 0,
    b'\r\n': 0,
    b'\r\n': 0,
    b'\r\n': 0,
}


class BoardManager:
    def __init__(self, com_num: int) -> None:
        self.__conn__ = serial.Serial(f"COM{com_num}", timeout=1) # 4
    
    def __go_to_stage(self, target_idx: int):
        while True:
            self.__conn__.write(b"\n")
            message = self.__conn__.readline()
            print(message)
            if board_stages_id_by_name[message] == target_idx:
                break
            time.sleep(0.100)
        self.__conn__.read(400)
        
    def reset(self):
        print("reset")

        self.__go_to_stage(board_stages_id_by_name[b'Starting - Press\r\n'])
    
    def next_stage(self):
        print("next stage")

        self.__conn__.write(b"\n")
        message = self.__conn__.readline()
        return message
    
    def close(self):
        print("closing board")
        self.__conn__.close()



