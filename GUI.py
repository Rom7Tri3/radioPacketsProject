import tkinter as tk
from tkinter import messagebox
import sounddevice as sd
import soundfile as sf
import numpy as np
import modulation
import demodulation
import audio_helper as ah
import threading
import os
import main

SAMPLE_RATE = 44100
DURATION = 5  # Recording duration in seconds


def send_data():
    text = text_input.get()
    if not text:
        messagebox.showwarning("Warning", "Please enter text to send.")
        return

    bits = main.to_bits(text)
    modulation.modulate(bits, filename="output.wav", baud=50, sample_rate=SAMPLE_RATE)
    if not os.path.exists("output.wav"):
        messagebox.showerror("Error", "Failed to create output.wav")
        return

    ah.add_tone_preamble("output.wav", "with_preamble.wav")
    ah.play_wav("with_preamble.wav")
    messagebox.showinfo("Info", "Transmission completed.")


def record_and_receive():
    messagebox.showinfo("Info", "Recording started...")
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    sf.write("received.wav", recording, SAMPLE_RATE)

    ah.remove_tone_preamble("received.wav", "cleaned.wav")
    decoded_bits = demodulation.demodulate("cleaned.wav", baud=50, sample_rate=SAMPLE_RATE)

    if decoded_bits:
        decoded_text = modulation.bits_to_string(decoded_bits)
        messagebox.showinfo("Received Data", f"Decoded: {decoded_text}")
    else:
        messagebox.showerror("Error", "No valid data received.")


def start_receiving():
    threading.Thread(target=record_and_receive, daemon=True).start()


# GUI Setup
root = tk.Tk()
root.title("QAM Communication")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

text_label = tk.Label(frame, text="Enter text to send:")
text_label.pack()

text_input = tk.Entry(frame, width=40)
text_input.pack()

send_button = tk.Button(frame, text="Send", command=send_data)
send_button.pack(pady=10)

receive_button = tk.Button(frame, text="Receive", command=start_receiving)
receive_button.pack()

root.mainloop()
