import numpy as np
from scipy.io.wavfile import write, read
import matplotlib.pyplot as plt  # Optional: For debugging or visualization


class QAMAudioModulator:
    """
    A 4-QAM (2-bit per symbol) modulator and demodulator with configurable carrier frequency and amplitude.
    """

    def __init__(self, sample_rate=48000, carrier_freq=1000, amplitude=1.0):
        """
        Initialize the modulator with sample rate, carrier frequency, and amplitude.

        Parameters:
            sample_rate (int): Audio sample rate.
            carrier_freq (float): Carrier frequency for modulation in Hz.
            amplitude (float): Amplitude of the carrier wave.
        """
        self.constellation = {
            '00': -1 - 1j,
            '01': -1 + 1j,
            '10': 1 - 1j,
            '11': 1 + 1j
        }
        self.inverse_constellation = {v: k for k, v in self.constellation.items()}
        self.sample_rate = sample_rate
        self.carrier_freq = carrier_freq
        self.amplitude = amplitude

    def _string_to_bits(self, input_string):
        """Convert an input string to a binary string."""
        return ''.join(f'{ord(c):08b}' for c in input_string)

    def _bits_to_string(self, binary_data):
        """Convert a binary string back to an ASCII string."""
        chars = [chr(int(binary_data[i:i + 8], 2)) for i in range(0, len(binary_data), 8)]
        return ''.join(chars)

    def modulate(self, input_string, output_file="qam_output.wav"):
        """
        Modulate an input string into a 4-QAM signal with a carrier wave and save it to a .wav file.

        Parameters:
            input_string (str): The input text to modulate.
            output_file (str): Path to the output .wav file.
        """
        binary_data = self._string_to_bits(input_string)

        # Pad binary data to be divisible by 2
        if len(binary_data) % 2 != 0:
            binary_data += '0'

        # Split into bit pairs and map to QAM symbols
        bit_pairs = [binary_data[i:i + 2] for i in range(0, len(binary_data), 2)]
        symbols = np.array([self.constellation[pair] for pair in bit_pairs])

        # Time vector for one symbol duration
        symbol_duration = 1 / (self.carrier_freq / 10)  # 10 carrier cycles per symbol
        t = np.linspace(0, symbol_duration, int(self.sample_rate * symbol_duration), endpoint=False)

        # Modulate real and imaginary parts separately
        signal = []
        for symbol in symbols:
            real_wave = np.real(symbol) * np.cos(2 * np.pi * self.carrier_freq * t)
            imag_wave = np.imag(symbol) * np.sin(2 * np.pi * self.carrier_freq * t)
            modulated_wave = self.amplitude * (real_wave + imag_wave)
            signal.append(modulated_wave)

        # Combine all symbol waves into one continuous signal
        full_signal = np.concatenate(signal)

        # Normalize to avoid clipping
        full_signal = full_signal / np.max(np.abs(full_signal))

        # Save as mono WAV file
        write(output_file, self.sample_rate, (full_signal * 32767).astype(np.int16))
        print(f"Signal written to '{output_file}'")

    def demodulate(self, input_file):
        """
        Read a .wav file, demodulate the 4-QAM signal, and reconstruct the original string.

        Parameters:
            input_file (str): Path to the input .wav file.

        Returns:
            str: The reconstructed input string.
        """
        # Read the WAV file
        sample_rate, signal = read(input_file)
        signal = signal / 32767  # Normalize back to -1 to 1

        # Time vector for symbol duration
        symbol_duration = 1 / (self.carrier_freq / 10)
        samples_per_symbol = int(sample_rate * symbol_duration)

        # Demodulate symbol by symbol
        bit_pairs = []
        for i in range(0, len(signal), samples_per_symbol):
            symbol_wave = signal[i:i + samples_per_symbol]
            if len(symbol_wave) < samples_per_symbol:
                break

            # Correlate with carrier waves
            t = np.linspace(0, symbol_duration, len(symbol_wave), endpoint=False)
            real_part = 2 * np.sum(symbol_wave * np.cos(2 * np.pi * self.carrier_freq * t)) / len(t)
            imag_part = 2 * np.sum(symbol_wave * np.sin(2 * np.pi * self.carrier_freq * t)) / len(t)

            # Find closest constellation point
            received_symbol = real_part + 1j * imag_part
            closest_symbol = min(self.inverse_constellation,
                                 key=lambda x: abs(received_symbol - x))
            bit_pairs.append(self.inverse_constellation[closest_symbol])

        # Combine bit pairs
        binary_data = ''.join(bit_pairs)

        # Trim to nearest byte
        binary_data = binary_data[:len(binary_data) - len(binary_data) % 8]

        # Convert binary data to string
        return self._bits_to_string(binary_data)


# Example usage
if __name__ == "__main__":
    modulator = QAMAudioModulator(sample_rate=48000, carrier_freq=1000, amplitude=1.0)

    # Input text to modulate
    input_text = "Hello QAM"
    output_wav = "qam_output_with_carrier.wav"

    # Modulate and save to .wav file
    print(f"Modulating text: {input_text}")
    modulator.modulate(input_text, output_wav)

    # Plot the waveform (optional)
    print("\nPlotting waveform...")
    def plot_wav(file_path):
        sample_rate, data = read(file_path)
        time = np.linspace(0, len(data) / sample_rate, num=len(data))
        plt.plot(time, data)
        plt.title("Waveform of .wav File")
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude")
        plt.grid()
        plt.show()
    plot_wav(output_wav)

    # Demodulate from .wav file
    print("\nDemodulating...")
    reconstructed_text = modulator.demodulate(output_wav)
    print(f"Reconstructed Text: {reconstructed_text}")
