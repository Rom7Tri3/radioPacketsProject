import numpy as np
from scipy.io.wavfile import read

# Parameters (same as modulation)
sampling_rate = 48000  # Hz
symbol_rate = 10  # Symbols per second
samples_per_symbol = sampling_rate // symbol_rate
carrier_frequency = 500  # Hz


# 📡 Demodulation function (Extract bits from received .wav file)
def demodulate(filename):
    sample_rate, received_signal = read(filename)
    print(f"🎵 Sample Rate: {sample_rate} Hz")

    if received_signal.ndim > 1:
        received_signal = np.mean(received_signal, axis=1)  # Convert stereo to mono

    received_signal = received_signal / np.max(np.abs(received_signal))  # Normalize signal

    if sample_rate != sampling_rate:
        raise ValueError(f"🚨 Expected {sampling_rate} Hz, but got {sample_rate} Hz")

    t = np.arange(len(received_signal)) / sampling_rate
    bits = []

    for i in range(0, len(received_signal) - samples_per_symbol, samples_per_symbol):
        symbol_window = received_signal[i:i + samples_per_symbol]

        if len(symbol_window) < samples_per_symbol:
            break

        I = np.mean(symbol_window * np.cos(2 * np.pi * carrier_frequency * t[i:i + samples_per_symbol]))
        Q = np.mean(symbol_window * np.sin(2 * np.pi * carrier_frequency * t[i:i + samples_per_symbol]))

        bits.extend([1 if I > 0 else 0, 1 if Q > 0 else 0])

    return bits



