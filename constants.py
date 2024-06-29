stages_map_ad2 = {
    "0. Start": 0,
    "1. Waveform Generator Linearity": 1,
    "2. Waveform Generator 1 Low Gain": 2,
    "3. Waveform Generator 1 High Gain": 3,
    "4. Waveform Generator 2 Low Gain": 4,
    "5. Waveform Generator 2 High Gain": 5,
    "6. Oscilloscope": 6,
    "7. Positive Supply": 7,
    "8. Negative Supply": 8,
    "9. End": 9
}

stages_map_ad3 = {
    "0. Start": 0,
    "1. Waveform Generator 1 Low Range": 1,
    "2. Waveform Generator 1 High Range": 2,
    "3. Waveform Generator 2 Low Range": 3,
    "4. Waveform Generator 2 High Range": 4,
    "5. Oscilloscope": 5,
    "6. Frequency Compensation": 6,
    "7. Positive Supply": 7,
    "8. Negative Supply": 8,
    "9. End": 9
}

dummy_inputs = [
    0,
    1,
    -1,
    5,
    -5,
    #
    0, 
    5,
    -5,
    5,
    -5,
    # WG2 LG
    0,
    1,
    -1,
    5,
    -5,
    # WG2 HG
    0,
    5,
    -5,
    5,
    -5,
    # OSC:
         
]