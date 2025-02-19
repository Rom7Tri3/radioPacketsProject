import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
import wave
from scipy.fft import fft, fftfreq


def plot_wav(file_path):
    """Plots the waveform of a .wav file."""
    with wave.open(file_path, 'rb') as wav_file:
        n_channels = wav_file.getnchannels()
        n_frames = wav_file.getnframes()
        framerate = wav_file.getframerate()
        audio_data = np.frombuffer(wav_file.readframes(n_frames), dtype=np.int16)
        if n_channels > 1:
            audio_data = audio_data[::n_channels]
    time = np.linspace(0, n_frames / framerate, num=n_frames)
    plt.figure(figsize=(10, 4))
    plt.plot(time, audio_data)
    plt.title(f"Waveform of {file_path}")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.show()


def play_wav(filename):
    """Plays a .wav file."""
    try:
        data, samplerate = sf.read(filename)
        sd.play(data, samplerate)
        sd.wait()
        print(f"✅ Finished playing: {filename}")
    except Exception as e:
        print(f"⚠️ Error playing {filename}: {e}")


def add_tone_preamble(input_wav, output_wav, tone_freq=1000, duration=1.0, amplitude=0.5):
    """Adds a sine wave tone at the beginning and end of a .wav file."""
    sample_rate, audio_data = wav.read(input_wav)
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = amplitude * np.sin(2 * np.pi * tone_freq * t)
    if audio_data.dtype == np.int16:
        tone = (tone * np.iinfo(np.int16).max).astype(np.int16)
    elif audio_data.dtype == np.float32:
        tone = tone.astype(np.float32)
    if audio_data.ndim > 1:
        tone = np.column_stack([tone, tone])
    new_audio = np.concatenate((tone, audio_data, tone), axis=0)
    wav.write(output_wav, sample_rate, new_audio)
    print(f"Saved {output_wav} with tone preamble.")


def remove_tone_preamble(wav_file, target_freq=1000, sampling_rate=48000, threshold=0.5, window_size=1024):
    """Detects and removes a tone preamble from a .wav file."""
    signal, rate = sf.read(wav_file)
    if rate != sampling_rate:
        raise ValueError(f"Sampling rate mismatch: {rate} Hz vs {sampling_rate} Hz")
    if signal.ndim > 1:
        signal = signal[:, 0]
    tone_start, tone_end = None, None
    for i in range(0, len(signal) - window_size, window_size):
        window_signal = signal[i:i + window_size]
        fft_result = fft(window_signal)[:window_size // 2]
        freqs = fftfreq(window_size, 1 / sampling_rate)[:window_size // 2]
        target_index = np.argmin(np.abs(freqs - target_freq))
        if np.abs(fft_result[target_index]) > threshold:
            if tone_start is None:
                tone_start = i / sampling_rate
            tone_end = (i + window_size) / sampling_rate

    if tone_start is None or tone_end is None:
        print("⚠️ No preamble found, are you sure there is a message to be heard?")
        return 0, len(signal) / sampling_rate

    print(f"✅Tone detected from {tone_start} to {tone_end} seconds.")
    return tone_start, tone_end


def trim_wav(input_wav, output_wav, t_1, t_2, sampling_rate=48000):
    """Trims a .wav file between t_1+1 and t_2-1 seconds."""
    signal, rate = sf.read(input_wav)
    if rate != sampling_rate:
        raise ValueError(f"Sampling rate mismatch: {rate} Hz vs {sampling_rate} Hz")
    start_sample, end_sample = int((t_1 + 1) * sampling_rate), int((t_2 - 1) * sampling_rate)
    if start_sample < 0 or end_sample > len(signal):
        raise ValueError("t_1 and t_2 out of range")
    sf.write(output_wav, signal[start_sample:end_sample], rate)
    print(f"✅ Trimmed file saved as {output_wav}")


def clean_data(input_wav, output_wav):
    """Removes tone preamble and trims audio."""
    start, end = remove_tone_preamble(input_wav)
    trim_wav(input_wav, output_wav, start, end, 48000)


def normalize_audio(filename):
    """Normalizes the amplitude of a .wav file."""
    data, samplerate = sf.read(filename)
    peak = np.max(np.abs(data))
    normalized_data = data / peak if peak > 0 else data
    sf.write('normalized_audio.wav', normalized_data, samplerate)
