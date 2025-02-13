import numpy as np
import soundfile as sf

def add_markers(input_file, output_file, tone_freq_start=500, tone_freq_end=1000, tone_duration=0.5, sampling_rate=48000):
    # Read the original audio file
    audio_data, _ = sf.read(input_file)

    # Create the tone at the beginning (500 Hz)
    t_start = np.linspace(0, tone_duration, int(sampling_rate * tone_duration), endpoint=False)
    tone_start = np.sin(2 * np.pi * tone_freq_start * t_start)

    # Create the tone at the end (1000 Hz)
    t_end = np.linspace(0, tone_duration, int(sampling_rate * tone_duration), endpoint=False)
    tone_end = np.sin(2 * np.pi * tone_freq_end * t_end)

    # Concatenate the tones with the original audio
    modified_audio = np.concatenate([tone_start, audio_data, tone_end])

    # Save the modified audio to a new file
    sf.write(output_file, modified_audio, sampling_rate)

# Example usage:
# add_markers('output.wav', 'outgoing.wav')



def remove_markers(input_file, output_file, tone_freq_start=500, tone_freq_end=1000, tone_duration=0.5,
                   sampling_rate=48000):
    # Read the original audio file
    audio_data, _ = sf.read(input_file)

    # Perform FFT to convert the audio data to the frequency domain
    fft_data = np.fft.fft(audio_data)
    fft_freqs = np.fft.fftfreq(len(fft_data), d=1 / sampling_rate)

    # Identify the indices corresponding to the start and end marker frequencies
    start_freq_idx = np.argmin(np.abs(fft_freqs - tone_freq_start))
    end_freq_idx = np.argmin(np.abs(fft_freqs - tone_freq_end))

    # Set a frequency range around the marker frequencies to capture the marker peaks
    start_marker_range = np.where(np.abs(fft_freqs - tone_freq_start) < 50)[0]  # Tolerance of 50 Hz
    end_marker_range = np.where(np.abs(fft_freqs - tone_freq_end) < 50)[0]  # Tolerance of 50 Hz

    # Detect the time domain indices that correspond to the start and end markers
    start_marker_position = np.argmax(np.abs(fft_data[start_marker_range]))
    end_marker_position = np.argmax(np.abs(fft_data[end_marker_range]))

    # Convert the frequency domain positions back to the time domain
    start_marker_time = int(start_marker_position * len(audio_data) / len(fft_data))
    end_marker_time = int(end_marker_position * len(audio_data) / len(fft_data))

    # Trim the audio to remove the markers (i.e., slice out the marker portions)
    trimmed_audio_data = audio_data[start_marker_time + int(sampling_rate * tone_duration):-end_marker_time - int(sampling_rate * tone_duration)]

    # Save the trimmed audio to a new file
    sf.write(output_file, trimmed_audio_data, sampling_rate)

# Example usage:
# remove_markers('outgoing.wav', 'received.wav')


# Example usage:
# remove_markers('outgoing.wav', 'received.wav')
