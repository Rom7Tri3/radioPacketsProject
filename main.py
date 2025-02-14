import modulation
import demodulation
import audio_helper as ah
import numpy as np
import os


def string_to_bits(s):
    return [int(b) for char in s.encode('utf-8') for b in format(char, '08b')]


def bits_to_string(bits):
    byte_chunks = [bits[i:i + 8] for i in range(0, len(bits), 8)]
    return bytes(int(''.join(map(str, byte)), 2) for byte in byte_chunks).decode('utf-8', errors='ignore')

def calculate_ber(original_bits, decoded_bits):
    """Calculates the Bit Error Rate (BER) between two bit sequences."""
    if len(original_bits) != len(decoded_bits):
        print("Warning: Bit sequences have different lengths! Truncating to match the shorter one.")
        min_length = min(len(original_bits), len(decoded_bits))
        original_bits = original_bits[:min_length]
        decoded_bits = decoded_bits[:min_length]

    errors = sum(1 for o, d in zip(original_bits, decoded_bits) if o != d)
    ber = errors / len(original_bits)
    return ber



if __name__ == "__main__":
    input_string = input("User input: ")
    bits = string_to_bits(input_string)
    print("Original Bits:", bits)

    # Modulate and save to file
    modulation.modulate(bits, filename="output.wav", baud=50, sample_rate=48000)
    if not os.path.exists("output.wav"):
        raise FileNotFoundError("The file 'output.wav' was not created. Check modulation module.")

    # Add preamble
    ah.add_tone_preamble("output.wav", "with_preamble.wav")

    # Play sound
    ah.play_wav('with_preamble.wav')

    # Remove preamble
    ah.remove_tone_preamble("with_preamble.wav", "cleaned.wav")

    # Demodulate from file
    decoded_bits = demodulation.demodulate("cleaned.wav", baud=50, sample_rate=48000)
    print("Decoded Bits:", decoded_bits)

    # Convert back to string
    output_string = bits_to_string(decoded_bits)
    print("Decoded String:", output_string)

    print(calculate_ber(bits, decoded_bits))