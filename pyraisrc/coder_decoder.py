import numpy as np
import signal_utils
from information_block import InformationBlock


'''
Returns the signal frames (separately) as bool numpy arrays
'''
def string_to_binary_frames(string: str):
    if len(string) != (32 + 16 + 1):
        raise Exception('Invalid string size')

    frame1 = np.zeros(32, dtype=bool)
    frame2 = np.zeros(16, dtype=bool)

    # First frame conversion
    for i in range(32):
        char = string[i]

        if char == '0':
            frame1[i] = False
        elif char == '1':
            frame1[i] = True
        else:
            raise Exception('Invalid String: Unrecognized character \'{}\''.format(char))

    # Check for space
    if string[32] != ' ':
        raise Exception('Invalid String: Unrecognized character \'{}\''.format(string[32]))

    # Second frame conversion
    for i in range(33, 33 + 16):
        char = string[i]

        if char == '0':
            frame2[i - 33] = False
        elif char == '1':
            frame2[i - 33] = True
        else:
            raise 'Unrecognized character \'{}\''.format(char)

    return frame1, frame2


# FRAME 1 BITS
ID_F1 = [0, 1]
OR = range(2, 8)
MI = range(8, 15)
OE = 15
P1 = 16
ME = range(17, 22)
GM = range(22, 28)
GS = range(28, 31)
P2 = 31

ID_F1_VALUE = np.array([False, True])
OR_VALUES = np.array([20, 10, 8, 4, 2, 1])
MI_VALUES = np.array([40, 20, 10, 8, 4, 2, 1])
ME_VALUES = np.array([10, 8, 4, 2, 1])
GM_VALUES = np.array([20, 10, 8, 4, 2, 1])
GS_VALUES = np.array([4, 2, 1])

# FRAME 2 BITS
ID_F2 = [0, 1]
AN = range(2, 10)
SE = [10, 11, 12]
SI = [13, 14]
PA = 15

ID_F2_VALUE = np.array([True, False])
AN_VALUES = np.array([80, 40, 20, 10, 8, 4, 2, 1])
SE_VALUES = np.array([4, 2, 1])

'''
Returns an InformationBlock object containing all SRC information contained in the input binary string
raises exceptions in case of inconsistencies (ID bits and parity)
'''
def decode(binary_string: str):
    frame1, frame2 = string_to_binary_frames(binary_string)

    # Check ID bits for both frames
    id1_check = (frame1[ID_F1] != ID_F1_VALUE)
    id2_check = (frame2[ID_F2] != ID_F2_VALUE)
    check_all = np.sum(id1_check) + np.sum(id2_check)
    if check_all > 0:
        print('Frame 1 ID: {}  | Frame 2 ID: {}'.format(frame1[ID_F1], frame2[ID_F2]))
        raise Exception('Invalid Rai SRC: At least one of the frame IDs is wrong')

    # Frame 1 decoding
    hour = np.dot(frame1[OR], OR_VALUES)
    minutes = np.dot(frame1[MI], MI_VALUES)

    is_cest = frame1[OE]

    parity_1 = np.sum(frame1[0:16]) % 2 == 0  # Odd parity

    if parity_1 != frame1[P1]:
        raise Exception('Invalid Rai SRC: P1 parity bit is incorrect')

    month = np.dot(frame1[ME], ME_VALUES)
    day = np.dot(frame1[GM], GM_VALUES)
    day_of_week = np.dot(frame1[GS], GS_VALUES)

    parity_2 = np.sum(frame1[17:31]) % 2 == 0  # Odd parity

    if parity_2 != frame1[P2]:
        raise Exception('Invalid Rai SRC: P2 parity bit is incorrect')

    # Frame 2 decoding
    year = np.dot(frame2[AN], AN_VALUES)
    time_to_next_time_zone_change = np.dot(frame2[SE], SE_VALUES)  # If more than 7 days, equal to 7
    leap_second_bits = frame2[SI]
    warning_leap_second = +1 * leap_second_bits[0] - 2 * leap_second_bits[1]
    parity = np.sum(frame2[0:15]) % 2 == 0  # Odd parity

    if parity != frame1[PA]:
        raise Exception('Invalid Rai SRC: PA parity bit is incorrect')

    info_block = InformationBlock()
    info_block.set_time(hour, minutes)
    info_block.set_date(day, month, year, day_of_week)
    info_block.set_time_zone(is_cest)
    info_block.set_next_time_zone_change(time_to_next_time_zone_change)
    info_block.set_leap_second(warning_leap_second)
    return info_block


'''
Returns the two frames (separately) as bool numpy arrays given the input InformationBlock
'''
def encode(info_block : InformationBlock):
    frame1 = np.zeros(32, dtype=bool)
    frame2 = np.zeros(16, dtype=bool)

    # Frame 1
    frame1[1] = True
    frame1[OR] = signal_utils.coded_integer(info_block.hour, OR_VALUES)
    frame1[MI] = signal_utils.coded_integer(info_block.minutes, MI_VALUES)
    frame1[OE] = info_block.time_zone == 'CEST'
    frame1[P1] = np.sum(frame1[0:16]) % 2 == 0 # Odd parity
    frame1[ME] = signal_utils.coded_integer(info_block.month, ME_VALUES)
    frame1[GM] = signal_utils.coded_integer(info_block.day, GM_VALUES)
    frame1[GS] = signal_utils.coded_integer(info_block.day_of_week, GS_VALUES)
    frame1[P2] = np.sum(frame1[17:31]) % 2 == 0  # Odd parity

    # Frame 2
    frame2[0] = True
    year_b = info_block.year

    # SRC year bits only have two digits (ambiguity)
    if year_b > 2000:
        year_b -= 2000
    else:
        year_b -= 1900

    frame2[AN] = signal_utils.coded_integer(year_b, AN_VALUES)

    tz_change = info_block.next_tz_change
    # internal representation of tz_change >= 7 in the InformationBlock is -1
    if tz_change < 0:
        tz_change = 7

    frame2[SE] = signal_utils.coded_integer(tz_change, SE_VALUES)

    # Leap second encoding
    if info_block.leap_second < 0:
        frame2[SI] = np.array([True, True])
    elif info_block.leap_second > 0:
        frame2[SI] = np.array([True, False])
    else:
        frame2[SI] = np.zeros(2, dtype=bool)

    frame2[PA] = np.sum(frame2[0:15]) % 2 == 0  # Odd parity

    return frame1, frame2


