import tkinter as tk
from tkinter import scrolledtext
import threading
import FEC
import modulation
import demodulation
import audio_helper as ah
import numpy as np
import os
import reedsolo
import sounddevice as sd
import wave
import sys


class GUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QAM Audio Transmission")
        self.root.configure(bg="#1E1E1E")  # Dark background

        # Styling
        label_font = ("Arial", 12, "bold")
        button_font = ("Arial", 10, "bold")
        text_font = ("Segoe UI Emoji", 10)  # Updated for emoji support

        # Text Input
        self.input_label = tk.Label(root, text="Enter Text:", font=label_font, fg="white", bg="#1E1E1E")
        self.input_label.pack(pady=5)

        self.input_text = tk.Entry(root, width=50, font=text_font, bg="#2D2D2D", fg="white", relief="flat")
        self.input_text.pack(pady=5, ipady=5)

        self.send_button = tk.Button(root, text="Send", font=button_font, bg="#007ACC", fg="white", relief="flat",
                                     command=self.send_text)
        self.send_button.pack(pady=5, ipadx=10, ipady=5)

        # Record Button
        self.record_button = tk.Button(root, text="Start Recording", font=button_font, bg="#E74C3C", fg="white", relief="flat",
                                       command=self.toggle_recording)
        self.record_button.pack(pady=5, ipadx=10, ipady=5)
        self.is_recording = False
        self.audio_stream = None
        self.audio_frames = []

        # Scrolling Text Output
        self.output_text = scrolledtext.ScrolledText(root, width=80, height=20, font=text_font, bg="#2D2D2D",
                                                     fg="white", relief="flat")
        self.output_text.pack(pady=10)

        # Redirect stdout to GUI
        sys.stdout = self

    def write(self, text):
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def flush(self):
        pass

    def send_text(self):
        threading.Thread(target=self.process_text).start()

    def process_text(self):
        input_string = self.input_text.get()
        print(f"✍️ User input: {input_string}")

        encoded_data = FEC.encode_reed_solomon("BEGIN: " + input_string)
        if not isinstance(encoded_data, bytes):
            encoded_data = bytes(encoded_data)

        bits = self.to_bits(encoded_data.decode("latin-1", errors="ignore"))
        print(f"📏 Encoded Data Length: {len(bits)} bits")

        modulation.modulate(bits, "output.wav")
        if not os.path.exists("output.wav"):
            print("🚨 The file 'output.wav' was not created. Check modulation module.")
            return

        ah.add_tone_preamble("output.wav", "with_preamble.wav")
        ah.play_wav("with_preamble.wav")

    def toggle_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.record_button.config(text="Start Recording", bg="#E74C3C")
            self.stop_recording()
        else:
            self.is_recording = True
            self.record_button.config(text="Stop Recording", bg="#27AE60")
            threading.Thread(target=self.start_recording).start()

    def start_recording(self):
        self.audio_frames = []
        samplerate = 48000
        channels = 1
        print("🎙️ Recording started...")

        def callback(indata, frames, time, status):
            if status:
                print(status)
            self.audio_frames.append(indata.copy())

        self.audio_stream = sd.InputStream(samplerate=samplerate, channels=channels, dtype='int16', callback=callback)
        self.audio_stream.start()

    def stop_recording(self):
        if self.audio_stream is not None:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None
            print("💾 Recording stopped. Saving file...")

            filename = "recorded.wav"
            samplerate = 48000
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                wf.writeframes(b"".join(frame.tobytes() for frame in self.audio_frames))

            print(f"💾 Saved recording as {filename}")
            self.process_received_audio(filename)

    def process_received_audio(self, filename):
        ah.clean_data(filename, "cleaned.wav")
        decoded_bits = demodulation.demodulate("cleaned.wav")
        flipped_bits = self.flip_bits(decoded_bits)

        received_text = self.bits_to_string(decoded_bits).replace("BEGIN: ", "").strip()
        flipped_text = self.bits_to_string(flipped_bits).replace("BEGIN: ", "").strip()

        print(f"📜 Decoded Text: {received_text}")
        print(f"🔀 Flipped Decoded Text: {flipped_text}")
        print(f"📊 Bit Error Rate: {self.calculate_ber(decoded_bits)}")

        decoded_bytes = self.binary_array_to_bytes(decoded_bits)
        flipped_bytes = self.binary_array_to_bytes(flipped_bits)

        try:
            print("✅ Decoded (FEC):", FEC.decode_reed_solomon(decoded_bytes))
        except reedsolo.ReedSolomonError:
            print("❌ FEC Decoding failed for received data.")

        try:
            print("✅ Flipped Decoded (FEC):", FEC.decode_reed_solomon(flipped_bytes))
        except reedsolo.ReedSolomonError:
            print("❌ FEC Decoding failed for flipped data.")

    @staticmethod
    def to_bits(text):
        return [int(bit) for char in text for bit in format(ord(char), '08b')]

    @staticmethod
    def flip_bits(bits):
        return [1 - bit for bit in bits]

    @staticmethod
    def bits_to_string(bits):
        return "".join(chr(int("".join(map(str, bits[i:i + 8])), 2)) for i in range(0, len(bits), 8))

    @staticmethod
    def calculate_ber(decoded_bits):
        return sum(b != 0 for b in decoded_bits) / len(decoded_bits) if decoded_bits else 0


if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()
