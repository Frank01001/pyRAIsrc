import signal_utils
import numpy as np
import scipy.io.wavfile as wav


def get_sequence_from_frames(frame1, frame2):
    sequence = ''

    for i in range(32):
        sequence += '1' if frame1[i] is True else '0'

    sequence += ' '

    for i in range(16):
        sequence += '1' if frame2[i] is True else '0'


def generate_waveform(frame1, frame2, sampling_rate, amplitude):
    N = int(signal_utils.total_signal_duration / 1000 * sampling_rate)
    waveform = np.zeros(N, dtype=np.float32)

    period = 1.0 / sampling_rate

    bit_N = int(signal_utils.bit_duration / 1000 * sampling_rate)
    bit_samples = np.arange(0, bit_N * period, period).astype(np.float32)
    low_30ms = np.cos(2.0 * np.pi * signal_utils.low_freq * bit_samples) * amplitude
    high_30ms = np.cos(2.0 * np.pi * signal_utils.high_freq * bit_samples) * amplitude

    # First frame
    for i in range(32):
        t = i * bit_N
        tp = t + bit_N

        pitch = high_30ms if frame1[i] == 1 else low_30ms
        waveform[t:tp] = pitch

    # Second frame starts at second 53
    k = 1 * sampling_rate

    # Second frame
    for i in range(16):
        t = k + i * bit_N
        tp = t + bit_N

        pitch = high_30ms if frame2[i] == 1 else low_30ms
        waveform[t:tp] = pitch

    # Sync beeps
    sync_N = int(signal_utils.sync_duration / 1000 * sampling_rate)
    sync_samples = np.arange(0, sync_N * period, period).astype(np.float32)
    sync_wave = np.cos(2 * np.pi * signal_utils.sync_freq * sync_samples) * amplitude

    k = 2 * sampling_rate

    for i in range(5):
        t = k + i * sampling_rate
        tp = t + sync_N

        waveform[t:tp] = sync_wave

    # Final sync
    waveform[-sync_N:] = sync_wave

    return waveform


def save_waveform_to_file(waveform, file_path, sampling_rate=44100):
    wav.write(file_path, sampling_rate, waveform.astype(np.float32))
