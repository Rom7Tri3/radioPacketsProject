import numpy as np
import scipy.io.wavfile as wav
from scipy.signal import correlate
import sounddevice as sd
import soundfile as sf


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
    Adds a 1-second sine wave tone at the beginning of a .wav file.

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

    # Concatenate tone with original audio
    new_audio = np.concatenate((tone, audio_data), axis=0)

    # Save the new WAV file
    wav.write(output_wav, sample_rate, new_audio)
    print(f"Saved {output_wav} with tone preamble.")


def remove_tone_preamble(input_wav, output_wav, tone_freq=1000, duration=1.0, amplitude=0.5):
    """
    Detects and removes a 1-second sine wave tone from a .wav file with higher accuracy.

    :param input_wav: Path to the input .wav file with the preamble.
    :param output_wav: Path to save the cleaned .wav file.
    :param tone_freq: Frequency of the preamble tone in Hz (default: 1000 Hz).
    :param duration: Duration of the tone in seconds (default: 1 second).
    :param amplitude: Amplitude of the tone (default: 0.5).
    :return: NumPy array of the cleaned audio.
    """
    # Read the WAV file
    sample_rate, audio_data = wav.read(input_wav)

    # Generate the expected tone
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = amplitude * np.sin(2 * np.pi * tone_freq * t)

    # Convert tone to match the audio data type
    if audio_data.dtype == np.int16:
        tone = (tone * np.iinfo(np.int16).max).astype(np.int16)
    elif audio_data.dtype == np.float32:
        tone = tone.astype(np.float32)

    # Handle stereo audio
    if audio_data.ndim > 1:
        audio_mono = np.mean(audio_data, axis=1)  # Convert stereo to mono for detection
    else:
        audio_mono = audio_data

    # Normalize both signals
    audio_mono = audio_mono / np.max(np.abs(audio_mono))
    tone = tone / np.max(np.abs(tone))

    # Compute cross-correlation
    correlation = correlate(audio_mono, tone, mode="valid")
    correlation = np.abs(correlation)  # Ensure positive values only

    # Find the strongest match
    preamble_start = np.argmax(correlation)

    # Confirm if it's a valid detection
    expected_start = int(0.1 * sample_rate)  # Expected within first 100ms
    if preamble_start > expected_start:
        print("⚠️ Warning: Preamble not detected at the beginning. Check the signal.")

    # Remove detected preamble
    cleaned_audio = audio_data[preamble_start + len(tone):]

    # Save the cleaned WAV file
    wav.write(output_wav, sample_rate, cleaned_audio)
    print(f"✅ Saved {output_wav} without tone preamble.")

    return cleaned_audio