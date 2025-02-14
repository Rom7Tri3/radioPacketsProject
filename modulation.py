import numpy as np
import soundfile as sf


def modulate(bits, filename="output.wav", baud=100, sample_rate=48000):
    """
    Maps a sequence of bits to tones and saves as a .wav file.

    Parameters:
    - bits: List of bits (0s and 1s)
    - filename: Name of the output .wav file
    - baud: Symbol rate (symbols per second)
    - sample_rate: Sampling rate in Hz
    """
    symbol_duration = 1 / baud  # Duration of each symbol in seconds
    samples_per_symbol = int(sample_rate * symbol_duration)

    # Define bit-to-tone mapping
    mapping = {
        (0, 0): 1500,
        (0, 1): 2000,
        (1, 0): 2500,
        (1, 1): 3000,
    }

    # Ensure bits array length is even
    if len(bits) % 2 != 0:
        bits.append(0)  # Pad with zero if odd

    # Convert bits to symbols (pairs of bits)
    symbols = [tuple(bits[i:i + 2]) for i in range(0, len(bits), 2)]

    # Generate waveform
    waveform = np.concatenate([
        np.sin(2 * np.pi * mapping[symbol] * np.arange(samples_per_symbol) / sample_rate)
        for symbol in symbols
    ])

    # Normalize waveform to avoid clipping
    waveform = 0.8 * waveform

    # Save to WAV file
    sf.write(filename, waveform, sample_rate)
    print(f"Saved {filename} with {len(symbols)} symbols.")


# Example usage
# modulate([0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0])