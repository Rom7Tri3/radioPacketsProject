import numpy as np
import soundfile as sf
from scipy.signal import spectrogram


def demodulate(filename, baud=100, sample_rate=48000):
    """
    Decodes a .wav file into a sequence of bits based on detected tones.

    Parameters:
    - filename: Name of the input .wav file
    - baud: Symbol rate (symbols per second)
    - sample_rate: Sampling rate in Hz

    Returns:
    - List of decoded bits
    """
    # Load the audio file
    signal, sr = sf.read(filename)

    if sr != sample_rate:
        raise ValueError(f"Sample rate of the file ({sr}) doesn't match the expected sample rate ({sample_rate}).")

    # Define tone-to-bit mapping
    reverse_mapping = {
        1500: (0, 0),
        2000: (0, 1),
        2500: (1, 0),
        3000: (1, 1),
    }

    # Calculate the number of samples per symbol
    samples_per_symbol = int(sample_rate / baud)

    # Ensure the signal length is a multiple of samples_per_symbol
    signal = signal[:len(signal) // samples_per_symbol * samples_per_symbol]

    # Reshape the signal into chunks of samples_per_symbol
    reshaped_signal = signal.reshape(-1, samples_per_symbol)

    decoded_bits = []
    for symbol in reshaped_signal:
        # Compute the spectrogram of the symbol (chunk)
        f, t, Sxx = spectrogram(symbol, fs=sample_rate, nperseg=samples_per_symbol)

        # Identify the dominant frequency for the current symbol
        dominant_freq = f[np.argmax(Sxx)]

        # Find the closest frequency in the reverse_mapping
        closest_freq = min(reverse_mapping.keys(), key=lambda x: abs(x - dominant_freq))

        # Add the corresponding bits to the decoded sequence
        decoded_bits.extend(reverse_mapping[closest_freq])

    return decoded_bits

# Example usage
# decoded_bits = demodulate("output.wav")
# print("Decoded bits:", decoded_bits)
