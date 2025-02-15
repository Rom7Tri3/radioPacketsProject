import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

# Parameters (these can be read from a config file)
sampling_rate = 48000  # Hz
symbol_rate = 10  # Symbols per second
samples_per_symbol = sampling_rate // symbol_rate
carrier_frequency = 500  # Hz


# Mapping bits to 4-QAM symbols (In-phase, Quadrature)
def bits_to_symbols(bits):
    symbols = []
    for i in range(0, len(bits), 2):  # Process bits in pairs (2 bits per symbol)
        bit_pair = bits[i:i + 2]
        if bit_pair == [0, 0]:
            symbols.append((-1, -1))
        elif bit_pair == [0, 1]:
            symbols.append((-1, 1))
        elif bit_pair == [1, 0]:
            symbols.append((1, -1))
        elif bit_pair == [1, 1]:
            symbols.append((1, 1))
    return symbols


# Modulation function (Generate a signal and save it as a .wav file)
def modulate(bits, filename='output.wav'):
    symbols = bits_to_symbols(bits)
    t = np.arange(0, len(symbols) * samples_per_symbol) / sampling_rate
    signal = np.zeros(len(t))

    for i, (I, Q) in enumerate(symbols):
        carrier = np.cos(2 * np.pi * carrier_frequency * t[i * samples_per_symbol:(i + 1) * samples_per_symbol])
        # Combine In-phase (I) and Quadrature (Q) components
        signal[i * samples_per_symbol:(i + 1) * samples_per_symbol] = I * carrier + Q * np.sin(
            2 * np.pi * carrier_frequency * t[i * samples_per_symbol:(i + 1) * samples_per_symbol])

    # Normalize the signal to the range of 16-bit integers
    signal_int16 = np.int16(signal / np.max(np.abs(signal)) * 32767)

    # Save the signal to a .wav file
    write(filename, sampling_rate, signal_int16)

    print(f"Signal saved as {filename}")
