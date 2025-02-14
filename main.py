import modulation
import demodulation
import audio_helper as ah
import numpy as np
import os
import FEC as ec


def to_bits(barr):
    return [int(b) for byte in barr for b in format(byte, '08b')]


def bits_to(bits):
    byte_values = [int(''.join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    return bytearray(byte_values)

def extract_ascii_string(byte_data):
    return ''.join(chr(b) for b in byte_data if 32 <= b <= 126)

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

    # ReedSolo encode
    message = ec.encode_reed_solomon(input_string)

    bits = to_bits(message)
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
    ah.clean_data('with_preamble.wav', 'cleaned.wav')

    # Demodulate from file
    decoded_bits = demodulation.demodulate("cleaned.wav", baud=50, sample_rate=48000)
    ec.decode_reed_solomon(bits_to(decoded_bits))
    print("Decoded Bits:", decoded_bits)

    # Convert back to string
    output_string = extract_ascii_string(bits_to(decoded_bits))

    print("Decoded String:", output_string)

    print(calculate_ber(bits, decoded_bits))


