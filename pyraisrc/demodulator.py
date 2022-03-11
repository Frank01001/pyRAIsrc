from scipy.io.wavfile import read
from numpy.fft import fft, ifft, fftfreq
from pyraisrc.signal_utils import *
import numpy as np
import matplotlib.pyplot as plt

'''
Prints basic file information: sample rate and encoding type
'''
def print_file_info(file_path):
    sampling_freq, data = read(file_path)
    print('Opened file ' + file_path + ' with sample rate ' + str(sampling_freq) + ' of ' + str(data.dtype))


'''
Returns string of binary digits from SRC in file.
If the file was generated with no noise or delay, perferct_generation should be set to True
'''
def get_sequence_from_file(file_path, perfect_generation=False):
    sampling_freq, data = read(file_path)

    sampling_period = 1 / sampling_freq

    # Number of samples for a single bit (30 ms)
    bit_N = int(bit_duration / 1000 * sampling_freq)
    bit_samples = np.arange(0, bit_N * sampling_period, sampling_period).astype(np.float32)
    search_step_samples = int(5 / 1000 * sampling_freq)

    sequence_buffer = ''

    # Start of signal has to be searched if the source sound file isn't perfect
    signal_start_index = -1

    if not perfect_generation:

        period = 1.0 / sampling_freq

        # 30 ms long cos waves are precalculated and applied when needed
        bit_N = int(bit_duration / 1000 * sampling_freq)
        low_30ms = np.cos(2.0 * np.pi * low_freq * bit_samples)
        high_30ms = np.cos(2.0 * np.pi * high_freq * bit_samples)
        target = np.concatenate([low_30ms, high_30ms])

        window_N = target.size
        window_count = data.size // window_N
        first_cov = 0.0
        minimum_cov = 7e-4

        for w in range(window_count):
            w_beg = w * window_N
            w_end = w_beg + window_N
            cov = np.cov(data[w_beg:w_end], target)[0, 1]
            if w == 0:
                first_cov = cov

            if cov > max(50.0 * first_cov, minimum_cov):
                signal_start_index = w_beg + int(10 / 1000 * sampling_freq)
                break

        print('Signal starts at {} seconds'.format(signal_start_index / sampling_freq))

        if signal_start_index < 0:
            raise Exception('Could not find start of signal!')
    else:
        signal_start_index = 0

    # After the start of the signal has been evaluated, filter with band-pass filters
    signal = data[signal_start_index:]
    freq_signal = fftfreq(signal.size, sampling_period)
    sig_fft = fft(signal)

    filter_2k = freq_filter(low_freq, freq_signal, interval=100)
    filter_2_5k = freq_filter(high_freq, freq_signal, interval=100)

    data_2k = np.real(ifft(filter_2k * sig_fft))
    data_2_5k = np.real(ifft(filter_2_5k * sig_fft))

    # First frame
    num_windows = 32
    for w in range(num_windows):
        lower_bound = int(w * bit_N)
        upper_bound = int((w + 1) * bit_N)
        # The prominent frequency is the one with the highest variance
        variance_2k = np.var(data_2k[lower_bound:upper_bound])
        variance_2_5k = np.var(data_2_5k[lower_bound:upper_bound])

        # Append corresponding bit
        if variance_2k > variance_2_5k:
            sequence_buffer += '0'
        else:
            sequence_buffer += '1'

    sequence_buffer += ' '

    # Second frame
    num_windows = 16
    start_frame = 1.0 * sampling_freq
    for w in range(num_windows):
        lower_bound = int(start_frame + w * bit_N)
        upper_bound = int(start_frame + (w + 1) * bit_N)
        # The prominent frequency is the one with the highest variance
        variance_2k = np.var(data_2k[lower_bound:upper_bound])
        variance_2_5k = np.var(data_2_5k[lower_bound:upper_bound])

        # Append corresponding bit
        if variance_2k > variance_2_5k:
            sequence_buffer += '0'
        else:
            sequence_buffer += '1'

    return sequence_buffer


'''
Plots the waveform, filtered 0 bits and 1 bits, noise spectrum (when applicable), filtered sync beeps
'''
def plot_from_file(file_path):
    sampling_freq, data = read(file_path)

    sampling_period = 1 / sampling_freq

    freq_space = fftfreq(data.size, sampling_period)

    # Signal Spectrum
    sig_fft = fft(data)

    # Band-pass filters for 2.0k, 2.5k and 1.0k frequencies
    low_filter = freq_filter(low_freq, freq_space)
    high_filter = freq_filter(high_freq, freq_space)
    sync_filter = freq_filter(sync_freq, freq_space)

    # Processed signals
    data_2k = np.real(ifft(low_filter * sig_fft))
    data_2_5k = np.real(ifft(high_filter * sig_fft))
    data_1k = np.real(ifft(sync_filter * sig_fft))

    # Noise evaluation (relevant only if the initial signal is not ideal)
    noise_extract = data[0:int(10 / 1000 * sampling_freq)]
    noise_freq_space = fftfreq(noise_extract.size, sampling_period)
    pos_noise_freq_space = noise_freq_space[:int(noise_freq_space.size / 2)]
    noise_sig_real_dft = np.real(fft(noise_extract))[:pos_noise_freq_space.size]

    # Plots
    time_domain_x_axis = np.array([i * sampling_period for i in range(data.size)])
    fig, axs = plt.subplots(3, 2, figsize=(20, 18))
    axs[0, 0].plot(time_domain_x_axis, data)
    axs[0, 0].set_title('Initial Signal')
    axs[1, 0].plot(time_domain_x_axis, data_2k)
    axs[1, 0].set_title('Filtered 0s')
    axs[1, 1].plot(time_domain_x_axis, data_2_5k)
    axs[1, 1].set_title('Filtered 1s')
    axs[2, 0].plot(time_domain_x_axis, data_1k)
    axs[2, 0].set_title('Filtered sync beeps')
    axs[2, 1].plot(pos_noise_freq_space, noise_sig_real_dft)
    axs[2, 1].set_xlim(0,4000)
    axs[2, 1].set_title('Noise spectrum (ignore if perfect generation)')
    fig.tight_layout(pad=5.0)
    plt.show()
