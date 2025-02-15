import numpy as np
import scipy.io.wavfile as wav
from scipy.signal import correlate
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
import wave
import scipy.signal as signal
from scipy.fft import fft, fftfreq

def plot_wav(file_path):
    # Read the .wav file
    with wave.open(file_path, 'rb') as wav_file:
        n_channels = wav_file.getnchannels()
        n_frames = wav_file.getnframes()
        framerate = wav_file.getframerate()

        # Read audio data and convert to numpy array
        audio_data = np.frombuffer(wav_file.readframes(n_frames), dtype=np.int16)

        if n_channels > 1:
            # Use only one channel if stereo
            audio_data = audio_data[::n_channels]

    # Create time axis for the x-axis (in seconds)
    time = np.linspace(0, n_frames / framerate, num=n_frames)

    # Plot the waveform
    plt.figure(figsize=(10, 4))
    plt.plot(time, audio_data)
    plt.title("Waveform of " + file_path)
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()

def play_wav(filename):
    """
    Plays a .wav file using the sounddevice library.

    :param filename: Path to the .wav file
    """
    try:
        data, samplerate = sf.read(filename)
        sd.play(data, samplerate)
        sd.wait()  # Wait until playback finishes
        print(f"✅ Finished playing: {filename}")
    except Exception as e:
        print(f"⚠️ Error playing {filename}: {e}")


def add_tone_preamble(input_wav, output_wav, tone_freq=1000, duration=1.0, amplitude=0.5):
    """
    Adds a 1-second sine wave tone at the beginning and end of a .wav file.

    :param input_wav: Path to the input .wav file.
    :param output_wav: Path to save the new .wav file with preamble.
    :param tone_freq: Frequency of the tone in Hz (default: 1000 Hz).
    :param duration: Duration of the tone in seconds (default: 1 second).
    :param amplitude: Amplitude of the tone (default: 0.5 to prevent clipping).
    """
    # Read the original WAV file
    sample_rate, audio_data = wav.read(input_wav)

    # Generate 1-second sine wave tone
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = amplitude * np.sin(2 * np.pi * tone_freq * t)

    # Convert tone to match the audio data type
    if audio_data.dtype == np.int16:
        tone = (tone * np.iinfo(np.int16).max).astype(np.int16)
    elif audio_data.dtype == np.float32:
        tone = tone.astype(np.float32)

    # Handle stereo audio
    if audio_data.ndim > 1:
        tone = np.column_stack([tone, tone])  # Duplicate for stereo

    # Concatenate tone with original audio at the beginning and end
    new_audio = np.concatenate((tone, audio_data, tone), axis=0)

    # Save the new WAV file
    wav.write(output_wav, sample_rate, new_audio)
    print(f"Saved {output_wav} with tone preamble at both ends.")


def remove_tone_preamble(wav_file, target_freq=1000, sampling_rate=48000, threshold=0.5, window_size=1024):
    # Ensure target_freq is a float (in case it was passed as a string or something else)
    target_freq = float(target_freq)

    # Load the audio file
    signal, rate = sf.read(wav_file)

    if rate != sampling_rate:
        raise ValueError(f"Sampling rate of file ({rate} Hz) does not match expected ({sampling_rate} Hz)")

    # Ensure the signal is mono (one channel)
    if signal.ndim > 1:
        signal = signal[:, 0]  # Taking the first channel if stereo

    # Initialize variables
    tone_start, tone_end = None, None
    signal_length = len(signal)

    # Loop through the signal in chunks (windows) for FFT analysis
    for i in range(0, signal_length - window_size, window_size):
        # Extract the current window of audio
        window_signal = signal[i:i + window_size]

        # Perform FFT to get frequency spectrum
        fft_result = fft(window_signal)
        freqs = fftfreq(window_size, 1 / sampling_rate)

        # Only consider positive frequencies
        freqs = freqs[:window_size // 2]
        fft_result = fft_result[:window_size // 2]

        # Find the index of the target frequency (1000 Hz)
        target_index = np.argmin(np.abs(freqs - target_freq))

        # Find the magnitude of the FFT at the target frequency
        magnitude = np.abs(fft_result[target_index])

        # Check if the magnitude exceeds the threshold (indicating the tone is present)
        if magnitude > threshold:
            # If tone_start is not set, this is the start of the tone
            if tone_start is None:
                tone_start = i / sampling_rate

            # Update tone_end as the current point in time
            tone_end = (i + window_size) / sampling_rate

    print(tone_start, " ", tone_end)

    return tone_start, tone_end

def trim_wav(input_wav, output_wav, t_1, t_2, sampling_rate=48000):
    """
    Trims the audio of a .wav file between t_1+1 and t_2-1 seconds.

    :param input_wav: Path to the input .wav file.
    :param output_wav: Path to save the trimmed .wav file.
    :param t_1: The start time (in seconds).
    :param t_2: The end time (in seconds).
    :param sampling_rate: Sampling rate of the .wav file (default 48000).
    """
    # Read the original WAV file
    signal, rate = sf.read(input_wav)

    if rate != sampling_rate:
        raise ValueError(f"Sampling rate of file ({rate} Hz) does not match expected ({sampling_rate} Hz)")

    # Calculate sample indices corresponding to t_1+1 and t_2-1
    start_sample = int((t_1 + 1) * sampling_rate)
    end_sample = int((t_2 - 1) * sampling_rate)

    # Ensure that the start and end samples are within bounds
    if start_sample < 0 or end_sample > len(signal):
        raise ValueError("t_1 and t_2 are out of the range of the audio file")

    # Trim the signal
    trimmed_signal = signal[start_sample:end_sample]

    # Save the trimmed WAV file
    sf.write(output_wav, trimmed_signal, rate)
    print(f"✅ Saved trimmed file as {output_wav}")

def clean_data(input, output):
    start, end = remove_tone_preamble(input)
    trim_wav(input, output, start, end, 48000)
    #normalize_audio(output)
    #plot_wav(output)
    #plot_wav('normalized_audio.wav')


def normalize_audio(filename):
    data, samplerate = sf.read(filename)
    peak = np.max(np.abs(data))
    normalization_factor = 1.0 / peak if peak > 0 else 1
    normalized_data = data * normalization_factor
    sf.write('normalized_audio.wav', normalized_data, samplerate)

#clean_data('Noise.wav', 'no_preamble.wav')




#plot_wav('with_preamble.wav')
#plot_wav('cleaned.wav')
#plot_wav('no_preamble.wav')

