import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

#TODO: Add buffer simbols before and after message, create Package format i.e. Start message bit and end message bit.

#TODO: Increase to 4 or 8 bits. (Modular ?)

#TODO: FEC

#TODO: Python interface


# Parameters
fs = 44100
bit_duration = 0.01
carrier_freq = 1000
amplitude = 0.5

qam_map = {
    (0, 0): (1, 1),
    (0, 1): (1, -1),
    (1, 0): (-1, 1),
    (1, 1): (-1, -1)
}


def string_to_bits(input_string):
    """
    Converts a string to a list of bits.

    Input: A string (e.g., "Hello").
    Output: A list of bits representing the ASCII values of the characters in the string.
    """
    return [int(bit) for char in input_string for bit in f"{ord(char):08b}"]


def bits_to_string(bits):
    """
    Converts a list of bits back to a string.

    Input: A list of bits (e.g., [0, 1, 0, 0, 0, 0, 1, 0]).
    Output: The original string represented by the bits (e.g., "H").
    """
    chars = [chr(int("".join(map(str, bits[i:i + 8])), 2)) for i in range(0, len(bits), 8)]
    return "".join(chars)


def modulate(bits):
    """
    Modulates a list of bits into a QAM signal.

    Input: A list of bits (e.g., [0, 1, 0]).
    Output: A NumPy array representing the QAM-modulated signal.
    """
    if len(bits) % 2 != 0:
        bits.append(0)  # Padding with zero if odd number of bits

    signal = []
    for i in range(0, len(bits), 2):
        pair = (bits[i], bits[i + 1])
        I, Q = qam_map[pair]
        t = np.linspace(0, bit_duration, int(fs * bit_duration), endpoint=False)
        carrier_I = amplitude * I * np.cos(2 * np.pi * carrier_freq * t)
        carrier_Q = amplitude * Q * np.sin(2 * np.pi * carrier_freq * t)
        signal.extend(carrier_I + carrier_Q)
    return np.array(signal)


def demodulate(signal):
    """
    Demodulates a QAM signal back into a list of bits.

    Input: A NumPy array representing a QAM-modulated signal.
    Output: A list of bits extracted from the signal (e.g., [0, 1, 0]).
    """
    num_samples = int(fs * bit_duration)
    num_symbols = len(signal) // num_samples
    bits = []
    for i in range(num_symbols):
        chunk = signal[i * num_samples:(i + 1) * num_samples]
        t = np.linspace(0, bit_duration, num_samples, endpoint=False)
        ref_I = np.cos(2 * np.pi * carrier_freq * t)
        ref_Q = np.sin(2 * np.pi * carrier_freq * t)
        I = np.sum(chunk * ref_I)
        Q = np.sum(chunk * ref_Q)
        pair = (0 if I > 0 else 1, 0 if Q > 0 else 1)
        bits.extend(pair)
    return bits


def main():
    """
    Main function to demonstrate QAM modulation and demodulation.

    Input: None directly (hardcoded input string in the function).
    Output: Prints the input string, bits, demodulated bits, and reconstructed string. Saves a .wav file and plots the waveform.
    """
    input_string = "Hello World!"
    print(f"Input string: {input_string}")
    bits = string_to_bits(input_string)
    print(f"Bits: {bits}")

    qam_signal = modulate(bits)
    audio_file = "qam_signal.wav"
    sf.write(audio_file, qam_signal, fs)
    print(f"QAM signal saved to {audio_file}")

    received_signal, _ = sf.read(audio_file)
    demodulated_bits = demodulate(received_signal)
    print(f"Demodulated bits: {demodulated_bits}")
    output_string = bits_to_string(demodulated_bits)
    print(f"Demodulated string: {output_string}")


if __name__ == "__main__":
    main()

