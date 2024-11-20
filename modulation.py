import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

# Parameters
fs = 48000
bit_duration = 0.01
carrier_freq = 1000
amplitude = 0.1

qam_map = {
    (0, 0, 0, 0): (3, 3),
    (0, 0, 0, 1): (3, 1),
    (0, 0, 1, 0): (3, -3),
    (0, 0, 1, 1): (3, -1),
    (0, 1, 0, 0): (1, 3),
    (0, 1, 0, 1): (1, 1),
    (0, 1, 1, 0): (1, -3),
    (0, 1, 1, 1): (1, -1),
    (1, 0, 0, 0): (-3, 3),
    (1, 0, 0, 1): (-3, 1),
    (1, 0, 1, 0): (-3, -3),
    (1, 0, 1, 1): (-3, -1),
    (1, 1, 0, 0): (-1, 3),
    (1, 1, 0, 1): (-1, 1),
    (1, 1, 1, 0): (-1, -3),
    (1, 1, 1, 1): (-1, -1),
}

def string_to_bits(input_string):
    """
    Converts a string into a list of bits.
    
    Input: A string (e.g., "Hello").
    Output: A list of bits representing the ASCII values of the characters in the string 
            (e.g., [0, 1, 0, 0, 1, 0, ...]).
    """
    return [int(bit) for char in input_string for bit in f"{ord(char):08b}"]

def bits_to_string(bits):
    """
    Converts a list of bits back into a string.
    
    Input: A list of bits (e.g., [0, 1, 0, 0, 1, 0, ...]).
    Output: A string reconstructed from the bits (e.g., "Hello").
    """
    chars = [chr(int("".join(map(str, bits[i:i + 8])), 2)) for i in range(0, len(bits), 8)]
    return "".join(chars)

def modulate(bits):
    """
    Modulates a list of bits into a QAM signal.
    
    Input: A list of bits (e.g., [0, 1, 0, 0, 1, 0, ...]).
    Output: A NumPy array representing the QAM-modulated signal.
    """
    if len(bits) % 4 != 0:
        bits.extend([0] * (4 - len(bits) % 4))  # Padding with zeros if not a multiple of 4

    signal = []
    for i in range(0, len(bits), 4):
        group = tuple(bits[i:i + 4])
        I, Q = qam_map[group]
        t = np.linspace(0, bit_duration, int(fs * bit_duration), endpoint=False)
        carrier_I = amplitude * I * np.cos(2 * np.pi * carrier_freq * t)
        carrier_Q = amplitude * Q * np.sin(2 * np.pi * carrier_freq * t)
        signal.extend(carrier_I + carrier_Q)
    return np.array(signal)

def demodulate(signal):
    """
    Demodulates a QAM signal back into a list of bits.
    
    Input: A NumPy array representing a QAM-modulated signal.
    Output: A list of bits extracted from the signal (e.g., [0, 1, 0, 0, 0, 1, 1, 0]).
    """
    num_samples = int(fs * bit_duration)
    num_symbols = len(signal) // num_samples
    bits = []

    for i in range(num_symbols):
        chunk = signal[i * num_samples:(i + 1) * num_samples]
        t = np.linspace(0, bit_duration, num_samples, endpoint=False)
        ref_I = np.cos(2 * np.pi * carrier_freq * t)
        ref_Q = np.sin(2 * np.pi * carrier_freq * t)
        # Calculate I and Q
        I = np.sum(chunk * ref_I) / (amplitude * num_samples)
        Q = np.sum(chunk * ref_Q) / (amplitude * num_samples)
        print(f"Raw {i}: I = {I}, Q = {Q}")
        I = clean_signal(I)
        Q = clean_signal(Q)

        # Clamp values to valid range [-3, -1, 1, 3]
        I = max(min(I, 3), -3)
        Q = max(min(Q, 3), -3)

        # Debugging intermediate values
        print(f"Symbol {i}: I = {I}, Q = {Q}")

        # Match to QAM map
        for key, value in qam_map.items():
            if value == (I, Q):
                bits.extend(key)
                break
        else:
            # Log unmatched pairs for debugging
            print(f"Unmatched I/Q pair: ({I}, {Q})")

    return bits

def clean_signal(value):
    """
    Rounds the given value to the closest value in {3, 1, -1, -3}.
    
    Input: A floating-point value representing a demodulated signal component.
    Output: An integer rounded to the nearest valid QAM value (e.g., -3, -1, 1, or 3).
    """
    if value < 0:
        value = value - 0.75
    else:
        value = value + 0.75

    targets = [3, 1, -1, -3]
    return min(targets, key=lambda x: abs(value - x))

def main():
    """
    Main function to test QAM modulation and demodulation.
    Converts a string to bits, modulates the bits into a QAM signal, writes the signal to a file, 
    reads the file, demodulates the signal, and converts the demodulated bits back into a string.
    """
    input_string = "Hello World!"
    print(f"Input string: {input_string}")
    bits = string_to_bits(input_string)
    print(f"Bits: {bits}")

    qam_signal = modulate(bits)
    audio_file = "qam_signal_16qam.wav"
    sf.write(audio_file, qam_signal, fs)
    print(f"QAM signal saved to {audio_file}")

    received_signal, _ = sf.read(audio_file)
    demodulated_bits = demodulate(received_signal)
    print(f"Demodulated bits: {demodulated_bits}")
    output_string = bits_to_string(demodulated_bits)
    print(f"Demodulated string: {output_string}")


if __name__ == "__main__":
    main()
