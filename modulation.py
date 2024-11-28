import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from itertools import product
try:
    import sounddevice as sd
except:
    print("No Auto-play available")


# Parameters
fs = 48000
bit_duration = 0.1
carrier_freq = 300
amplitude = 0.05

qam_map = {}
values = [-15, -13, -11, -9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 11, 13, 15]
possible_tuples = list(product(values, repeat=2))
for i in range(256):
    bits = f"{i:08b}"
    bit_tuple = tuple(map(int, bits))
    qam_map[bit_tuple] = possible_tuples[i]


def string_to_bits(input_string):
    return [int(bit) for char in input_string for bit in f"{ord(char):08b}"]


def bits_to_string(bits):
    chars = [chr(int("".join(map(str, bits[i:i + 8])), 2)) for i in range(0, len(bits), 8)]
    return "".join(chars)


def modulate(bits):
    if len(bits) % 8 != 0:
        bits.extend([0] * (8 - len(bits) % 8))

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
    num_samples = int(fs * bit_duration)
    num_symbols = len(signal) // num_samples
    bits = []

    for i in range(num_symbols):
        chunk = signal[i * num_samples:(i + 1) * num_samples]
        t = np.linspace(0, bit_duration, num_samples, endpoint=False)
        ref_I = np.cos(2 * np.pi * carrier_freq * t)
        ref_Q = np.sin(2 * np.pi * carrier_freq * t)
        I = np.sum(chunk * ref_I) / (amplitude * num_samples)
        Q = np.sum(chunk * ref_Q) / (amplitude * num_samples)
        I = clean_signal(I)
        Q = clean_signal(Q)

        for key, value in qam_map.items():
            if value == (I, Q):
                bits.extend(key)
                break
        else:
            print(f"Unmatched I/Q pair: ({I}, {Q})")

    return bits


def clean_signal(value):
    value *= 2
    targets = [-15, -13, -11, -9, -7, -5, -3, -1, 1, 3, 5, 7, 9, 11, 13, 15]
    return min(targets, key=lambda x: abs(value - x))


def plot_wav(file_path):
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
    duration = 0.1
    freq_start = 2000
    freq_end = 3000

    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    start_tone = np.sin(2 * np.pi * freq_start * t)
    end_tone = np.sin(2 * np.pi * freq_end * t)

    bits = string_to_bits(message)
    qam_signal = modulate(bits)

    full_signal = np.concatenate((start_tone, qam_signal, end_tone))

    audio_file = "outgoing.wav"
    sf.write(audio_file, full_signal, fs)
    plot_wav(audio_file)

    print(f"Playing {audio_file}...")
    data, samplerate = sf.read(audio_file)
    try:
        sd.play(data, samplerate)
        sd.wait()
    except:
        print("¯\_(ツ)_/¯")
    print(f"Saved as {audio_file}")

def recieveMessage(audio_file):
    extracted_file = extract_audio_between_frequencies(audio_file, "extracted.wav")
    if extracted_file is None:
        print("Failed to extract and process the message.")
        return

    extracted_signal, _ = sf.read(extracted_file)
    demodulated_bits = demodulate(extracted_signal)
    output_string = bits_to_string(demodulated_bits)
    print(f"Demodulated string: {output_string}")

def extract_audio_between_frequencies(input_filename, output_filename):
    freq_end = 3000
    freq_start = 2000
    chunk_duration = 0.1
    tolerance = 10

    data, rate = sf.read(input_filename)
    if data.ndim > 1:
        data = data[:, 0]

    chunk_size = int(chunk_duration * rate)
    num_chunks = len(data) // chunk_size

    def find_chunk_with_frequency(target_freq):
        for i in range(num_chunks):
            chunk = data[i * chunk_size:(i + 1) * chunk_size]
            freqs = np.fft.fftfreq(chunk_size, 1 / rate)
            spectrum = np.abs(np.fft.fft(chunk))
            dominant_freq = freqs[np.argmax(spectrum[:chunk_size // 2])]
            if abs(dominant_freq - target_freq) < tolerance:
                return i * chunk_size
        return -1

    start_index = find_chunk_with_frequency(freq_start)
    end_index = find_chunk_with_frequency(freq_end)

    if start_index == -1 or end_index == -1 or start_index >= end_index:
        print("Failed to extract audio between frequencies.")
        return None  # Return None if extraction fails

    segment = data[start_index:end_index]
    sf.write(output_filename, segment, rate)
    print(f"Extracted audio saved to {output_filename}")
    plot_wav(output_filename)
    return output_filename



def main():
    input_string = "Hello World!"
    print(f"Input string: {input_string}")
    sendMessage(input_string)
    recieveMessage("outgoing.wav")
    plot_wav("outgoing.wav")


if __name__ == "__main__":
    main()
