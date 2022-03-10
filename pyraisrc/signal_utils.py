import numpy as np

low_freq = 2e+3  # Hz
high_freq = 2.5e+3  # Hz
sync_freq = 1.0e+3  # Hz

bit_duration = 30 # ms
pause_between_frames = 40 # ms
pause_to_sync = 520 # ms
total_signal_duration = 8.1e+3 # ms
sync_duration = 0.1e+3 # ms


'''
Returns a band-pass filter around the frequency with a band of twice the interval
'''
def freq_filter(frequency, freq_obj, interval = 100):
    buffer = np.zeros(freq_obj.size)
    mask_1 = freq_obj >= frequency - interval
    mask_2 = freq_obj <= frequency + interval
    mask = np.logical_and(mask_1, mask_2)
    buffer[mask] = 1.0
    return buffer


'''
Returns the index of the closest frequency of the discrete time spectrum
'''
def get_closest_frequency_index(freq, freq_obj):
    for i in range(freq_obj - 1):
        if freq_obj[i] <= freq < freq_obj[i + 1]:
            return i

    # Could not reach frequency
    return -1


'''
Used to compute the value of coded integers within the SRC signal
'''
def coded_integer(value, bit_values):
    N = bit_values.size
    code = np.zeros(N, dtype=bool)

    buffer = value

    for k in range(N):
        if buffer > bit_values[k]:
            buffer -= bit_values[k]
            code[k] = True

    return code
