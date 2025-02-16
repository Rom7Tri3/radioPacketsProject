import modulation
import demodulation
import audio_helper as ah
import numpy as np
import os
import FEC as ec


def to_bits(text):
    return [int(bit) for char in text for bit in format(ord(char), '08b')]


def bits_to(bits):
    chars = [chr(int("".join(map(str, bits[i:i + 8])), 2)) for i in range(0, len(bits), 8)]
    return "".join(chars)

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

def get_data_after_pattern(binary_array):

    print("Nothing")
    return binary_array

def binary_array_to_string(binary_array):
    if all(isinstance(b, int) for b in binary_array):  # Ensure it's a list of 0s and 1s
        binary_string = ''.join(map(str, binary_array))
        byte_array = [int(binary_string[i:i+8], 2) for i in range(0, len(binary_string), 8)]
        return ''.join(chr(b) for b in byte_array if 32 <= b <= 126)  # ASCII filtering
    else:
        return ''.join(chr(int(b, 2)) for b in binary_array)

def flip_bits(bits):
    return [1 - bit for bit in bits]


if __name__ == "__main__":
    input_string = input("User input: ")
    input_string = "BEGIN: " + input_string


    bits = to_bits(input_string)
    print("Original Bits:", bits)
    print("Length: ", len(bits))

    # Modulate and save to file
    modulation.modulate(bits, "output.wav")
    if not os.path.exists("output.wav"):
        raise FileNotFoundError("The file 'output.wav' was not created. Check modulation module.")

    # Add preamble
    ah.add_tone_preamble("output.wav", "with_preamble.wav")

    # Play sound
    ah.play_wav('with_preamble.wav')

    # Remove preamble
    ah.clean_data('noise.wav', 'cleaned.wav')

    # Demodulate from file
    decoded_bits = demodulation.demodulate("cleaned.wav")
    flipped_bits = flip_bits(decoded_bits)

    print(decoded_bits)
    print("Received: ", binary_array_to_string(decoded_bits).replace("BEGIN: ", "").strip())
    print("Received: ", binary_array_to_string(flipped_bits).replace("BEGIN: ", "").strip())
    print("Decoded Bits:", decoded_bits)
    print("Flipped Decoded Bits: ", flipped_bits)
    print("Error rate of: ",calculate_ber(bits, decoded_bits))

