
import asyncio
from constants import dummy_inputs, stages_map_ad2, stages_map_ad3
from Board.BoardManager import BoardManager
from SerialDevs import UT61E
# This function will call the board and switch the relays to next state


async def switch_relays_ad2(bm, expected_state: str):
    # Should return confirmation that relays have been switched
    # to expected state
    # True if relays are in new state, false otherwise
    if expected_state == stages_map_ad2["2. Waveform Generator 1 Low Gain"]:
        print("[Info] Switching relay...")
        newState = bm.next_stage()
        print(f"[Info] Relay switched to state: {newState}")

    elif expected_state == stages_map_ad2["4. Waveform Generator 2 Low Gain"]:
        newState = bm.next_stage()
        print(f"[Info] Relay switched to state: {newState}")
    elif expected_state == stages_map_ad2["6. Oscilloscope"]:
        newState = bm.next_stage()
        print(f"[Info] Relay switched to state: {newState}")
    elif expected_state == stages_map_ad2["7. Positive Supply"]:
        newState = bm.next_stage()
        print(f"[Info] Relay switched to state: {newState}")
    elif expected_state == stages_map_ad2["8. Negative Supply"]:
        newState = bm.next_stage()
        print(f"[Info] Relay switched to state: {newState}")
    return True

async def switch_relays_ad3(bm, expected_state: str):
    print("switch to " + str(expected_state))
    # Should return confirmation that relays have been switched
    # to expected state
    # True if relays are in new state, false otherwise
    if expected_state == stages_map_ad3["1. Waveform Generator 1 Low Range"]:
        print("[Info] Switching relay...")
        newState = bm.next_stage()
        print(f"[Info] Relay switched to state: {newState}")

    elif expected_state == stages_map_ad3["3. Waveform Generator 2 Low Range"]:
        newState = bm.next_stage()
        print(f"[Info] Relay switched to state: {newState}")
    elif expected_state == stages_map_ad3["5. Oscilloscope"]:
        newState = bm.next_stage()
        print(f"[Info] Relay switched to state: {newState}")
    elif expected_state == stages_map_ad3["7. Positive Supply"]:
        newState = bm.next_stage()
        print(f"[Info] Relay switched to state: {newState}")
    elif expected_state == stages_map_ad3["8. Negative Supply"]:
        newState = bm.next_stage()
        print(f"[Info] Relay switched to state: {newState}")
    return True

def reset_dummy():
    global idx
    idx = 0