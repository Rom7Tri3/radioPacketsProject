import numpy as np
import soundfile as sf
import json



# Load parameters from JSON config file
def load_config(config_file='config.json'):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config


config = load_config()

sampling_rate = config["sampling_rate"]  # Hz
symbol_rate = config["symbol_rate"]  # symbols per second
samples_per_symbol = sampling_rate // symbol_rate
carrier_frequency = config["carrier_frequency"]  # Hz
qam_order = config["qam_order"]  # 2 for BPSK


# BPSK modulation: 0 -> +1, 1 -> -1
def modulate(bits):
    symbols = []
    for bit in bits:
        if bit == 0:
            symbols.append(1)  # +1 for bit 0
        else:
            symbols.append(-1)  # -1 for bit 1
    return symbols


def generate_waveform(symbols):
    # Time vector for one symbol
    t = np.linspace(0, 1 / symbol_rate, samples_per_symbol, endpoint=False)

    # Generate the waveform
    signal = np.array([])
    for symbol in symbols:
        # Generate the signal for each symbol (modulate the carrier)
        real_part = np.cos(2 * np.pi * carrier_frequency * t) * symbol
        signal = np.concatenate([signal, real_part])

    return signal


def save_wav(filename, signal):
    # Save the waveform to a .wav file
    sf.write(filename, signal, sampling_rate)


def demodulate(signal):
    # Resample signal to match the symbol rate
    symbol_time = 1 / symbol_rate
    t = np.linspace(0, symbol_time, samples_per_symbol, endpoint=False)

    bits = []
    for i in range(0, len(signal), samples_per_symbol):
        symbol_signal = signal[i:i + samples_per_symbol]
        # Calculate in-phase component
        in_phase = np.sum(symbol_signal * np.cos(2 * np.pi * carrier_frequency * t))

        # Decision rule for BPSK symbols
        if in_phase > 0:
            bits.append(0)
        else:
            bits.append(1)

    return bits


# Example usage:
bits = [0, 1, 0, 0, 1, 1, 0, 1]  # Example bit stream
symbols = modulate(bits)  # BPSK modulation
signal = generate_waveform(symbols)  # Generate audio waveform
save_wav('output.wav', signal)  # Save to .wav file

# Demodulate from the generated .wav file
audio_signal, _ = sf.read('output.wav')
demodulated_bits = demodulate(audio_signal)
print("Demodulated bits:", demodulated_bits)
