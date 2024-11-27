import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from itertools import product
import sounddevice as sd

# Parameters
fs = 48000
bit_duration = 0.1
carrier_freq = 300
amplitude = 0.05

qam_map = {}
values = [-15, -13, -11, -9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 11, 13, 15]
possible_tuples = list(product(values, repeat=2))
# Iterate over all 256 possible 8-bit combinations
for i in range(256):
    bits = f"{i:08b}"
    bit_tuple = tuple(map(int, bits))
    qam_map[bit_tuple] = possible_tuples[i]
#print(qam_map)

def string_to_bits(input_string):
    """
    Converts a string into a list of bits.
    """
    return [int(bit) for char in input_string for bit in f"{ord(char):08b}"]

def bits_to_string(bits):
    """
    Converts a list of bits back into a string.
    """
    chars = [chr(int("".join(map(str, bits[i:i + 8])), 2)) for i in range(0, len(bits), 8)]
    return "".join(chars)

def modulate(bits):
    """
    Modulates a list of bits into a QAM signal using 256-QAM.
    """
    if len(bits) % 8 != 0:
        bits.extend([0] * (8 - len(bits) % 8))  #Not sure if padding is even needed, sinde symbol is 8 bits

    signal = []
    for i in range(0, len(bits), 8):
        group = tuple(bits[i:i + 8])
        I, Q = qam_map[group]
        t = np.linspace(0, bit_duration, int(fs * bit_duration), endpoint=False)
        carrier_I = amplitude * I * np.cos(2 * np.pi * carrier_freq * t)
        carrier_Q = amplitude * Q * np.sin(2 * np.pi * carrier_freq * t)
        signal.extend(carrier_I + carrier_Q)
    return np.array(signal)

def demodulate(signal):
    """
    Demodulates a QAM signal back into a list of bits using 256-QAM.
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
        #print(I, Q)
        # Clamp I and Q to nearest valid values in the constellation
        I = clean_signal(I)
        Q = clean_signal(Q)

        # Find the corresponding bit combination
        for key, value in qam_map.items():
            if value == (I, Q):
                bits.extend(key)
                break
        else:
            print(f"Unmatched I/Q pair: ({I}, {Q})")

    return bits

def clean_signal(value):
    """
    Rounds the given value to the closest value in {±7, ±5, ±3, ±1}.
    """
    value=value*2
    #print(value)
    targets = [-15, -13, -11, -9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 11, 13, 15]
    return min(targets, key=lambda x: abs(value - x))

def plot_wav(file_path):
    """
    Reads a .wav file and plots its waveform.
    """
    signal, sample_rate = sf.read(file_path)
    time = np.linspace(0, len(signal) / sample_rate, len(signal), endpoint=False)

    plt.figure(figsize=(10, 6))
    plt.plot(time, signal, label="QAM Signal", color="blue", linewidth=1)
    plt.title("Waveform of QAM Signal")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()


def sendMessage(message):
    """
    Sends a .wav message to the QAM receiver by autoplaying the file and saving it.
    Includes a 2-second high-pitch tone at the beginning and another different high-pitch tone at the end.
    """

    fs = 48000
    duration = 1

    #TODO: Use FFT to find start- and end-freq to clip .wav for demodulation!!
    freq_start = 2000
    freq_end = 3000
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    start_tone = 0.5 * np.sin(2 * np.pi * freq_start * t)
    end_tone = 0.5 * np.sin(2 * np.pi * freq_end * t)


    bits = string_to_bits(message)
    qam_signal = modulate(bits)


    full_signal = np.concatenate((start_tone, qam_signal, end_tone))

    audio_file = "outgoing.wav"
    sf.write(audio_file, full_signal, fs)
    plot_wav(audio_file)


    print(f"Playing {audio_file}...")
    data, samplerate = sf.read(audio_file)
    sd.play(data, samplerate)
    sd.wait()

def main():
    """
    Main function to test 256-QAM modulation and demodulation.
    """
    input_string = "Hello World!"
    print(f"Input string: {input_string}")
    bits = string_to_bits(input_string)
    print(f"Bits: {bits}")

    qam_signal = modulate(bits)
    audio_file = "qam_signal_256qam.wav"
    sf.write(audio_file, qam_signal, fs)
    print(f"QAM signal saved to {audio_file}")

    received_signal, _ = sf.read(audio_file)
    demodulated_bits = demodulate(received_signal)
    print(f"Demodulated bits: {demodulated_bits}")
    output_string = bits_to_string(demodulated_bits)
    print(f"Demodulated string: {output_string}")
    plot_wav(audio_file)


if __name__ == "__main__":
    main()


