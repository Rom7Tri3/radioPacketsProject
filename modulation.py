import numpy as np
from scipy.io.wavfile import write

# 🎛️ Configuration Parameters
sampling_rate = 48000  # Hz
symbol_rate = 10  # Symbols per second
samples_per_symbol = sampling_rate // symbol_rate
carrier_frequency = 500  # Hz

# 🎯 Converts a string to a list of bits
def to_bits(text):
    return [int(bit) for char in text for bit in format(ord(char), '08b')]

# 🔄 Converts a list of bits back to a string
def bits_to_string(bits):
    return "".join(chr(int("".join(map(str, bits[i:i + 8])), 2)) for i in range(0, len(bits), 8))

# 📉 Calculates the Bit Error Rate (BER)
def calculate_ber(original_bits, decoded_bits):
    min_length = min(len(original_bits), len(decoded_bits))
    errors = sum(o != d for o, d in zip(original_bits[:min_length], decoded_bits[:min_length]))
    return errors / min_length if min_length > 0 else 0

# 🔢 Converts a binary array into bytes
def binary_array_to_bytes(binary_array):
    if len(binary_array) % 8 != 0:
        binary_array.extend([0] * (8 - len(binary_array) % 8))
    return bytes(int("".join(map(str, binary_array[i:i + 8])), 2) for i in range(0, len(binary_array), 8))

# 🔄 Flips all bits in an array (0 → 1, 1 → 0)
def flip_bits(bits):
    return [1 - bit for bit in bits]

# 🔢 Mapping bits to 4-QAM symbols
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

# 📡 Modulation function (Generate signal and save as .wav)
def modulate(bits, filename='output.wav'):
    symbols = bits_to_symbols(bits)
    t = np.arange(0, len(symbols) * samples_per_symbol) / sampling_rate
    signal = np.zeros(len(t))

    for i, (I, Q) in enumerate(symbols):
        carrier = np.cos(2 * np.pi * carrier_frequency * t[i * samples_per_symbol:(i + 1) * samples_per_symbol])
        # Combine In-phase (I) and Quadrature (Q) components
        signal[i * samples_per_symbol:(i + 1) * samples_per_symbol] = I * carrier + Q * np.sin(
            2 * np.pi * carrier_frequency * t[i * samples_per_symbol:(i + 1) * samples_per_symbol])

    # Normalize signal to 16-bit integer range
    signal_int16 = np.int16(signal / np.max(np.abs(signal)) * 32767)
    write(filename, sampling_rate, signal_int16)
    print(f"📀 Signal saved as {filename}")