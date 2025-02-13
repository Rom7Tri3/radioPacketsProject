#Takes bits, modulatets bits to .wav, demodulates .wav to bits, returns bits.

import json
import numpy as np
import scipy.signal as signal
import scipy.io.wavfile as wav
import sounddevice as sd

# Load configuration
with open("config.json", "r") as f:
    config = json.load(f)

fs = config["fs"]  # Sampling rate
baud_rate = config["baud_rate"]  # Symbol rate
samples_per_symbol = fs // baud_rate
carrier_freq = config["carrier_freq"]  # Carrier frequency
qam_order = config["qam_order"]  # QAM order

# Generate QAM Constellation
def generate_qam_constellation(order):
    m = int(np.sqrt(order))
    real = np.arange(-m + 1, m, 2)
    imag = np.arange(-m + 1, m, 2) * 1j
    constellation = np.array([x + y for x in real for y in imag])
    constellation /= np.sqrt((constellation.real**2 + constellation.imag**2).mean())  # Normalize power
    return constellation

constellation = generate_qam_constellation(qam_order)

# Mapping bits to symbols
def bits_to_symbols(bits):
    bits = np.array(bits)  # Ensure it's a NumPy array
    num_bits_per_symbol = int(np.log2(qam_order))
    assert len(bits) % num_bits_per_symbol == 0, "Bit length must be a multiple of symbol size."

    # Reshape bits into groups of log2(QAM order)
    bit_groups = bits.reshape(-1, num_bits_per_symbol)

    # Convert binary groups to decimal values
    decimal_values = np.dot(bit_groups, 2**np.arange(num_bits_per_symbol)[::-1])

    # Ensure values map correctly within constellation bounds
    assert np.all(decimal_values < qam_order), "Index out of range for constellation."

    return constellation[decimal_values]


# Modulate to waveform
def qam_modulate(bits):
    symbols = bits_to_symbols(bits)
    time = np.arange(len(symbols) * samples_per_symbol) / fs
    upsampled = np.zeros(len(symbols) * samples_per_symbol, dtype=np.complex64)
    upsampled[::samples_per_symbol] = symbols
    pulse = signal.firwin(101, 1.0/samples_per_symbol, window="hamming")
    shaped_signal = np.convolve(upsampled, pulse, mode='same')
    carrier = np.exp(2j * np.pi * carrier_freq * time)
    modulated_signal = np.real(shaped_signal * carrier)
    return modulated_signal

# Demodulate from recorded waveform
def qam_demodulate(signal_rx):
    time = np.arange(len(signal_rx)) / fs
    carrier = np.exp(-2j * np.pi * carrier_freq * time)
    mixed_signal = signal_rx * carrier
    lowpass = signal.firwin(101, 1.0/samples_per_symbol, window="hamming")
    baseband = np.convolve(mixed_signal, lowpass, mode='same')
    symbols_rx = baseband[::samples_per_symbol]

    # Demodulation (nearest constellation point)
    distances = np.abs(symbols_rx[:, None] - constellation)
    decoded_symbols = np.argmin(distances, axis=1)
    decoded_bits = np.unpackbits(decoded_symbols.astype(np.uint8)[:, None], axis=1)[:, -int(np.log2(qam_order)):]
    return decoded_bits.flatten()

# Save to .wav
def save_wav(filename, signal):
    wav.write(filename, fs, np.int16(signal * 32767))

# Record from microphone
def record_wav(duration):
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    return recording[:, 0]

# Example Usage
if __name__ == "__main__":
    message_bits = np.random.randint(0, 2, 1000)  # Example random bits
    modulated_signal = qam_modulate(message_bits)
    save_wav("qam_output.wav", modulated_signal)

    print("Playing modulated signal...")
    sd.play(modulated_signal, samplerate=fs)
    sd.wait()

    print("Recording received signal...")
    received_signal = record_wav(duration=len(modulated_signal) / fs)

    print("Demodulating received signal...")
    recovered_bits = qam_demodulate(received_signal)

    print(f"Bit error rate: {np.mean(message_bits != recovered_bits)}")