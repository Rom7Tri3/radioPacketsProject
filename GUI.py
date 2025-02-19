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
        self.root.configure(bg="#2C3E50")

        # Styling
        label_font = ("Arial", 12, "bold")
        button_font = ("Arial", 10, "bold")
        text_font = ("Courier", 10)

        # Text Input
        self.input_label = tk.Label(root, text="Enter Text:", font=label_font, fg="white", bg="#2C3E50")
        self.input_label.pack(pady=5)

        self.input_text = tk.Entry(root, width=50, font=text_font, bg="#ECF0F1", fg="#2C3E50")
        self.input_text.pack(pady=5)

        self.send_button = tk.Button(root, text="Send", font=button_font, bg="#3498DB", fg="white",
                                     command=self.send_text)
        self.send_button.pack(pady=5)

        # Record Button
        self.record_button = tk.Button(root, text="Start Recording", font=button_font, bg="#E74C3C", fg="white",
                                       command=self.toggle_recording)
        self.record_button.pack(pady=5)
        self.is_recording = False

        # Scrolling Text Output
        self.output_text = scrolledtext.ScrolledText(root, width=80, height=20, font=text_font, bg="#ECF0F1",
                                                     fg="#2C3E50")
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
        else:
            self.is_recording = True
            self.record_button.config(text="Stop Recording", bg="#27AE60")
            threading.Thread(target=self.record_audio).start()

    def record_audio(self):
        filename = "recorded.wav"
        duration = 5
        samplerate = 44100
        print(f"🎙️ Recording for {duration} seconds...")
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
        sd.wait()

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(samplerate)
            wf.writeframes(audio_data.tobytes())

        print(f"💾 Saved recording as {filename}")

    @staticmethod
    def to_bits(text):
        return [int(bit) for char in text for bit in format(ord(char), '08b')]


if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()
