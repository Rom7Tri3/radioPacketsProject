import modulation as m
import audio_helper as h
import matplotlib.pyplot as plt
import soundfile as sf

def plot_wav(file_path):
    # Read the audio data from the .wav file
    audio_data, sample_rate = sf.read(file_path)

    # Create a time axis for the audio data
    time = [i / sample_rate for i in range(len(audio_data))]

    # Plot the waveform
    plt.figure(figsize=(10, 4))
    plt.plot(time, audio_data, label='Audio Waveform')
    plt.title('Waveform of ' + file_path)
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()

# Example usage:
# plot_wav('output.wav')


def string_to_bits(s):
    # Convert each character to its 8-bit binary representation
    return [bit for c in s for bit in bin(ord(c))[2:].zfill(8)]

def bits_to_string(bits):
    # Ensure bits are in groups of 8
    return ''.join(chr(int(''.join(map(str, bits[i:i + 8])), 2)) for i in range(0, len(bits), 8))

def main():
    # Test string
    s = input("Send Message:")

    # Convert string to bits
    bits = string_to_bits(s)
    print("String to bits:", bits)

    # Modulate
    symbols = m.modulate(bits)  # BPSK modulation
    signal = m.generate_waveform(symbols)  # Generate audio waveform
    m.save_wav('output.wav', signal)  # Save to .wav file
    plot_wav('output.wav')

    # Prep audio
    h.add_markers('output.wav', 'output_m.wav')
    plot_wav('output_m.wav')

    # TODO: Play audio file

    # Unprep audio
    h.remove_markers('output_m.wav', 'received.wav')
    plot_wav('received.wav')

    # Demodulate
    audio_signal, _ = sf.read('received.wav')
    demodulated_bits = m.demodulate(audio_signal)
    print("Demodulated bits:", demodulated_bits)
    bits = demodulated_bits

    # Convert bits back to string
    reconstructed_string = bits_to_string(bits)
    print("Bits to string:", reconstructed_string)  # 'Hello'

if __name__ == "__main__":
    main()
