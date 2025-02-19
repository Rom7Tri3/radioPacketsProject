import FEC
import modulation
import demodulation
import audio_helper as ah
import numpy as np
import os
import reedsolo
import sounddevice as sd
import wave

# 🎤 Records audio and saves it as a .wav file
def record_audio(filename, duration=5, samplerate=44100):
    print(f"🎙️ Recording for {duration} seconds...")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()

    # Save recorded data as a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())

    print(f"💾 Saved recording as {filename}")
# 🎯 Converts a string to a list of bits
def to_bits(text):
    return [int(bit) for char in text for bit in format(ord(char), '08b')]


# 🔄 Converts a list of bits back to a string
def bits_to_string(bits):
    return "".join(chr(int("".join(map(str, bits[i:i + 8])), 2)) for i in range(0, len(bits), 8))


# 📉 Calculates the Bit Error Rate (BER)
def calculate_ber(original_bits, decoded_bits):
    min_length = min(len(original_bits), len(decoded_bits))
    errors = sum(o != d for o, d in zip(original_bits[:min_length], decoded_bits[:min_length]))
    return errors / min_length if min_length > 0 else 0


# 🔢 Converts a binary array into bytes
def binary_array_to_bytes(binary_array):
    if len(binary_array) % 8 != 0:
        binary_array.extend([0] * (8 - len(binary_array) % 8))
    return bytes(int("".join(map(str, binary_array[i:i + 8])), 2) for i in range(0, len(binary_array), 8))


# 🔄 Flips all bits in an array (0 → 1, 1 → 0)
def flip_bits(bits):
    return [1 - bit for bit in bits]


if __name__ == "__main__":
    input_string = input("✍️ User input: ")
    encoded_data = FEC.encode_reed_solomon("BEGIN: " + input_string)

    if not isinstance(encoded_data, bytes):
        encoded_data = bytes(encoded_data)

    bits = to_bits(encoded_data.decode("latin-1", errors="ignore"))
    print(f"📏 Encoded Data Length: {len(bits)} bits")

    # 🎵 Modulate the bits into a .wav file
    modulation.modulate(bits, "output.wav")
    if not os.path.exists("output.wav"):
        raise FileNotFoundError("🚨 The file 'output.wav' was not created. Check modulation module.")

    # 🔊 Add a preamble and play the sound
    ah.add_tone_preamble("output.wav", "with_preamble.wav")
    ah.play_wav("with_preamble.wav")

    # 🧹 Clean the received noisy signal
    ah.clean_data("noise.wav", "cleaned.wav")

    # 📡 Demodulate the received signal
    decoded_bits = demodulation.demodulate("cleaned.wav")
    flipped_bits = flip_bits(decoded_bits)

    # 📜 Convert decoded bits to a readable string
    received_text = bits_to_string(decoded_bits).replace("BEGIN: ", "").strip()
    flipped_text = bits_to_string(flipped_bits).replace("BEGIN: ", "").strip()

    print(f"📜 Decoded Text: {received_text}")
    print(f"🔀 Flipped Decoded Text: {flipped_text}")
    print(f"📊 Bit Error Rate: {calculate_ber(bits, decoded_bits):.6f}")

    # 🔄 Convert decoded bits to bytes
    decoded_bytes = binary_array_to_bytes(decoded_bits)
    flipped_bytes = binary_array_to_bytes(flipped_bits)

    try:
        print("✅ Decoded (FEC):", FEC.decode_reed_solomon(decoded_bytes))
    except reedsolo.ReedSolomonError:
        print("❌ FEC Decoding failed for received data.")

    try:
        print("✅ Flipped Decoded (FEC):", FEC.decode_reed_solomon(flipped_bytes))
    except reedsolo.ReedSolomonError:
        print("❌ FEC Decoding failed for flipped data.")


"""
Notes:

Not perfect yet, too much noise from different sources. Ie Microphone, speaker noise, general noise. QAM not suited for audio.

Higher QAM modes lead to more errors, 256 was completely unusable. Higher baud rate also leads to more errors, since detecting signal gets more difficult on shorter symbols.

"BEGIN: " is buffer since most errors appear at the beginning or end (no clue why) So we added the word to catch most errors.

Not very efficient for data transmission over sound, but kinda stable
"""